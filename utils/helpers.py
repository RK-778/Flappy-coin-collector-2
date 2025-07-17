import pygame
import random

PIPE_GAP = 150  # Vertical gap between the top and bottom pipes

def generate_pipe(pipe_image, screen_width):
    """
    Generate a new pair of pipes (upper and lower) at the right edge of the screen.
    """
    gap_y = random.randint(100, 400)
    
    top_pipe = {
        "x": screen_width,
        "y": gap_y - pipe_image.get_height(),
        "image": pygame.transform.flip(pipe_image, False, True)  # Flip pipe to face downward
    }
    
    bottom_pipe = {
        "x": screen_width,
        "y": gap_y + PIPE_GAP,
        "image": pipe_image
    }
    
    return {"top": top_pipe, "bottom": bottom_pipe}

def check_collisions(bird, bird_y, pipes):
    """
    Check for collisions between the bird and any of the pipes.
    """
    bird_rect = bird.get_rect(topleft=(50, bird_y))
    
    for pipe_pair in pipes:
        top_pipe_rect = pipe_pair["top"]["image"].get_rect(topleft=(pipe_pair["top"]["x"], pipe_pair["top"]["y"]))
        bottom_pipe_rect = pipe_pair["bottom"]["image"].get_rect(topleft=(pipe_pair["bottom"]["x"], pipe_pair["bottom"]["y"]))
        
        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
            return True
    
    if bird_y < 0 or bird_y > 600:
        return True
    
    return False

def load_high_score(file_path):
    """
    Load the high score from a file.
    """
    try:
        with open(file_path, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score, file_path):
    """
    Save the high score to a file.
    """
    with open(file_path, "w") as f:
        f.write(str(score))
