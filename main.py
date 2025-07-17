import pygame
import sys
import random
import sqlite3
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.display.set_icon(pygame.image.load("C:/Users/ragha/OneDrive/Desktop/RK_flappy/rk/assets/images/bluebird power.png"))
font = pygame.font.Font(None, 22)
title_font = pygame.font.Font(None, 32)

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAVITY = 0.5
BASE_PIPE_GAP = 160
ANIMATION_SPEED = 2
BASE_SPEED = 4
SPEED_INCREMENT = 0.5
SCORE_THRESHOLD = 110
POWER_DISPLAY_X = SCREEN_WIDTH - 120
POWER_DISPLAY_Y = 15
BLUEBIRD_DISPLAY_Y = 50
INVISIBLE_DURATION = 7000
BLUEBIRD_DURATION = 7000
FPS = 60
POWER_ICON_SIZE = 50
POWER_ICON_X = SCREEN_WIDTH - 100
POWER_ICON_Y = 15
POWER_ICON_SPACING = 60
TIMER_OFFSET_X = 60
POWER_SPAWN_INTERVAL = 15000  # 15 seconds between spawn attempts
MIN_PIPE_DISTANCE = 250  # Minimum distance from pipes

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Coin Collector")

# Database Manager
class DatabaseManager:
    def __init__(self, db_name="game_scores.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                score INTEGER,
                coins_collected INTEGER,
                difficulty INTEGER
            )
        ''')
        self.conn.commit()
        
    def save_score(self, score, coins, difficulty=1):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO game_scores (score, coins_collected, difficulty)
            VALUES (?, ?, ?)
        ''', (score, coins, difficulty))
        self.conn.commit()
        
    def close(self):
        self.conn.close()

# Initialize database
db = DatabaseManager()

def load_image(path, default_size=(50, 50)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, default_size)
    except Exception as e:
        print(f"Failed to load image {path}: {e}")
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255), 200)
        surf.fill(color)
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
        return surf

