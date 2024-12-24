import pygame
import random
import sys
from sprite import SpriteAnimator

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invader")

# Font for displaying points and lives
font = pygame.font.Font(None, 36)

# Load sounds
pygame.mixer.init()
laser_sound = pygame.mixer.Sound("laser.mp3")
alien_move_sound = pygame.mixer.Sound("alien_move1.wav")
background_music = "spaceinvaders1.mpeg"
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)  # Loop the music

class PointsManager:
    def __init__(self):
        self.points = 0

    def reset_points(self):
        self.points = 0

    def add_points(self, amount):
        self.points += amount

    def render(self, screen):
        points_text = f"Points: {self.points:03d}"
        text_surface = font.render(points_text, True, WHITE)
        screen.blit(text_surface, (10, 10))


class LivesManager:
    def __init__(self):
        self.lives = 3

    def reset_lives(self):
        self.lives = 3

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1

    def render(self, screen):
        lives_text = f"Lives: {self.lives}"
        text_surface = font.render(lives_text, True, WHITE)
        text_rect = text_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(text_surface, text_rect)


class AlienManager:
    def __init__(self, sprite_animator):
        self.sprite_animator = sprite_animator
        self.aliens = []
        self.rows = 4
        self.columns = 6
        self.alien_spacing = 20
        self.direction = 1
        self.speed = 2
        self.cycle_count = 1
        self.lasers = []
        self.laser_speed = 5
        self._create_aliens()

    def _create_aliens(self):
        alien_files = ["black_pixel_alien.pixil", "black_saucer_alien.pixil"]
        for row in range(self.rows):
            for col in range(self.columns):
                alien_name = f"alien_{row}_{col}"
                alien_file = random.choice(alien_files)
                self.sprite_animator.add_sprite(alien_name, alien_file)
                x = col * (self.sprite_animator.pixel_size * 10 + self.alien_spacing)
                y = row * (self.sprite_animator.pixel_size * 10 + self.alien_spacing)
                self.sprite_animator.set_sprite_position(alien_name, x, y)
                self.aliens.append(alien_name)

    def move_aliens(self):
        for alien_name in self.aliens:
            x, y = self.sprite_animator.sprites[alien_name]["position"]
            x += self.direction * self.speed
            self.sprite_animator.set_sprite_position(alien_name, x, y)

        # Change direction if needed
        move_down = False
        for alien_name in self.aliens:
            x, _ = self.sprite_animator.sprites[alien_name]["position"]
            if x < 0 or x + 50 > SCREEN_WIDTH:
                self.direction *= -1
                move_down = True
                break

        if move_down:
            for alien_name in self.aliens:
                x, y = self.sprite_animator.sprites[alien_name]["position"]
                self.sprite_animator.set_sprite_position(alien_name, x, y + 10)
            alien_move_sound.play()

    def check_collision_with_ship(self, ship, lives_manager):
        for alien_name in self.aliens:
            alien_sprite = self.sprite_animator.sprites[alien_name]
            alien_x, alien_y = alien_sprite["position"]
            alien_width = self.sprite_animator.pixel_size * len(alien_sprite["frames"][0][0])
            alien_height = self.sprite_animator.pixel_size * len(alien_sprite["frames"][0])

            if (alien_x < ship.x + 50 and alien_x + alien_width > ship.x and
                alien_y < ship.y + 50 and alien_y + alien_height > ship.y):
                lives_manager.lose_life()
                self.reset_aliens()
                break

    def check_collision_with_lasers(self, lasers, points_manager):
        for laser in lasers[:]:
            for alien_name in self.aliens[:]:
                alien_sprite = self.sprite_animator.sprites[alien_name]
                alien_x, alien_y = alien_sprite["position"]
                alien_width = self.sprite_animator.pixel_size * len(alien_sprite["frames"][0][0])
                alien_height = self.sprite_animator.pixel_size * len(alien_sprite["frames"][0])

                if (laser.x > alien_x and laser.x < alien_x + alien_width and
                    laser.y > alien_y and laser.y < alien_y + alien_height):
                    lasers.remove(laser)
                    self.aliens.remove(alien_name)
                    points_manager.add_points(100)
                    break

        # Check if all aliens are destroyed
        if not self.aliens:
            self.reset_aliens()

    def fire_lasers(self):
        if self.cycle_count > 1 and self.aliens:
            if random.randint(1, 100) <= 5:  # Adjust fire probability as needed
                alien_name = random.choice(self.aliens)
                alien_sprite = self.sprite_animator.sprites[alien_name]
                alien_x, alien_y = alien_sprite["position"]
                laser = pygame.Rect(alien_x + 25, alien_y + 50, 5, 15)
                self.lasers.append(laser)

    def move_lasers(self, ship, lives_manager):
        for laser in self.lasers[:]:
            laser.y += self.laser_speed
            if laser.y > SCREEN_HEIGHT:
                self.lasers.remove(laser)
            elif ship.x < laser.x < ship.x + 50 and ship.y < laser.y < ship.y + 50:
                self.lasers.remove(laser)
                lives_manager.lose_life()

    def reset_aliens(self):
        self.aliens.clear()
        self.cycle_count += 1
        self._create_aliens()

    def render(self):
        for alien_name in self.aliens:
            sprite = self.sprite_animator.sprites[alien_name]
            current_time = pygame.time.get_ticks()
            if current_time - sprite["last_update_time"] > 1000 // self.sprite_animator.frame_rate:
                sprite["frame_index"] = (sprite["frame_index"] + 1) % len(sprite["frames"])
                sprite["last_update_time"] = current_time

            self.sprite_animator.draw_frame(
                sprite["frames"][sprite["frame_index"]],
                screen,
                sprite["position"],
            )

        for laser in self.lasers:
            pygame.draw.rect(screen, RED, laser)


