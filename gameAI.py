import pygame
import heapq
import random
import cv2
from os.path import join
# Initialize Pygame
pygame.init()
# Game settings
width, height = 800, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Fighter Game")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 105, 180)

# Define player attributes
player_width, player_height = 50, 50
player_x, player_y = width // 2 - player_width // 2, height - player_height - 10
player_speed = 8
lives = 3  # Player starts with 3 lives

# Define obstacle attributes
obstacle_width, obstacle_height = 40, 40
obstacle_speed = 5  
obstacles = []
obstacle_count = 0  # Track how many obstacles have been created
obstacle_spawn_rate = 3  # Initial rate of obstacle appearance (1 out of 100 chance per frame)
min_obstacle_gap = 60  # Minimum gap to avoid overlapping obstacles

# Define bullet attributes
bullet_width, bullet_height = 8, 20  
bullet_speed = 10
bullets = []  # Store active bullets

# Define coin attributes
coin_width, coin_height = 40, 40
coin = None  # Initially, no coin exists

# Define life power-up attributes
life_width, life_height = 40, 40
life_power_up = None  # Initially, no life power-up exists

"""extra for movement"""
target_x, target_y = player_x, player_y  # Initialize target position
movement_delay = 5  # Frames between movements
movement_counter = 0
smooth_speed = 5  # Pixels per frame for smooth movement

# Define the clock
clock = pygame.time.Clock()

# Font for displaying lives, score, and other info
font = pygame.font.SysFont(None, 36)

# Score variable
score = 0

def is_overlapping(x1, y1, w1, h1, x2, y2, w2, h2):
    """Check if two rectangles are overlapping"""
    return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

def create_obstacle():
    """Create a new obstacle at a random x position, avoiding overlap with existing obstacles and power-ups"""
    global obstacle_count
    max_attempts = 20  # Limit the number of attempts to find a non-overlapping position
    for _ in range(max_attempts):
        x_pos = random.randint(0, width - obstacle_width)
        y_pos = -obstacle_height
        
        # Check for overlap with existing obstacles, coin, and life power-up
        overlap = False
        for obstacle in obstacles:
            if is_overlapping(x_pos, y_pos, obstacle_width, obstacle_height,
                              obstacle[0], obstacle[1], obstacle_width, obstacle_height):
                overlap = True
                break
        
        if coin and is_overlapping(x_pos, y_pos, obstacle_width, obstacle_height,
                                   coin[0], coin[1], coin_width, coin_height):
            overlap = True

        if life_power_up and is_overlapping(x_pos, y_pos, obstacle_width, obstacle_height,
                                            life_power_up[0], life_power_up[1], life_width, life_height):
            overlap = True
        
        if not overlap:
            obstacles.append([x_pos, y_pos])
            break
    
    # Increment obstacle count and check if a coin or life power-up should appear
    obstacle_count += 1
    if obstacle_count % 20 == 0:  # Every 30 obstacles, create a coin
        create_coin()
    if obstacle_count % 50 == 0:  # Every 50 obstacles, create a life power-up
        create_life_power_up()

def move_obstacles():
    """Move obstacles down the screen"""
    global score
    for obstacle in obstacles:
        obstacle[1] += obstacle_speed
        if obstacle[1] >= height:  # If obstacle goes off-screen, increase score
            score += 1
    # Remove obstacles that have passed off the screen
    obstacles[:] = [obstacle for obstacle in obstacles if obstacle[1] < height]

def create_coin():
    """Create a coin at a random position at the top of the screen, avoiding overlap with obstacles"""
    global coin
    max_attempts = 20  # Limit the number of attempts to find a non-overlapping position
    for _ in range(max_attempts):
        x_pos = random.randint(0, width - coin_width)
        y_pos = -coin_height
        
        # Check for overlap with existing obstacles
        overlap = False
        for obstacle in obstacles:
            if is_overlapping(x_pos, y_pos, coin_width, coin_height,
                              obstacle[0], obstacle[1], obstacle_width, obstacle_height):
                overlap = True
                break
        
        if not overlap:
            coin = [x_pos, y_pos]
            break

def move_coin():
    """Move the coin down the screen"""
    if coin:
        coin[1] += obstacle_speed
        # Remove the coin if it goes off the screen
        if coin[1] >= height:
            return None
    return coin