# Game assets
background = load_image("assets/images/flapybirdbackground.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
title_image = load_image("assets/images/main title.png", (365, 58))
game_over_image = load_image("assets/images/gameover2.png", (300, 70))
game_over_icon = load_image("assets/images/RK.png", (40, 35))
bird_frames = [
    load_image("assets/images/bird.png", (50, 35)),
    load_image("assets/images/bird2.png", (50, 35)),
    load_image("assets/images/bird3.png", (50, 35))
]
inv_bird_frames = [
    load_image("assets/images/inv-bird1.png", (50, 35)),
    load_image("assets/images/inv-bird2.png", (50, 35)),
    load_image("assets/images/inv-bird3.png", (50, 35))
]
pipe_image = load_image("assets/images/pipe.png", (120, 550))
coin_image = load_image("assets/images/coin.png", (40, 40))
power_image = inv_bird_frames[0]
bluebird_power_image = load_image("assets/images/bluebird power.png", (50, 50))
restart_image = load_image("assets/images/restart.png", (100, 50))

# Initialize game objects
title_rect = title_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
restart_rect = restart_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
bird_index = 0
bird_icon = bird_frames[0]

# Load number images
numbers = {}
for i in range(10):
    try:
        numbers[i] = pygame.transform.scale(pygame.image.load(f"assets/images/{i}.png"), (25, 35))
    except:
        surf = pygame.Surface((25, 35))
        surf.fill(BLACK)
        text = font.render(str(i), True, WHITE)
        surf.blit(text, (5, 5))
        numbers[i] = surf

# Initialize sounds
try:
    pygame.mixer.init()
    bg_music = pygame.mixer.Sound("C:/Users/ragha/OneDrive/Desktop/RK_flappy/rk/assets/sounds/bg_music.mp3")
    coin_sound = pygame.mixer.Sound("C:/Users/ragha/OneDrive/Desktop/RK_flappy/rk/assets/sounds/coin.wav")
    jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
    game_over_sound = pygame.mixer.Sound("assets/sounds/game_over.wav")
    bg_music.play(-1)
except Exception as e:
    print(f"Failed to load sounds: {e}")
    class DummySound:
        def play(self): pass
    bg_music = coin_sound = jump_sound = game_over_sound = power_sound = DummySound()

# Game state
clock = pygame.time.Clock()
bird_animation_timer = 0
bird_animation_interval = 50
bird_y = SCREEN_HEIGHT // 2
bird_velocity = 0
score = 0
coins_collected = 0
game_active = False
show_home_screen = True
pipes = []
current_difficulty = 1
pipe_gap = BASE_PIPE_GAP
pipe_speed = BASE_SPEED
is_invisible = False
invisible_timer = 0
current_power = None
bluebird_power = None
is_bluebird_active = False
bluebird_timer = 0
cheat_mode = False
last_power_spawn_time = 0
power_spawn_cooldown = POWER_SPAWN_INTERVAL
ICON_WIDTH = 50
NUMBER_WIDTH = 25
ICON_NUMBER_SPACING = 10

def reset_game():
    global bird_y, bird_velocity, score, coins_collected, pipes, game_active
    global current_difficulty, pipe_gap, pipe_speed
    global is_invisible, invisible_timer, current_power, bluebird_power
    global is_bluebird_active, bluebird_timer, last_power_spawn_time
    
    bird_y = SCREEN_HEIGHT // 2
    bird_velocity = 0
    score = 0
    coins_collected = 0
    pipes = []
    game_active = True
    current_difficulty = 1
    pipe_gap = BASE_PIPE_GAP
    pipe_speed = BASE_SPEED
    is_invisible = False
    invisible_timer = 0
    current_power = None
    bluebird_power = None
    is_bluebird_active = False
    bluebird_timer = 0
    last_power_spawn_time = 0

def check_collisions(bird_rect):
    if bird_rect.top <= 0 or bird_rect.bottom >= SCREEN_HEIGHT:
        return True
    
    if not is_invisible:
        for pipe in pipes:
            if bird_rect.colliderect(pipe["top"]) or bird_rect.colliderect(pipe["bottom"]):
                return True
    return False

def generate_pipes():
    pipe_height = random.randint(100, 400)
    return {
        "top": pipe_image.get_rect(midbottom=(SCREEN_WIDTH + 100, pipe_height - pipe_gap // 2)),
        "bottom": pipe_image.get_rect(midtop=(SCREEN_WIDTH + 100, pipe_height + pipe_gap // 2)),
        "coin": coin_image.get_rect(center=(SCREEN_WIDTH + 100, pipe_height)),
        "collected": False
    }

def is_position_valid(new_rect):
    """Check if a position is valid (not overlapping pipes or coins)"""
    for pipe in pipes:
        if new_rect.colliderect(pipe["top"]) or new_rect.colliderect(pipe["bottom"]):
            return False
        if not pipe["collected"] and new_rect.colliderect(pipe["coin"]):
            return False
    return True

def generate_power():
    """Generate a power-up in a valid position"""
    attempts = 0
    while attempts < 20:
        x_pos = SCREEN_WIDTH + random.randint(100, 300)
        y_pos = random.randint(100, SCREEN_HEIGHT - 100)
        new_rect = power_image.get_rect(center=(x_pos, y_pos))
        
        if is_position_valid(new_rect):
            return {
                "rect": new_rect,
                "active": True,
                "frame": 0
            }
        attempts += 1
    return None

def generate_bluebird_power():
    """Generate a bluebird power-up in a valid position"""
    attempts = 0
    while attempts < 20:
        x_pos = SCREEN_WIDTH + random.randint(100, 300)
        y_pos = random.randint(100, SCREEN_HEIGHT - 100)
        new_rect = bluebird_power_image.get_rect(center=(x_pos, y_pos))
        
        if is_position_valid(new_rect):
            return {
                "rect": new_rect,
                "active": True
            }
        attempts += 1
    return None

def draw_numbers(value, x, y):
    for i, digit in enumerate(str(value)):
        screen.blit(numbers[int(digit)], (x + i * 25, y))

# Main game loop
try:
    running = True
    while running:
        screen.blit(background, (0, 0))
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and show_home_screen:
                    show_home_screen = False
                    reset_game()
                elif event.key == pygame.K_SPACE and game_active:
                    bird_velocity = -8
                    jump_sound.play()
                elif event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT and event.key == pygame.K_SPACE:
                    cheat_mode = not cheat_mode
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_active and not show_home_screen and restart_rect.collidepoint(event.pos):
                reset_game()

        if show_home_screen:
            screen.blit(title_image, title_rect)
        elif game_active:
            # Game logic
            bird_velocity += GRAVITY
            bird_y += bird_velocity
            bird_rect = bird_frames[bird_index].get_rect(center=(100, bird_y))
            
            # Animation
            bird_animation_timer += clock.get_time()
            if bird_animation_timer >= bird_animation_interval:
                bird_index = (bird_index + 1) % len(bird_frames)
                bird_animation_timer = 0
            
            # Generate pipes
            if len(pipes) == 0 or pipes[-1]["top"].right < SCREEN_WIDTH - 200:
                pipes.append(generate_pipes())
            
            # Move pipes and check coin collection
            for pipe in pipes:
                pipe["top"].x -= pipe_speed
                pipe["bottom"].x -= pipe_speed
                pipe["coin"].x -= pipe_speed
                
                if not pipe["collected"] and bird_rect.colliderect(pipe["coin"]):
                    pipe["collected"] = True
                    coins_collected += 1
                    score += 5
                    coin_sound.play()
            
            # Remove off-screen pipes
            if pipes and pipes[0]["top"].right < 0:
                pipes.pop(0)
            
            # Progressive difficulty
            if score >= current_difficulty * SCORE_THRESHOLD:
                current_difficulty += 1
                if not is_bluebird_active:
                    pipe_speed = BASE_SPEED + (current_difficulty - 1) * SPEED_INCREMENT
            
            # Power-up spawning (only one at a time)
            if current_time - last_power_spawn_time > power_spawn_cooldown:
                power_choice = random.random()
                
                if power_choice < 0.5 and current_power is None and not is_invisible:
                    current_power = generate_power()
                    if current_power:
                        last_power_spawn_time = current_time
                        power_spawn_cooldown = random.randint(15000, 25000)
                elif bluebird_power is None and not is_bluebird_active:
                    bluebird_power = generate_bluebird_power()
                    if bluebird_power:
                        last_power_spawn_time = current_time
                        power_spawn_cooldown = random.randint(15000, 25000)
            
            # Handle bluebird power
            if bluebird_power and bluebird_power["active"]:
                bluebird_power["rect"].x -= pipe_speed
                screen.blit(bluebird_power_image, bluebird_power["rect"])
                
                if bird_rect.colliderect(bluebird_power["rect"]):
                    is_bluebird_active = True
                    bluebird_timer = pygame.time.get_ticks()
                    bluebird_power["active"] = False
                    bluebird_power = None
                    pipe_speed = BASE_SPEED + 6
            
            # Bluebird power effect
            if is_bluebird_active:
                if pygame.time.get_ticks() - bluebird_timer > BLUEBIRD_DURATION:
                    is_bluebird_active = False
                    pipe_speed = BASE_SPEED + (current_difficulty - 1) * SPEED_INCREMENT
            
            # Handle regular power
            if current_power and current_power["active"]:
                current_power["rect"].x -= pipe_speed
                current_power["frame"] = (pygame.time.get_ticks() // 100) % len(inv_bird_frames)
                screen.blit(inv_bird_frames[current_power["frame"]], current_power["rect"])
                
                if bird_rect.colliderect(current_power["rect"]):
                    is_invisible = True
                    invisible_timer = pygame.time.get_ticks()
                    current_power["active"] = False
                    current_power = None
                
                if current_power and current_power["rect"].right < 0:
                    current_power = None
            
            # Invisibility effect
            if is_invisible:
                if pygame.time.get_ticks() - invisible_timer > INVISIBLE_DURATION:
                    is_invisible = False
            
            # Draw pipes
            for pipe in pipes:
                screen.blit(pygame.transform.flip(pipe_image, False, True), pipe["top"])
                screen.blit(pipe_image, pipe["bottom"])
                if not pipe["collected"]:
                    screen.blit(coin_image, pipe["coin"])
            
            # Draw bird
            if is_invisible:
                inv_frame_index = (pygame.time.get_ticks() // 100) % len(inv_bird_frames)
                screen.blit(inv_bird_frames[inv_frame_index], bird_rect)
            else:
                screen.blit(bird_frames[bird_index], bird_rect)
            
            # Check collisions
            if not (cheat_mode or is_bluebird_active) and check_collisions(bird_rect):
                db.save_score(score, coins_collected, current_difficulty)
                game_active = False
                game_over_sound.play()
            
            # Score increases over time
            score += 0.05
            
            # Draw UI
            screen.blit(bird_icon, (15, 15))
            draw_numbers(int(score), 70, 15)
            
            screen.blit(coin_image, (15, 60))
            draw_numbers(coins_collected, 70, 60)
            
            # Power-up timers
            if is_bluebird_active:
                elapsed = (pygame.time.get_ticks() - bluebird_timer) // 1000
                remaining = max(0, BLUEBIRD_DURATION//1000 - elapsed)
                screen.blit(bluebird_power_image, (POWER_ICON_X, POWER_ICON_Y))
                draw_numbers(remaining, POWER_ICON_X + TIMER_OFFSET_X, POWER_ICON_Y)

            if is_invisible:
                elapsed = (pygame.time.get_ticks() - invisible_timer) // 1000
                remaining = max(0, INVISIBLE_DURATION//1000 - elapsed)
                screen.blit(power_image, (POWER_ICON_X, POWER_ICON_Y + POWER_ICON_SPACING))
                draw_numbers(remaining, POWER_ICON_X + TIMER_OFFSET_X, POWER_ICON_Y + POWER_ICON_SPACING)

        elif not show_home_screen:  # Game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0)) 

            game_over_x = SCREEN_WIDTH // 2 - 150
            game_over_y = 80
            
            screen.blit(game_over_image, (SCREEN_WIDTH // 2 - 150, 80))

            icon_x = SCREEN_WIDTH - game_over_icon.get_width() - 10
            icon_y = SCREEN_HEIGHT - game_over_icon.get_height() - 10
            screen.blit(game_over_icon, (icon_x, icon_y))
            
            # Draw score
            score_value = int(score)
            score_digits = len(str(score_value))
            score_total_width = ICON_WIDTH + ICON_NUMBER_SPACING + (NUMBER_WIDTH * score_digits)
            score_x = (SCREEN_WIDTH - score_total_width) // 2

            screen.blit(bird_icon, (score_x, 180))
            draw_numbers(score_value, score_x + ICON_WIDTH + ICON_NUMBER_SPACING, 185)

            # Draw coins in center
            coin_digits = len(str(coins_collected))
            coin_total_width = ICON_WIDTH + ICON_NUMBER_SPACING + (NUMBER_WIDTH * coin_digits)
            coin_x = (SCREEN_WIDTH - coin_total_width) // 2

            screen.blit(coin_image, (coin_x, 230))
            draw_numbers(coins_collected, coin_x + ICON_WIDTH + ICON_NUMBER_SPACING, 235)
            
            screen.blit(restart_image, restart_rect)
        
        pygame.display.update()
        clock.tick(FPS)

except Exception as e:
    print(f"Game crashed with error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
    pygame.quit()
    sys.exit()