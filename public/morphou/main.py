import pygame
import sys
import random
import math
import asyncio

# Constants
sWidth = 800
sHeight = 600
pSize = 40
eSize = 40
bSize = 10
bSpeed = 10
enemySpeed = 10
fire_rate = 6  # Bullet fire rate
bullet_delay = 1500 // fire_rate  # milliseconds
score = 0
enemy_spawn_delay = 1300
enemy_bullet_delay = 1000
enemy2_spawn_delay = 10000
enemy3_spawn_delay = 20000

# Load and scale images only once
player_img = pygame.image.load('./morphou_assets/Morp.png')
player_img = pygame.transform.scale(player_img, (pSize, pSize))

enemy1_img = pygame.image.load('./morphou_assets/enemy1.png')
enemy1_img = pygame.transform.scale(enemy1_img, (eSize, eSize))

enemy2_img = pygame.image.load('./morphou_assets/enemy2.png')
enemy2_img = pygame.transform.scale(enemy2_img, (eSize, eSize))

enemy3_img = pygame.image.load('./morphou_assets/enemy3.png')
enemy3_img = pygame.transform.scale(enemy3_img, (eSize, eSize))

bullet_img = pygame.image.load('./morphou_assets/bullet.png')
bullet_img = pygame.transform.scale(bullet_img, (bSize, bSize))

background_img = pygame.image.load('./morphou_assets/background.png')


pygame.init()
screen = pygame.display.set_mode((sWidth, sHeight))
pygame.display.set_caption("Morphou")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Global variables
game_over = False

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.midleft = (0, sHeight // 2)
        self.speed = 8
        self.hp = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < sHeight: self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < sWidth: self.rect.x += self.speed

    def damage(self):
        self.hp -= 1
        if self.hp <= 0:
            return True  # Return True if player is dead
        return False

# Base Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, size, image, hp, fire_pattern):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midright = (random.randint(int(sWidth * 0.8), sWidth), random.randint(0, sHeight))
        self.hp = hp
        self.fire_pattern = fire_pattern
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        self.fire_pattern()

    def fire(self, angle=0):
        bullet = Bullet(self.rect.centerx, self.rect.centery, -enemySpeed, self, angle)
        bullets.add(bullet)
        all_sprites.add(bullet)
        self.last_shot_time = pygame.time.get_ticks()

    def damage(self):
        global score
        self.hp -= 1
        if self.hp <= 0:
            score += 100 * (self.hp + 1)  # Scale score based on HP
            self.kill()

# Specific Enemy Types
class Enemy1(Enemy):
    def __init__(self):
        super().__init__(size=40, image=enemy1_img, hp=1, fire_pattern=self.fire_pattern)

    def fire_pattern(self):
        if pygame.time.get_ticks() - self.last_shot_time >= enemy_bullet_delay:
            self.fire()

class Enemy2(Enemy):
    def __init__(self):
        super().__init__(size=40, image=enemy2_img, hp=2, fire_pattern=self.fire_pattern)

    def fire_pattern(self):
        if pygame.time.get_ticks() - self.last_shot_time >= enemy_bullet_delay:
            for angle in range(-45, 46, 15):
                self.fire(angle)

class Enemy3(Enemy):
    def __init__(self):
        super().__init__(size=40, image=enemy3_img, hp=3, fire_pattern=self.fire_pattern)

    def fire_pattern(self):
        if pygame.time.get_ticks() - self.last_shot_time >= 100:
            self.fire(self.current_angle)
            self.current_angle = (self.current_angle + 10) % 60

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, shooter, angle=0):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.angle = angle
        self.shooter = shooter

    def update(self):
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y += self.speed * math.sin(math.radians(self.angle))
        if not screen.get_rect().colliderect(self.rect): self.kill()

# Reinitialize game state
def refresh_game():
    global all_sprites, bullets, enemies, player, score, last_shot_time, last_enemy_spawn, last_enemy2_spawn, last_enemy3_spawn, start_time
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    score = 0
    last_shot_time = pygame.time.get_ticks()
    last_enemy_spawn = pygame.time.get_ticks()  # Initialize spawn timers
    last_enemy2_spawn = pygame.time.get_ticks()
    last_enemy3_spawn = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()