class NavoaShip:
    def __init__(self):
        self.image = pygame.image.load("navoaship.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.x = SCREEN_WIDTH // 2 - 25
        self.y = SCREEN_HEIGHT - 60
        self.speed = 5
        self.lasers = []
        self.laser_speed = 7

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x = max(0, self.x - self.speed)
        if keys[pygame.K_RIGHT]:
            self.x = min(SCREEN_WIDTH - 50, self.x + self.speed)

    def shoot(self):
        laser = pygame.Rect(self.x + 25, self.y, 5, 15)
        self.lasers.append(laser)
        laser_sound.play()

    def move_lasers(self):
        for laser in self.lasers[:]:
            laser.y -= self.laser_speed
            if laser.y < 0:
                self.lasers.remove(laser)

    def render(self):
        screen.blit(self.image, (self.x, self.y))
        for laser in self.lasers:
            pygame.draw.rect(screen, RED, laser)


def game_over_screen():
    while True:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, WHITE)
        score_text = font.render(f"Score: {points_manager.points}", True, WHITE)
        play_again_text = font.render("Play Again", True, WHITE)
        quit_text = font.render("Quit", True, WHITE)

        screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)))
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))

        play_again_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2, 150, 40)
        quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 60, 150, 40)

        pygame.draw.rect(screen, WHITE, play_again_button)
        pygame.draw.rect(screen, WHITE, quit_button)

        play_again_surface = font.render("Play Again", True, BLACK)
        quit_surface = font.render("Quit", True, BLACK)

        screen.blit(play_again_surface, play_again_surface.get_rect(center=play_again_button.center))
        screen.blit(quit_surface, quit_surface.get_rect(center=quit_button.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    return True
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# Initialize components
sprite_animator = SpriteAnimator(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
points_manager = PointsManager()
lives_manager = LivesManager()

while True:
    alien_manager = AlienManager(sprite_animator)
    navoa_ship = NavoaShip()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    navoa_ship.shoot()

        keys = pygame.key.get_pressed()
        navoa_ship.move(keys)

        navoa_ship.move_lasers()
        alien_manager.move_aliens()
        alien_manager.check_collision_with_ship(navoa_ship, lives_manager)
        alien_manager.check_collision_with_lasers(navoa_ship.lasers, points_manager)
        alien_manager.fire_lasers()
        alien_manager.move_lasers(navoa_ship, lives_manager)

        # Check game over
        if lives_manager.lives <= 0:
            if game_over_screen():
                points_manager.reset_points()
                lives_manager.reset_lives()
                break

        # Drawing
        screen.fill(BLACK)
        alien_manager.render()
        navoa_ship.render()
        points_manager.render(screen)
        lives_manager.render(screen)
        pygame.display.flip()

        clock.tick(60)
