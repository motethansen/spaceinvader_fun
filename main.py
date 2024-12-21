import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invader")

# Load assets
pygame.mixer.music.load("spaceinvaders1.mpeg")
pygame.mixer.music.play(-1)  # Play the music in a loop
laser_sound = pygame.mixer.Sound("laser.mp3")
alien_move_sound = pygame.mixer.Sound("alien_move1.wav")

# Load the NavoaShip sprite
try:
    navoa_ship_image = pygame.image.load("navoaship.png")
    navoa_ship_image = pygame.transform.scale(navoa_ship_image, (50, 50))  # Scale to fit
    navoa_ship_image.set_colorkey((0, 0, 0))  # Assuming black is transparent
except pygame.error as e:
    print(f"Error loading navoaship.png: {e}")
    sys.exit()

# Font for displaying points and lives
font = pygame.font.Font(None, 36)

# Points manager class
class PointsManager:
    def __init__(self):
        self.points = 0

    def add_points(self, amount):
        self.points += amount

    def get_points(self):
        return self.points

    def render_points(self, screen):
        points_text = f"{self.points:03d}"
        text_surface = font.render(points_text, True, WHITE)
        screen.blit(text_surface, (10, 10))

# Lives manager class
class LivesManager:
    def __init__(self):
        self.lives = 3

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1

    def gain_life(self):
        if self.lives < 3:
            self.lives += 1

    def render_lives(self, screen):
        lives_text = f"Lives: {self.lives}"
        text_surface = font.render(lives_text, True, WHITE)
        text_rect = text_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(text_surface, text_rect)

# Alien manager class
class AlienManager:
    def __init__(self):
        self.aliens = []
        self.lasers = []
        self.columns = 6
        self.rows = 4
        self.alien_width = 48
        self.alien_height = 30
        self.colors = [BLUE, RED, GREEN, YELLOW]
        self.spacing = 20
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 2
        self._create_aliens()

    def _create_aliens(self):
        for row in range(self.rows):
            for col in range(self.columns):
                x = col * (self.alien_width + self.spacing) + self.spacing
                y = row * (self.alien_height + self.spacing) + self.spacing
                alien_rect = pygame.Rect(x, y, self.alien_width, self.alien_height)
                self.aliens.append((alien_rect, self.colors[row]))

    def move_aliens(self):
        if points_manager.get_points() >= 5000:
            self.speed = 4  # Increase alien speed when score reaches 5000

        move_down = False
        for alien, _ in self.aliens:
            alien.x += self.direction * self.speed
            if alien.right >= SCREEN_WIDTH or alien.left <= 0:
                move_down = True

        if move_down:
            self.direction *= -1
            for alien, _ in self.aliens:
                alien.y += self.alien_height + self.spacing
            alien_move_sound.play()
        move_down = False
        for alien, _ in self.aliens:
            alien.x += self.direction * self.speed
            if alien.right >= SCREEN_WIDTH or alien.left <= 0:
                move_down = True

        if move_down:
            self.direction *= -1
            for alien, _ in self.aliens:
                alien.y += self.alien_height + self.spacing
            alien_move_sound.play()

    def render_aliens(self, screen):
        for alien, color in self.aliens:
            pygame.draw.rect(screen, color, alien)
        for laser in self.lasers:
            pygame.draw.rect(screen, RED, laser)

    def fire_laser(self):
        if self.aliens:
            alien, _ = random.choice(self.aliens)
            laser = pygame.Rect(alien.centerx - 2, alien.bottom, 4, 10)
            self.lasers.append(laser)

    def update_lasers(self, navoa_ship, lives_manager):
        for laser in self.lasers[:]:
            laser.y += 5
            if laser.y > SCREEN_HEIGHT:
                self.lasers.remove(laser)
            elif laser.colliderect(pygame.Rect(navoa_ship.x, navoa_ship.y, navoa_ship.width, navoa_ship.height)):
                self.lasers.remove(laser)
                lives_manager.lose_life()

    def reset_aliens(self):
        self.aliens.clear()
        self._create_aliens()

# NavoaShip class
class NavoaShip:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 5
        self.lasers = []
        self.laser_speed = 7

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        # Ensure the sprite stays within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

    def shoot(self):
        laser = pygame.Rect(self.x + self.width // 2 - 2, self.y, 4, 10)
        self.lasers.append(laser)
        laser_sound.play()

    def update_lasers(self, alien_manager, points_manager):
        for laser in self.lasers[:]:
            laser.y -= self.laser_speed
            if laser.y < 0:
                self.lasers.remove(laser)
            for alien, _ in alien_manager.aliens[:]:
                if laser.colliderect(alien):
                    alien_manager.aliens.remove((alien, _))
                    self.lasers.remove(laser)
                    points_manager.add_points(100)
                    break

    def render(self, screen):
        screen.blit(navoa_ship_image, (self.x, self.y))
        for laser in self.lasers:
            pygame.draw.rect(screen, RED, laser)

# Initialize the points, lives, and alien managers
points_manager = PointsManager()
lives_manager = LivesManager()
alien_manager = AlienManager()
navoa_ship = NavoaShip()

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                navoa_ship.shoot()

    # Handle keys
    keys = pygame.key.get_pressed()

    # Move NavoaShip
    navoa_ship.move(keys)

    # Update lasers
    navoa_ship.update_lasers(alien_manager, points_manager)
    alien_manager.update_lasers(navoa_ship, lives_manager)

    # Randomly fire alien lasers
    if random.randint(1, 100) == 1:  # Adjust probability as needed
        alien_manager.fire_laser()

    # Move aliens
    alien_manager.move_aliens()

    # Check if all aliens are removed
    if not alien_manager.aliens:
        alien_manager.reset_aliens()

    # Check if any alien is at the same level as the NavoaShip
    for alien, _ in alien_manager.aliens:
        if alien.bottom >= navoa_ship.y:
            lives_manager.lose_life()
            alien_manager.reset_aliens()
            break

    # End game if no lives are left
    if lives_manager.lives <= 0:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    # Drawing everything
    screen.fill(BLACK)  # Clear the screen
    navoa_ship.render(screen)
    points_manager.render_points(screen)
    lives_manager.render_lives(screen)
    alien_manager.render_aliens(screen)
    pygame.display.flip()  # Update the display

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
