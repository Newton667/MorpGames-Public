import pygame
import sys
import asyncio

pygame.init()

# Game dimensions
Width = 876
Height = 1000
TileSize = 50
pygame.display.set_caption("Evil Morph")
displayRes = pygame.display.set_mode((Width, Height))

# Load images
background_images = [
    pygame.image.load(f'pictures/bg_layer_{i}.png').convert() for i in range(1, 5)
]
tile = pygame.image.load('pictures/tile.png')

# Character Class
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        image = pygame.image.load('pictures/Morp.png')
        self.original_image = pygame.transform.scale(image, (30, 30))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.jumping = False
        self.jumpVel = 0
        self.daGrav = 1.5  # Slower falling
        self.onTile = False
        self.doubleJump = False
        self.jumpCooldown = 0
        self.speed = 4  # Smooth horizontal movement

    def update(self, keys):
        cx = 0
        cy = 6

        if self.jumpCooldown > 0:
            self.jumpCooldown -= 1

        if keys[pygame.K_LEFT]:
            cx -= self.speed
            self.image = pygame.transform.flip(self.original_image, True, False)
        if keys[pygame.K_RIGHT]:
            cx += self.speed
            self.image = self.original_image

        if self.jumping:
            cy += self.jumpVel
            self.jumpVel = min(self.jumpVel + self.daGrav, 10)  # Clamp falling speed

        self.move(cx, cy)

    def move(self, cx, cy):
        self.rect.x += cx
        collisions = pygame.sprite.spritecollide(self, tiles, False)
        for tile in collisions:
            if cx > 0:  # Moving right
                self.rect.right = tile.rect.left
            elif cx < 0:  # Moving left
                self.rect.left = tile.rect.right

        self.rect.y += cy
        collisions = pygame.sprite.spritecollide(self, tiles, False)
        self.onTile = False
        for tile in collisions:
            if cy > 0:  # Falling
                self.rect.bottom = tile.rect.top
                self.jumping = False
                self.onTile = True
                self.doubleJump = False
                cy = 0
            elif cy < 0:  # Jumping upwards
                self.rect.top = tile.rect.bottom
                self.jumpVel = 0

    def handle_jump(self):
        if self.onTile and not self.jumping and self.jumpCooldown == 0:
            self.jumping = True
            self.jumpVel = -24
            self.jumpCooldown = 15
        elif not self.onTile and not self.doubleJump:
            self.jumping = True
            self.jumpVel = -24
            self.doubleJump = True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        image = pygame.image.load('pictures/EMorp.png')
        self.image = pygame.transform.scale(image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.jumping = False
        self.jumpVel = 0
        self.daGrav = 1.5  # Gravity for falling
        self.speed = 2  # Walking speed
        self.fly_speed = 3  # Flying speed
        self.jump_power = -25  # Adjusted jump power
        self.onTile = False
        self.target_tile = None  # Tile to jump toward
        self.flying = False  # State to track flying
        self.flying_cooldown = 0  # Cooldown to avoid rapid switching

    def update(self, player):
        cx = 0
        cy = 6

        # Reduce flying cooldown
        if self.flying_cooldown > 0:
            self.flying_cooldown -= 1

        # Calculate distance to the player
        distance_x = abs(player.rect.x - self.rect.x)
        distance_y = abs(player.rect.y - self.rect.y)

        # Determine flying state
        if self.flying_cooldown == 0:
            self.flying = distance_x > Width // 2 or distance_y > Height // 3

        if self.flying:
            self.fly_towards_player(player)
        else:
            self.check_ground()
            if not self.jumping and self.onTile:
                if player.rect.y < self.rect.y - TileSize:
                    self.set_target_tile(player)
            self.normal_movement(player, cx, cy)

        # Apply gravity and collision if not flying
        if not self.flying:
            self.apply_gravity(cy)

        # Move horizontally if not flying
        if not self.flying:
            self.rect.x += cx

    def fly_towards_player(self, player):
        # Smooth flying movement toward the player (ignoring tile collisions)
        if player.rect.x > self.rect.x:
            self.rect.x += self.fly_speed
        elif player.rect.x < self.rect.x:
            self.rect.x -= self.fly_speed

        if player.rect.y > self.rect.y:
            self.rect.y += self.fly_speed
        elif player.rect.y < self.rect.y:
            self.rect.y -= self.fly_speed

        # Ensure the enemy lands on top of tiles
        self.land_on_tile()

        # Switch back to walking after reaching proximity
        if abs(player.rect.x - self.rect.x) < Width // 4 and abs(player.rect.y - self.rect.y) < Height // 4:
            self.flying = False
            self.flying_cooldown = 30  # Avoid rapid toggling

    def land_on_tile(self):
        # Check for tiles directly below the enemy to simulate landing
        self.rect.y += 1
        collisions = pygame.sprite.spritecollide(self, tiles, False)
        self.onTile = False
        for tile in collisions:
            self.rect.bottom = tile.rect.top
            self.onTile = True
            self.jumping = False
            self.jumpVel = 0
            break  # Only land on the first tile collision

        if not self.onTile:
            self.rect.y -= 1  # Revert position if no tile is below

    def normal_movement(self, player, cx, cy):
        # Walk toward the player horizontally
        if player.rect.x > self.rect.x:
            cx += self.speed
        elif player.rect.x < self.rect.x:
            cx -= self.speed

        # Move toward the target tile
        if self.target_tile:
            self.jump_to_tile()

    def set_target_tile(self, player):
        # Find the best tile to jump toward
        nearest_tile = None
        min_distance = float('inf')
        for tile in tiles:
            if tile.rect.top < self.rect.y:  # Only consider tiles above the enemy
                distance = abs(player.rect.x - tile.rect.x) + abs(player.rect.y - tile.rect.y)
                if distance < min_distance:
                    nearest_tile = tile
                    min_distance = distance

        # Assign the target tile for jumping
        if nearest_tile:
            self.target_tile = nearest_tile
            self.jumping = True
            self.jumpVel = self.jump_power

    def jump_to_tile(self):
        # Move horizontally toward the target tile
        if self.target_tile.rect.x > self.rect.x:
            self.rect.x += self.speed
        elif self.target_tile.rect.x < self.rect.x:
            self.rect.x -= self.speed

        # Check if the enemy has reached the tile
        if abs(self.rect.x - self.target_tile.rect.x) < 5:
            self.jumping = False
            self.target_tile = None

    def apply_gravity(self, cy):
        # Apply jump velocity if jumping
        if self.jumping:
            self.rect.y += self.jumpVel
            self.jumpVel += self.daGrav
            # Stop jumping if falling back down
            if self.jumpVel > 0:
                self.jumping = False

        # Apply vertical movement and handle collisions
        self.rect.y += cy
        collisions = pygame.sprite.spritecollide(self, tiles, False)
        self.onTile = False
        for tile in collisions:
            if cy > 0:  # Falling
                self.rect.bottom = tile.rect.top
                self.jumping = False
                self.onTile = True
                self.jumpVel = 0
                cy = 0
            elif cy < 0:  # Jumping upwards
                self.rect.top = tile.rect.bottom
                self.jumpVel = 0

    def check_ground(self):
        # Check if the enemy is standing on a tile
        self.rect.y += 1
        collisions = pygame.sprite.spritecollide(self, tiles, False)
        self.onTile = bool(collisions)
        if not self.onTile:
            self.rect.y -= 1  # Revert position if not grounded

    def handle_collision_with_player(self, player):
        # Check for collisions with the player
        return self.rect.colliderect(player.rect)



# Tile Class
class Tiles(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = tile
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
# Background
class StaticBackground:
    def __init__(self, images):
        self.images = images
        self.num_images = len(images)
        self.height = images[0].get_height()

    def update(self, camera_offset):
        # Dynamically calculate which image should be at the top
        self.start_index = int(camera_offset // self.height) % self.num_images

    def draw(self, screen, camera_offset):
        # Draw multiple images to cover the screen and eliminate gaps
        first_y = -(camera_offset % self.height)  # Start position for the first image
        for i in range(2):  # Only need two images to cover the screen
            image_index = (self.start_index + i) % self.num_images
            screen.blit(self.images[image_index], (0, first_y + i * self.height))






# Tile map
tiles = pygame.sprite.Group()
tile_map = [
    ' ' * 18,
    '                  ',
    '     tttt         ',
    '                  ',
    '  ttttttttt       ',
    '       tttt       ',
    '                  ',
    'ttttttt           ',
    '        ttt       ',
    '    t             ',
    '                  ',
    '       ttt        ',
    '   tttt      ttt  ',
    '                  ',
    '  ttt             ',
    '     tttt         ',
    '                  ',
    '       ttt        ',
    ' ttt              ',
    '   tttttt         ',
    '                  ',
    '        ttt       ',
    '    tttttttt      ',
    '                  ',
    '  t               ',
    '      ttt         ',
    'tttt              ',
    '                  ',
    '       tttt       ',
    '    tttttt        ',
    '                  ',
    'ttt               ',
    '       t          ',
    '                  ',
    '     ttttt        ',
    '   ttt            ',
    '                  ',
    'ttt        tttt   ',
    '   ttt            ',
    '                  ',
    '    ttt           ',
    '                  ',
    '       ttttt      ',
    ' ttt              ',
    '                  ',
    '          ttt     ',
    '                  ',
    '   ttttttt        ',
    '      ttt         ',
    ' t         t      ',
    '                  ',
    '       tttt       ',
    '   ttt       ttt  ',
    '                  ',
    ' tttt             ',
    '                  ',
    '         tttt     ',
    '   ttt            ',
    '                  ',
    '       ttttt      ',
    '                  ',
    '     tttt         ',
    '                  ',
    ' t                ',
    '   ttttt          ',
    '                  ',
    '       ttt        ',
    '   tttt           ',
    '         t        ',
    '     tttt         ',
    '                  ',
    '          ttt     ',
    '  tttt            ',
    '                  ',
    '       ttt        ',
    '                  ',
    ' ttttt            ',
    '     t            ',
    ' ttt              ',
    '                  ',
    '   ttt            ',
    '          t       ',
    '                  ',
    '       ttttt      ',
    '   ttt            ',
    '                  ',
    ' ttt              ',
    '                  ',
    ' tttt         ttt ',
    '         tttt     ',
    '      ttt         ',
    '   t         tttt ',
    '                  ',
    '       ttt        ',
    '   tt       tttt  ',
    ' ttttt  t         ',
    '          tttt    ',
    '                t ',
    '            ttttt ',
    'tttttttt          ',
    '          tttt    ',
    'ttttt            t',
    '             ttttt',
    '       tttttttt   ',
    'ttt               ',
    '    ttttt         ',
    '           ttt ttt',
    'c    ttttt        ',
    'ttttt             ',
]




characterStartPosition = (0, 0)
camera_offset = 0  # Initialize camera offset


# Function to populate tiles and adjust the player position
def populate_tiles():
    global tiles, characterStartPosition
    tiles.empty()
    character_start_set = False

    for row_cell, row in enumerate(tile_map):
        for col_cell, cell in enumerate(row):
            x, y = col_cell * TileSize, row_cell * TileSize

            if cell == 't':
                tiles.add(Tiles(x, y))
            elif cell == 'c' and not character_start_set:
                characterStartPosition = (x, y)
                character_start_set = True

    # Default to bottom of the screen if 'c' is missing
    if not character_start_set:
        first_tile = next(iter(tiles), None)
        if first_tile:
            characterStartPosition = (first_tile.rect.x, first_tile.rect.y - TileSize)
        else:
            characterStartPosition = (0, Height - TileSize * 2)


populate_tiles()
EvilMorp = Character(*characterStartPosition)

# Initialize background
background = StaticBackground(background_images)

# Game state
pygame.font.init()
font = pygame.font.Font(None, 50)
score = 0
gameOver = False


async def game_over_screen():
    global score
    displayRes.fill((0, 0, 0))
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    restart_text = font.render("Press ESC to Restart", True, (255, 255, 255))

    displayRes.blit(game_over_text, (Width // 2 - game_over_text.get_width() // 2, Height // 3))
    displayRes.blit(score_text, (Width // 2 - score_text.get_width() // 2, Height // 2))
    displayRes.blit(restart_text, (Width // 2 - restart_text.get_width() // 2, Height // 1.5))
    pygame.display.flip()

    while gameOver:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                refresh_game()
                return
        await asyncio.sleep(0.01)


def refresh_game():
    global tiles, EvilMorp, score, gameOver, camera_offset, gracePeriod, enemy
    populate_tiles()
    EvilMorp = Character(*characterStartPosition)

    # Initialize camera_offset to the bottom of the screen
    camera_offset = max(0, EvilMorp.rect.bottom - Height + TileSize)
    score = 0
    gameOver = False

    # Reset the grace period
    gracePeriod = 600  # 10 seconds at 60 FPS

    # Despawn the enemy
    enemy = None




# Game state
pygame.font.init()
font = pygame.font.Font(None, 50)
score = 0
gameOver = False
gracePeriod = 600  # 10 seconds at 60 FPS
enemy = None

async def game_loop():
    global gameOver, score, camera_offset, gracePeriod, enemy
    clock = pygame.time.Clock()

    # Track the highest tile row reached by the player
    highest_tile_row = len(tile_map)

    # Start the camera at the lowest possible point
    camera_offset = max(0, EvilMorp.rect.bottom - Height + TileSize)

    while True:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                EvilMorp.handle_jump()

        if gameOver:
            await game_over_screen()
        else:
            EvilMorp.update(keys)

            # Calculate the current tile row the player is in
            current_tile_row = EvilMorp.rect.top // TileSize

            # Increment score if the player reaches a new row (higher in the tile map)
            if gracePeriod == 0 and current_tile_row < highest_tile_row:
                highest_tile_row = current_tile_row
                score += 1

            # Decrease grace period timer
            if gracePeriod > 0:
                gracePeriod -= 1

            # Spawn the enemy after grace period ends
            if gracePeriod == 0 and enemy is None:
                enemy = Enemy(*characterStartPosition)  # Spawn at the player's starting position

            # Update the enemy if it exists
            if enemy:
                enemy.update(EvilMorp)

                # Check for collision with the player
                if enemy.handle_collision_with_player(EvilMorp):
                    gameOver = True

            # Check if the player falls out of the visible camera window after the grace period
            if gracePeriod == 0 and EvilMorp.rect.top > camera_offset + Height:
                gameOver = True

            # Update Camera: Move up only, never down
            target_offset = max(0, EvilMorp.rect.bottom - Height // 2)
            if target_offset < camera_offset:  # Only update if the player moves upward
                camera_offset -= (camera_offset - target_offset) * 0.1  # Smooth upward movement

            # Update Background
            background.update(camera_offset)
            background.draw(displayRes, camera_offset)

            # Render Tiles with camera offset
            for tile in tiles:
                displayRes.blit(tile.image, (tile.rect.x, tile.rect.y - camera_offset))

            # Render Player with camera offset
            displayRes.blit(EvilMorp.image, (EvilMorp.rect.x, EvilMorp.rect.y - camera_offset))

            # Render Enemy with camera offset
            if enemy:
                displayRes.blit(enemy.image, (enemy.rect.x, enemy.rect.y - camera_offset))

            # Render Grace Period Timer
            if gracePeriod > 0:
                time_left = gracePeriod // 60  # Convert frames to seconds
                grace_text = font.render(f"Grace: {time_left}s", True, (0, 255, 0))
                displayRes.blit(grace_text, (Width - 200, 10))

            # Render Scoreboard
            displaySB = font.render(f"Score: {score}", True, (255, 0, 0))
            displayRes.blit(displaySB, (10, 10))

            pygame.display.update()

        clock.tick(60)
        await asyncio.sleep(0.01)


asyncio.run(game_loop())
