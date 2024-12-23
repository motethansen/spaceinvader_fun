import pygame
import json
import sys

class SpriteAnimator:
    def __init__(self, screen_width=320, screen_height=240, pixel_size=10, fps=60, frame_rate=1):
        # Pygame initialization
        pygame.init()

        # Constants
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pixel_size = pixel_size
        self.fps = fps
        self.frame_rate = frame_rate
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        # Color constants
        self.color_map = {
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

        self.sprites = {}  # To store frames for multiple sprite animations

    def load_pixil_file(self, filename):
        """Load and parse a .pixil file."""
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            return data.get("frames", [])
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []

    def add_sprite(self, name, filename):
        """Add a sprite animation by loading its frames from a .pixil file."""
        frames = self.load_pixil_file(filename)
        if frames:
            self.sprites[name] = {
                "frames": frames,
                "frame_index": 0,
                "last_update_time": pygame.time.get_ticks(),
                "position": (0, 0)  # Default position (x, y)
            }
        else:
            print(f"No frames found in {filename}.")

    def set_sprite_position(self, name, x, y):
        """Set the position of a sprite on the screen."""
        if name in self.sprites:
            self.sprites[name]["position"] = (x, y)
        else:
            print(f"Sprite '{name}' not found.")

    def draw_frame(self, frame, surface, position):
        """Draw a single frame on the screen at a given position."""
        x_offset, y_offset = position
        for y, row in enumerate(frame):
            for x, cell in enumerate(row):
                color = self.color_map.get(cell, (0, 0, 0))
                pygame.draw.rect(
                    surface,
                    color,
                    pygame.Rect(
                        x_offset + x * self.pixel_size,
                        y_offset + y * self.pixel_size,
                        self.pixel_size,
                        self.pixel_size
                    )
                )

    def animate(self):
        """Main animation loop to handle sprite animations."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Clear the screen
            self.screen.fill((0, 0, 0))

            # Draw and update each sprite
            for sprite in self.sprites.values():
                current_time = pygame.time.get_ticks()
                if current_time - sprite["last_update_time"] > 1000 // self.frame_rate:
                    sprite["frame_index"] = (sprite["frame_index"] + 1) % len(sprite["frames"])
                    sprite["last_update_time"] = current_time

                frame = sprite["frames"][sprite["frame_index"]]
                self.draw_frame(frame, self.screen, sprite["position"])

            pygame.display.flip()
            self.clock.tick(self.fps)

# Example usage
if __name__ == "__main__":
    animator = SpriteAnimator()
    #animator.add_sprite("alien", "black_pixel_alien.pixil")  # Replace with your .pixil file paths
    #animator.add_sprite("alien_saucer", "black_saucer_alien.pixil")
    #animator.add_sprite("space_invader", "black_space_invader.pixil")
    #animator.add_sprite("blck_alien", "blck_alien.pixil")
    #animator.add_sprite("blue_alien", "blue_alien.pixil")
    animator.add_sprite("explotion", "explotion.pixil")
    #animator.set_sprite_position("alien", 50, 50)  # Set initial position
    #animator.set_sprite_position("alien_saucer", 150, 50)
    #animator.set_sprite_position("space_invader", 50, 50)
    #animator.set_sprite_position("blue_alien", 150, 150)
    animator.set_sprite_position("explotion", 150, 150)
    animator.animate()

   


