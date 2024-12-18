import pygame
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
player_width, player_height = 60, 60
player_x, player_y = width // 2 - player_width // 2, height - player_height - 10
player_speed = 8
lives = 3  # Player starts with 3 lives

# Define obstacle attributes
obstacle_width, obstacle_height = 45, 45
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
    if obstacle_count % 30 == 0:  # Every 30 obstacles, create a coin
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
            # lives += 1  # Gain an extra life
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
            lives += 1  # Gain an extra life
            score += 20  # Gain score for collecting a life power-up
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


#-----------starts design part--------------

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



def game_loop():
    global player_x, player_y, lives, coin, life_power_up, score, obstacle_speed, min_obstacle_gap, obstacle_spawn_rate
    
    # Create initial obstacles
    create_obstacle()
    
    running = True
    game_over = False
    
    while running:
        # Set FPS (frames per second)
        clock.tick(60)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cap.release()
                pygame.quit()
            elif not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        shoot_bullet()
            else:  # Game Over event handling
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart game
                        game_over = False
                        running = True
                        lives = 3
                        score = 0
                        obstacle_speed = 5
                        obstacle_spawn_rate = 3
                        min_obstacle_gap = 60
                        obstacles.clear()
                        create_obstacle()
                    elif event.key == pygame.K_q:  # Quit game
                        running = False
                        cap.release()
                        pygame.quit()
                        
        
        if not game_over:
            # Move player based on user input (left , right , up , down)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < width - player_width:
                player_x += player_speed
            # Vertical movement
            if keys[pygame.K_UP] and player_y > 0:
                player_y -= player_speed
            if keys[pygame.K_DOWN] and player_y < height - player_height: 
                player_y += player_speed
            
            # Move obstacles, bullets, coin, and power-up
            move_obstacles()
            move_bullets()
            coin = move_coin()
            life_power_up = move_life_power_up()
            
            # Check collisions and collections
            if check_collision():
                lives -= 1  # Decrease life on collision
                if lives <= 0:
                    # running = False  # End the game if no lives are left
                    game_over = True
                else:
                    obstacles.clear()  # Clear obstacles after collision for a fresh start
            
            check_coin_collection()
            check_life_power_up_collection()
            
            # Periodically create new obstacles based on the increased difficulty
            if random.randint(1, 100) < obstacle_spawn_rate:
                create_obstacle()
            
            # Read the next frame from the video
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video when it ends
                continue

            # Convert the frame to a Pygame surface
            video_surface = pygame.surfarray.make_surface(frame)

            # Draw the frame and game elements
            draw(video_surface)

        # Handle Game Over
        if game_over:
            draw_game_over()
    
    # pygame.quit()

# Run the game loop
game_loop() 