def create_life_power_up():
    """Create a life power-up at a random position at the top of the screen, avoiding overlap"""
    global life_power_up
    max_attempts = 20  # Limit the number of attempts to find a non-overlapping position
    for _ in range(max_attempts):
        x_pos = random.randint(0, width - life_width)
        y_pos = -life_height
        
        # Check for overlap with existing obstacles and coin
        overlap = False
        for obstacle in obstacles:
            if is_overlapping(x_pos, y_pos, life_width, life_height,
                              obstacle[0], obstacle[1], obstacle_width, obstacle_height):
                overlap = True
                break
        
        if coin and is_overlapping(x_pos, y_pos, life_width, life_height,
                                   coin[0], coin[1], coin_width, coin_height):
            overlap = True

        if not overlap:
            life_power_up = [x_pos, y_pos]
            break

def move_life_power_up():
    """Move the life power-up down the screen"""
    if life_power_up:
        life_power_up[1] += obstacle_speed
        # Remove the life power-up if it goes off the screen
        if life_power_up[1] >= height:
            return None
    return life_power_up

def check_collision():
    """Check for collision between player and any obstacles"""
    global player_x, player_y, lives
    for obstacle in obstacles:
        if (player_x + player_width > obstacle[0] and player_x < obstacle[0] + obstacle_width and
            player_y + player_height > obstacle[1] and player_y < obstacle[1] + obstacle_height):
            return True
    return False

def check_coin_collection():
    """Check if the player collects the coin"""
    global player_x, player_y, coin, lives, obstacle_spawn_rate, obstacle_speed, score
    if coin:
        if (player_x + player_width > coin[0] and player_x < coin[0] + coin_width and
            player_y + player_height > coin[1] and player_y < coin[1] + coin_height):
            # if lives < 10:
            #     lives += 1  # Gain an extra life
            score += 10  # Gain score for collecting a coin
            coin = None  # Remove the coin after collection
            
            # Increase the difficulty by increasing the obstacle spawn rate and speed
            if obstacle_spawn_rate < 10:  # Limit the maximum spawn rate
                obstacle_spawn_rate += 1
                obstacle_speed += 1  # Increase obstacle speed each time difficulty level increases

def check_life_power_up_collection():
    """Check if the player collects the life power-up"""
    global player_x, player_y, life_power_up, lives, score
    if life_power_up:
        if (player_x + player_width > life_power_up[0] and player_x < life_power_up[0] + life_width and
            player_y + player_height > life_power_up[1] and player_y < life_power_up[1] + life_height):
            if lives < 10:
                lives += 1  # Gain an extra life
            # score += 20  # Gain score for collecting a life power-up
            life_power_up = None  # Remove the life power-up after collection

def shoot_bullet():
    """Create a new bullet at the player's position"""
    bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])

def move_bullets():
    """Move bullets up the screen and check for collisions with obstacles"""
    global score
    for bullet in bullets:
        bullet[1] -= bullet_speed
        # Check collision with obstacles
        for obstacle in obstacles:
            if (bullet[0] + bullet_width > obstacle[0] and bullet[0] < obstacle[0] + obstacle_width and
                bullet[1] < obstacle[1] + obstacle_height and bullet[1] + bullet_height > obstacle[1]):
                obstacles.remove(obstacle)  # Remove the obstacle
                bullets.remove(bullet)  # Remove the bullet
                score += 5  # Gain score for destroying an obstacle
                break
    # Remove bullets that have gone off the screen
    bullets[:] = [bullet for bullet in bullets if bullet[1] > 0]


#-------------starts graphic part--------------

# OpenCV Video Capture
video_path = "Assets\display5.mp4"  # Replace with your video file
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Load images 
background_image = pygame.image.load("Assets\display3.jpg").convert_alpha()
background_image2 = pygame.image.load("Assets\display7.jpg").convert_alpha()
player_image = pygame.image.load("Assets\player2.png").convert_alpha()
obstacle_image = pygame.image.load("Assets\enemy2.png").convert_alpha()
# bullet_image = pygame.image.load("Assets\bullet.png").convert_alpha()
coin_image = pygame.image.load("Assets\coin1.png").convert_alpha()
life_power_up_image = pygame.image.load("Assets\life2.png").convert_alpha()