# Title screen
async def title_screen():
    screen.fill((0, 0, 0))
    title_text = font.render('Morphou', True, (255, 255, 255))
    screen.blit(title_text, (sWidth // 2 - title_text.get_width() // 2, sHeight // 3))

    button_color = (255, 0, 255)
    button_rect = pygame.Rect(sWidth // 2 - 100, sHeight // 2, 200, 50)
    pygame.draw.rect(screen, button_color, button_rect)

    button_text = font.render('Start', True, (255, 255, 255))
    screen.blit(button_text, (sWidth // 2 - button_text.get_width() // 2, sHeight // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    global running
                    running = True
                    waiting = False
        await asyncio.sleep(0)

# Game Over screen
async def game_over_screen():
    screen.fill((0, 0, 0))
    
    # Display "GAME OVER" text
    game_over_text = font.render('GAME OVER', True, (255, 0, 0))
    screen.blit(game_over_text, (sWidth // 2 - game_over_text.get_width() // 2, sHeight // 3))
    
    # Display final score
    final_score_text = font.render(f'Score: {score:06}', True, (255, 255, 255))
    screen.blit(final_score_text, (sWidth // 2 - final_score_text.get_width() // 2, sHeight // 3 + 50))
    
    # Restart button
    restart_button_rect = pygame.Rect(sWidth // 2 - 100, sHeight // 2, 200, 50)
    pygame.draw.rect(screen, (0, 255, 0), restart_button_rect)
    restart_text = font.render('Restart', True, (255, 255, 255))
    screen.blit(restart_text, (sWidth // 2 - restart_text.get_width() // 2, sHeight // 2))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    refresh_game()
                    global game_over, running
                    game_over = False
                    running = True
                    waiting = False
        await asyncio.sleep(0)

# Game loop
async def main():
    global running, last_shot_time, last_enemy_spawn, last_enemy2_spawn, last_enemy3_spawn, game_over
    running = True
    game_over = False
    bg_x1 = 0  # Initialize bg_x1
    bg_x2 = background_img.get_width()

    await title_screen()

    while running:
        refresh_game()

        while running:
            clock.tick(60)  # Frame rate of 60 FPS

            if game_over:
                await game_over_screen()
                await asyncio.sleep(0)
                continue

            await handle_events()

            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            time_elapsed = current_time - start_time

            # Player shooting
            if keys[pygame.K_SPACE] and current_time - last_shot_time >= bullet_delay:
                bullet = Bullet(player.rect.right, player.rect.centery, bSpeed, player)
                bullets.add(bullet)
                all_sprites.add(bullet)
                last_shot_time = current_time

            # Enemy spawning
            if current_time - last_enemy_spawn >= enemy_spawn_delay:
                enemy = Enemy1()
                enemies.add(enemy)
                all_sprites.add(enemy)
                last_enemy_spawn = current_time

            if time_elapsed >= 30000 and current_time - last_enemy2_spawn >= enemy2_spawn_delay:
                enemy = Enemy2()
                enemies.add(enemy)
                all_sprites.add(enemy)
                last_enemy2_spawn = current_time

            if time_elapsed >= 60000 and current_time - last_enemy3_spawn >= enemy3_spawn_delay:
                enemy = Enemy3()
                enemies.add(enemy)
                all_sprites.add(enemy)
                last_enemy3_spawn = current_time

            # Collision detection
            for bullet in bullets:
                if bullet.shooter == player:
                    hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
                    for enemy in hit_enemies:
                        enemy.damage()
                        bullet.kill()

                elif pygame.sprite.collide_rect(bullet, player):
                    if player.damage():
                        game_over = True  # Set game over if player is dead
                    bullet.kill()

            # Background movement
            screen.fill((0, 0, 0))
            bg_width = background_img.get_width()
            bg_x1 -= 2
            bg_x2 -= 2

            # Reset background positions if they go off the screen
            if bg_x1 <= -bg_width:
                bg_x1 = bg_width
            if bg_x2 <= -bg_width:
                bg_x2 = bg_width

            screen.blit(background_img, (bg_x1, 0))
            screen.blit(background_img, (bg_x2, 0))

            # Update and draw sprites
            all_sprites.update()
            all_sprites.draw(screen)

            # Display score and player HP
            score_display = font.render(f'Score: {score:06}', True, (255, 255, 255))
            screen.blit(score_display, (sWidth - 200, 20))
            hp_display = font.render(f'HP: {player.hp}', True, (255, 255, 255))
            screen.blit(hp_display, (20, 20))

            pygame.display.flip()

            await asyncio.sleep(0)

async def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit

asyncio.run(main())
