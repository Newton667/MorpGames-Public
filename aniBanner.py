import pygame
import os
import random

# Initialize Pygame
pygame.init()

# Set up the display
window_width = 1200
window_height = 500
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Animated Banner with Walking Morps")

# Set up the frame rate
clock = pygame.time.Clock()

# Load the banner image
banner_path = os.path.join('Pictures', 'MoonBanner.png')
banner = pygame.image.load(banner_path).convert()
banner = pygame.transform.scale(banner, (window_width, window_height))

# Load the character images (morp and walking morp)
morp_path = os.path.join('Pictures', 'Morp_2.png')
morp_walk_path = os.path.join('Pictures', 'MorpWalk.png')
morp_image = pygame.image.load(morp_path).convert_alpha()
morp_walk_image = pygame.image.load(morp_walk_path).convert_alpha()

# Resize the character images (making them smaller)
morp_image = pygame.transform.scale(morp_image, (75, 100))
morp_walk_image = pygame.transform.scale(morp_walk_image, (75, 100))

# Set up the font for the score
font = pygame.font.SysFont(None, 36)

# Global speed modifier (this increases as more Morps are flicked)
global_speed_modifier = 1.0

# Class to represent a Morp
class Morp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 75
        self.height = 100
        self.current_image = morp_image
        self.animation_toggle = True
        self.falling = False
        self.dodging = False
        self.x_speed = 2 * global_speed_modifier  # Slow initial speed for walking
        self.fall_speed_x = 0  # Horizontal flick speed
        self.fall_speed_y = 0  # Vertical speed (initial upward, then downward)
        self.gravity = 1.2     # Gravity to pull the Morp down

    def update(self):
        # Update walking speed based on global modifier
        self.x_speed = 2 * global_speed_modifier

        # Toggle walking animation if not falling or dodging
        if not self.falling and not self.dodging:
            if self.animation_toggle:
                self.current_image = morp_walk_image
            else:
                self.current_image = morp_image
            self.animation_toggle = not self.animation_toggle

            # Move slowly across the screen
            self.x += self.x_speed
            if self.x > window_width:
                self.x = -self.width

        # Handle dodging by moving the Morp left or right temporarily
        if self.dodging:
            self.x += random.choice([-100, 100])  # Move left or right randomly
            self.dodging = False  # Only dodge once, then reset

        # Handle falling if flicked
        if self.falling:
            self.x += self.fall_speed_x  # Apply horizontal movement
            self.y += self.fall_speed_y  # Apply vertical movement
            self.fall_speed_y += self.gravity  # Increase fall speed due to gravity
            
            # Stop the fall if the Morp hits the bottom of the screen
            if self.y > window_height:
                self.y = window_height
                self.fall_speed_y = 0
                self.fall_speed_x = 0

    def draw(self, screen):
        screen.blit(self.current_image, (self.x, self.y))

    def check_collision(self, pos):
        # Check if the mouse click is within the Morp's bounds
        if self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height:
            return True
        return False

    def flick(self, flick_strength):
        # Flick upwards aggressively and increase speed
        self.falling = True
        self.x_speed = 10 * global_speed_modifier  # Increase speed after being flicked
        self.fall_speed_y = -20  # Faster initial upward motion
        self.fall_speed_x = flick_strength * 1.5  # Flicked horizontal speed

    def dodge(self):
        # Dodge by moving left or right quickly
        self.dodging = True


# List to hold all the Morps
morps = []

# Score
score = 0
score_visible = False  # Score appears when the first Morp is flicked

# Function to randomly add a Morp from the left
def add_morp():
    y = 300  # All morps start at the same y position
    morps.append(Morp(-75, y))  # Spawn at the left side, just outside the screen

# Timer for random Morp spawning
spawn_timer = random.randint(50, 150)  # Random initial spawn timer

# Variables to track mouse movement for flick intensity
mouse_start_pos = None
mouse_end_pos = None

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Track the starting position of the mouse for flick
            mouse_start_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            # Track the ending position of the mouse for flick
            mouse_end_pos = pygame.mouse.get_pos()

            # Calculate flick strength (horizontal distance of mouse movement)
            if mouse_start_pos and mouse_end_pos:
                flick_strength = (mouse_end_pos[0] - mouse_start_pos[0]) / 5  # More sensitive to mouse movement
                
                # Check if any Morp is clicked
                for morp in morps:
                    if morp.check_collision(mouse_start_pos) and not morp.falling:
                        # 30% chance to dodge the flick
                        if random.random() < 0.3:
                            morp.dodge()
                        else:
                            # Use the global keyword to modify the global variable
                            global_speed_modifier
                            # Flick the Morp with the calculated strength
                            morp.flick(flick_strength)

                            # Increase score and make it visible when first Morp is flicked
                            if not score_visible:
                                score_visible = True
                            score += 1

                            # Increase global speed as more Morps are flicked
                            global_speed_modifier += 0.1  # Speed up walking as more Morps are flicked

                            # Chance to spawn new Morps on flick
                            if random.random() < 0.5:  # 50% chance of spawning a new Morp
                                add_morp()

            mouse_start_pos = None  # Reset the flick position after flicking

    # Decrease the spawn timer and add a new Morp when it reaches zero
    spawn_timer -= 1
    if spawn_timer <= 0:
        add_morp()  # Add a new Morp
        spawn_timer = random.randint(50, 150)  # Reset the timer with a random value

    # Update the Morps
    for morp in morps:
        morp.update()

    # Draw the banner and Morps
    screen.blit(banner, (0, 0))
    for morp in morps:
        morp.draw(screen)

    # Display the score if it's visible
    if score_visible:
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))  # Draw score in the top-left corner

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(30)  # Increase frame rate to make it smoother

# Quit Pygame
pygame.quit()