# Scale images to match the dimensions used in the original drawing
background_image = pygame.transform.scale(background_image, (width, height))
background_image2 = pygame.transform.scale(background_image2, (width, height))
player_image = pygame.transform.scale(player_image, (player_width, player_height))
obstacle_image = pygame.transform.scale(obstacle_image, (obstacle_width, obstacle_height))
# bullet_image = pygame.transform.scale(bullet_image, (bullet_width, bullet_height))
coin_image = pygame.transform.scale(coin_image, (coin_width, coin_height))
life_power_up_image = pygame.transform.scale(life_power_up_image, (life_width, life_height))
fps = 30

def draw(video_frame):
    """Draw all game elements on the screen with images"""
    # screen.fill(BLACK)
    # screen.blit(background_image, (0, 0))
    screen.blit(pygame.transform.rotate(video_frame, -90), (0, 0))
    # screen.blit(pygame.transform.scale(video_frame, (width, height)),(0, 0))
    
    # Draw player image
    screen.blit(player_image, (player_x, player_y))
    
    # Draw obstacle images
    for obstacle in obstacles:
        screen.blit(obstacle_image, (obstacle[0], obstacle[1]))
    
    # Draw bullet images
    # for bullet in bullets: 
    #     screen.blit(bullet_image, (bullet[0], bullet[1]))
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], bullet_width, bullet_height))
    
    # Draw coin image if it exists 
    if coin:
        screen.blit(coin_image, (coin[0], coin[1]))
    
    # Draw life power-up image if it exists
    if life_power_up:
        screen.blit(life_power_up_image, (life_power_up[0], life_power_up[1]))
    
    # Display lives and score
    lives_text = font.render(f'Lives: {lives}', True, WHITE)
    screen.blit(lives_text, (10, 10))
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 50))
    
    pygame.display.flip()

def draw_game_over():
    """Display Game Over screen with the final score."""
    # screen.fill((0, 0, 0))  # Clear the screen with black
    screen.blit(background_image2, (0, 0))
    game_over_text = font.render("GAME OVER", True, YELLOW)
    score_text = font.render(f"Score: {score}", True, GREEN)
    restart_text = font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    
    # Center the text on the screen
    screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 100))
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2))
    screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height // 2 + 50))
    
    pygame.display.flip()


# -----------------------A* Algorithm Implementation-----------------------------

def a_star(start, target, obstacles, grid_size):
    """A* pathfinding algorithm."""
    rows, cols = grid_size
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, target)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == target:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, rows, cols):
            if neighbor in obstacles:
                continue

            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, target)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found

def heuristic(pos, target):
    """Manhattan distance heuristic."""
    return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

def get_neighbors(pos, rows, cols):
    """Get all possible neighbors for a given position."""
    x, y = pos
    neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < cols and 0 <= ny < rows]

def reconstruct_path(came_from, current):
    """Reconstruct the path from start to target."""
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    return path[::-1]

def predict_obstacle_positions(obstacles, speed, grid_size, steps=3):
    """Predict future positions of obstacles based on their speed and direction."""
    future_positions = set(obstacles)  # Start with current positions
    rows, cols = grid_size

    for _ in range(steps):  # Predict for the next few steps
        new_positions = set()
        for x, y in future_positions:
            y += speed  # Move obstacle down
            if 0 <= y < rows:  # Ensure within bounds
                new_positions.add((x, y))
        future_positions.update(new_positions)

    return future_positions

