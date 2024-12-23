import pygame
import json
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 320, 240
PIXEL_SIZE = 10  # Scale factor for display
FPS = 60
FRAME_RATE = 1  # Display each frame per second

# Color constants
COLOR_MAP = {
    0: (0, 0, 0),       # BLACK
    1: (255, 255, 255), # WHITE
    2: (255, 0, 0),     # RED
    3: (0, 255, 0),     # GREEN
    4: (0, 0, 255),     # BLUE
    5: (255, 255, 0),   # YELLOW
    6: (255, 192, 203), # PINK
    7: (173, 216, 230), # LIGHTBLUE
    8: (128, 0, 128),   # PURPLE
}

# Load and parse .pixil file
def load_pixil_file(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    # Extract the "frames" from the .pixil file
    # Assuming it contains an array of frames with pixel color data
    return data.get("frames", [])

# Draw a frame on the screen
def draw_pixil_frame(frame, surface, pixel_size):
    for y, row in enumerate(frame):
        for x, cell in enumerate(row):
            color = COLOR_MAP.get(cell, (0, 0, 0))  # Map number to color, default to BLACK
            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(
                    x * pixel_size,
                    y * pixel_size,
                    pixel_size,
                    pixel_size
                )
            )

# Load the .pixil file
pixil_file = "black_pixel_alien.pixil"  # Replace with the path to your .pixil file
frames = load_pixil_file(pixil_file)

if not frames:
    print("No frames found in the .pixil file.")
    sys.exit()

# Setup Pygame display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Main loop
frame_index = 0
last_update_time = pygame.time.get_ticks()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update (cycle through frames for animation if multiple frames exist)
    current_time = pygame.time.get_ticks()
    if current_time - last_update_time > 1000 // FRAME_RATE:
        frame_index = (frame_index + 1) % len(frames)
        last_update_time = current_time

    # Draw
    screen.fill((0, 0, 0))  # Clear screen
    draw_pixil_frame(frames[frame_index], screen, PIXEL_SIZE)
    pygame.display.flip()

    # Control frame rate
    clock.tick(FPS)