def avoid_obstacles(player_pos, obstacles, grid_size):
    """Basic obstacle avoidance mechanism."""
    rows, cols = grid_size
    x, y = player_pos

    # Check nearby obstacles
    dangerous_positions = {(ox, oy) for ox, oy in obstacles if abs(oy - y) <= 2 and abs(ox - x) <= 1}

    # Decide the safest move
    possible_moves = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    safe_moves = [move for move in possible_moves if move not in dangerous_positions and 0 <= move[0] < cols and 0 <= move[1] < rows]

    if safe_moves:
        # Prioritize moves that stay in the center of the screen
        return min(safe_moves, key=lambda pos: abs(pos[0] - cols // 2))
    return player_pos  # Stay in place if no safe moves

def handle_potential_collisions(player_x, player_y, obstacles, player_width, bullet_ready=True):
    """Check for obstacles that may collide with the spaceship and fire bullets if needed."""
    for obstacle in obstacles:
        obstacle_x, obstacle_y = obstacle
        # Check if the obstacle is within the collision path
        if abs(obstacle_y - player_y) < height // 4:  # Vertical proximity
            if abs(obstacle_x - player_x) < player_width:  # Horizontally aligned
                # Fire bullet if aligned
                if bullet_ready:
                    shoot_bullet()
                return player_x, player_y
            
            # Align horizontally if not already aligned
            if obstacle_x > player_x:
                player_x += player_speed
            elif obstacle_x < player_x:
                player_x -= player_speed
            return player_x, player_y

    return player_x, player_y  # No immediate threat


def ai_control_with_dynamic_replanning(player_pos, coin_pos, life_pos, obstacles, grid_size, return_to_base=False):
    """AI control with dynamic replanning to avoid moving obstacles."""
    target = None
    
    if return_to_base:  # If returning to base
        target = (player_pos[0], grid_size[0] - 1)  # Closest point on the bottom row
    elif life_pos:
        target = life_pos  # Prioritize life power-up
    elif coin_pos:
        target = coin_pos  # Go for coin if no life power-up

    # Pathfinding logic
    if target:
        future_obstacles = predict_obstacle_positions(obstacles, speed=1, grid_size=grid_size)
        path = a_star(player_pos, target, future_obstacles, grid_size)
        if path and len(path) > 1:
            return path[1]  # Take the next step towards the target

    # Default movement mechanism: Avoid obstacles
    next_move = avoid_obstacles(player_pos, obstacles, grid_size)

    # Shoot bullets if obstacles are directly ahead
    rows, cols = grid_size
    px, py = player_pos
    for ox, oy in obstacles:
        if oy > py and abs(ox - px) <= 50:  # Obstacle directly in front
            shoot_bullet()  # Call the bullet-shooting function
            break

    return next_move



#------------main function--------------

def game_loop():
    global player_x, player_y, lives, coin, life_power_up, score, obstacle_speed, min_obstacle_gap, obstacle_spawn_rate

    create_obstacle()
    return_to_base = False  # Track return-to-base mode
    running = True
    game_over = False

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cap.release()
                pygame.quit()

        if not game_over:
            # Move obstacles
            move_obstacles()

            # Check if coin or life power-up is collected
            if check_coin_collection():
                return_to_base = True  # Trigger return-to-base mode
            if check_life_power_up_collection():
                return_to_base = True  # Trigger return-to-base mode

            # Handle return-to-base or AI-controlled movement
            if return_to_base:
                # Move the spaceship downward with the same speed as the obstacles
                player_y += obstacle_speed

                # Check if the spaceship has reached the base
                if player_y >= height - player_height:
                    return_to_base = False  # Reset return-to-base mode
            else:
                # Regular AI control for moving towards coin or life power-up
                grid_size = (40, 40)  # Define the grid size (e.g., 40x40)
                player_pos = (player_x // (width // grid_size[1]), player_y // (height // grid_size[0]))
                coin_pos = (coin[0] // (width // grid_size[1]), coin[1] // (height // grid_size[0])) if coin else None
                life_pos = (life_power_up[0] // (width // grid_size[1]), life_power_up[1] // (height // grid_size[0])) if life_power_up else None
                obstacles_grid = [(ob[0] // (width // grid_size[1]), ob[1] // (height // grid_size[0])) for ob in obstacles]

                # Get the next move from AI control
                next_move = ai_control_with_dynamic_replanning(player_pos, coin_pos, life_pos, obstacles_grid, grid_size)

                # Smoothly move towards the target
                dx = (next_move[0] * (width // grid_size[1]) - player_x) / smooth_speed
                dy = (next_move[1] * (height // grid_size[0]) - player_y) / smooth_speed
                player_x += dx
                player_y += dy

            # Move other elements
            move_bullets()
            coin = move_coin()
            life_power_up = move_life_power_up()

            # Check collisions
            if check_collision():
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    obstacles.clear()

            if random.randint(1, 100) < obstacle_spawn_rate:
                create_obstacle()

            # Draw everything
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            video_surface = pygame.surfarray.make_surface(frame)
            draw(video_surface)

        if game_over:
            draw_game_over()

    pygame.quit()



# Run the game loop
game_loop() 
