import pygame
import random
import sys
import time
from pathlib import Path

# --- Pygame Initialization ---
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Multiplication Shooter: Asteroid Defense")

# File Locations
app_dir = Path(__file__).parent
sprite_dir = app_dir.joinpath("sprites/")

# Renderable Dimensions
HUD_HEIGHT=40
SCREEN_RENDER_HEIGHT = SCREEN_HEIGHT-HUD_HEIGHT # Bottom of renderable gaming area is shortened to account for the HUD at the top

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)

# Fonts
font_large = pygame.font.SysFont("monospace", 30)
font_medium = pygame.font.SysFont("monospace", 20)
font_small = pygame.font.SysFont("monospace", 20)

# Game variables
score = 0
game_over = False
current_input = ""
clock = pygame.time.Clock()
last_fizzle_time = 0
SHIP_SPEED=5
ASTEROID_SPEED=1.0

# global sprites in memory
asteroid_sprites = [
    pygame.image.load(sprite_dir.joinpath('Asteroid.png')).convert_alpha()
]
ship_sprite = pygame.image.load(sprite_dir.joinpath('ship.png')).convert_alpha()

# --- Utility Functions ---

def generate_problem():
    """Generates a random multiplication problem (1-12 tables)."""
    a = random.randint(1, 12)
    b = random.randint(1, 12)
    problem = f"{a} \u00D7 {b}" # \u00D7 is the multiplication sign
    answer = a * b
    return problem, answer


class SpriteSheet:
    def __init__(self, filename):
        try:
            # Load the image. convert_alpha() is crucial for transparency and speed.
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def get_image(self, x, y, width, height):
        """
        Extracts a single image from the larger sheet.
        x, y: The top-left coordinate of the sprite on the sheet itself.
        width, height: The dimensions of the sprite to cut out.
        """
        # Create a rectangle defining the area we want to cut out
        rect = pygame.Rect(x, y, width, height)
        
        # 'subsurface' creates a new surface that shares pixel data 
        # with the original. It's fast and memory efficient.
        image_segment = self.sheet.subsurface(rect)
        
        return image_segment

# --- Game Objects ---

class Asteroid(pygame.sprite.Sprite):
    """Represents an asteroid carrying a math problem."""
    def __init__(self, speed = ASTEROID_SPEED):
        super().__init__()
        self.problem_str, self.answer = generate_problem()
        self.radius = 40
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        #pygame.draw.circle(self.image, (150, 150, 150), (self.radius, self.radius), self.radius)
        self.image.blit(asteroid_sprites[0],(0,0))
        # Add the problem text
        font_medium.set_bold(True)
        text_surface = font_medium.render(self.problem_str, True, YELLOW)
        font_medium.set_bold(False)
        text_rect = text_surface.get_rect(center=(self.radius, self.radius))
        self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(2*self.radius, SCREEN_WIDTH - (2*self.radius))
        self.rect.y = -self.radius * 2  # Start off-screen
        self.speed = speed

    def update(self):
        """Moves the asteroid down."""
        self.rect.y += self.speed
        if self.rect.bottom > SCREEN_RENDER_HEIGHT:
            global game_over
            game_over = True

    def draw(self):
        pass

class Projectile(pygame.sprite.Sprite):
    """Represents the projectile fired by the gun."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([6, 15])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10

    def update(self):
        """Moves the projectile up."""
        self.rect.y -= self.speed
        # Remove if it goes off-screen
        if self.rect.bottom < 0:
            self.kill()

class Gun:
    """Represents the player's fixed cannon."""
    def __init__(self):
        self.width = 39
        self.height = 64
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = HUD_HEIGHT+SCREEN_RENDER_HEIGHT - self.height - 10
        self.color = BLUE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.fizzle_effect = False
        self.moving_left=False
        self.moving_right=False

    def move(self):
        if self.moving_left:
            self.x -= SHIP_SPEED
        if self.moving_right:
            self.x += SHIP_SPEED

        # Screen edge clamping
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        # Update the rect position based on x
        self.rect.x = self.x

    def draw(self, surface):
        """Draws the gun on the screen."""
        surface.blit(ship_sprite,(self.x, self.y))


    def fizzle(self):
        """Activates a temporary fizzle effect."""
        self.fizzle_effect = True
        global last_fizzle_time
        last_fizzle_time = time.time()
    
    def update_fizzle(self):
        """Turns off the fizzle effect after a short delay."""
        if self.fizzle_effect and (time.time() - last_fizzle_time < 0.5):
            self.color=RED
        else:
            self.color=BLUE
            self.fizzle_effect = False

class StarField:
    def __init__(self):
        self.__star_sprites = [
            [], # Medium Stars
            [], # Large Stars
            [], # Small Stars
            [] # Smallest Stars
        ]
        star_ratio = [5, 2, 20, 100]   # by column index: Medium, Large, Small, Smallest...  For every 100 smallest stars, there are 2 Large and 5 Medium stars...
        star_speed = [.5, .35, .1, .05] # by column index: Medium, Large, Small, Smallest... Smallest stars are furthest away and slowest

        STAR_ROWS=3
        self.__SPRITE_WIDTH=8
        SPRITE_HEIGHT=8
        star_spritesheet = SpriteSheet(sprite_dir.joinpath('stars.png'))


        # Build Initial Star Field
        
        for star_size, star_num in enumerate(star_ratio):
            for star_id in range(star_num): # Create a star of the appropriate size following the ratio list
                color_id = random.randint(0,STAR_ROWS-1) # Select random star color
                spritesheet_frame_x=star_size*self.__SPRITE_WIDTH
                spritesheet_frame_y=color_id*SPRITE_HEIGHT
                
                # Extract the sprite
                star_sprite = star_spritesheet.get_image(spritesheet_frame_x, spritesheet_frame_y, self.__SPRITE_WIDTH, SPRITE_HEIGHT)
                y = random.randint(HUD_HEIGHT-8,SCREEN_RENDER_HEIGHT-8)  # Each star sprite is 8px
                x = random.randint(-self.__SPRITE_WIDTH,SCREEN_WIDTH)

                # 2. Get the current size
                w = star_sprite.get_width()
                h = star_sprite.get_height()

                # 3. Scale it up x4
                # pygame.transform.scale(image, (new_width, new_height))
                star_sprite = pygame.transform.scale(star_sprite, (w * 2, h * 2))

                self.__star_sprites[star_size].append({'sprite':star_sprite, 'x':x, 'y':y, 'speed':star_speed[star_size]})

    def update(self):
        for sprite_group_id in range(len(self.__star_sprites)):
            for sprite_id in range(len(self.__star_sprites[sprite_group_id])):
                this_sprite = self.__star_sprites[sprite_group_id][sprite_id]
                if this_sprite['y']>=SCREEN_RENDER_HEIGHT:
                    self.__star_sprites[sprite_group_id][sprite_id].update({'y':HUD_HEIGHT-8, 'x':random.randint(-self.__SPRITE_WIDTH,SCREEN_WIDTH)})
                else:
                    self.__star_sprites[sprite_group_id][sprite_id].update({'y':(this_sprite['y']+this_sprite['speed'])})
                
    def draw(self, screen):
        for sprite_group in self.__star_sprites:
            for sprite in sprite_group:
                screen.blit(sprite['sprite'], (sprite['x'], sprite['y']))


# --- Game Setup ---

def initialize_game():
    """Sets up initial game state and objects."""
    global score, game_over, current_input, all_sprites, asteroids, projectiles
    


    score = 0
    game_over = False
    current_input = ""
    
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    
    
    # Create the first asteroid
    new_asteroid = Asteroid()
    asteroids.add(new_asteroid)
    all_sprites.add(new_asteroid)
    
    # Create the gun
    gun = Gun()
    starfield = StarField()
    
    return gun, new_asteroid, starfield


gun, current_asteroid, starfield = initialize_game()


# --- Drawing Functions ---

def draw_input_box(surface, input_text, is_fizzling):
    """Draws the input box and the current text."""
    # Input box dimensions
    input_box_rect = pygame.Rect(200, 0, 200, 40)
    
    # Background for input box
    box_color = RED if is_fizzling else (50, 50, 50)
    pygame.draw.rect(surface, box_color, input_box_rect, border_radius=5)
    pygame.draw.rect(surface, WHITE, input_box_rect, 2, border_radius=5) # Border

    # Render input text
    text_surface = font_medium.render(input_text, True, WHITE)
    text_rect = text_surface.get_rect(center=input_box_rect.center)
    surface.blit(text_surface, text_rect)

    # Instruction text
    instruction_text = font_small.render("Enter Answer and Press ENTER", True, WHITE)
    surface.blit(instruction_text, (input_box_rect.right + 10, input_box_rect.top+10))

def draw_hud(surface):
    """Draws score and other UI elements."""
    HUD_backdrop = pygame.Rect(0,0,SCREEN_WIDTH, HUD_HEIGHT)
    pygame.draw.rect(surface, BLACK, HUD_backdrop, border_radius=0)
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    surface.blit(score_text, (10, 10))

def draw_game_over(surface):
    """Draws the game over screen."""
    surface.fill(BLACK)
    
    title_text = font_large.render("GAME OVER", True, RED)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    surface.blit(title_text, title_rect)

    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
    surface.blit(score_text, score_rect)
    
    restart_text = font_small.render("Press R to Restart or Q to Quit", True, YELLOW)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    surface.blit(restart_text, restart_rect)


# --- Game Loop ---
running = True
while running:
    
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    gun, current_asteroid, starfield = initialize_game()
                elif event.key == pygame.K_q:
                    running = False
            continue

        if event.type == pygame.KEYDOWN:
            print(event.key)
            if (event.key == pygame.K_a) | (event.key == pygame.K_LEFT):
                gun.moving_left = True
            elif (event.key == pygame.K_d) | (event.key == pygame.K_RIGHT):
                gun.moving_right=True
            if (event.key == pygame.K_RETURN) | (event.key == pygame.K_KP_ENTER):
                # Check the input answer
                try:
                    user_answer = int(current_input)
                    if (user_answer == current_asteroid.answer)&(gun.fizzle_effect==False):
                        # Correct answer: Fire projectile
                        new_projectile = Projectile(gun.rect.centerx, gun.rect.top)
                        projectiles.add(new_projectile)
                        all_sprites.add(new_projectile)
                        current_input = "" # Clear input
                    else:
                        # Incorrect answer: Fizzle
                        gun.fizzle()
                        current_input = "" # Clear input
                except ValueError:
                    # Input wasn't a number
                    gun.fizzle()
                    current_input = "" # Clear input

            elif event.key == pygame.K_BACKSPACE:
                current_input = current_input[:-1]
            elif event.unicode.isdigit():
                # Append digit to input string
                current_input += event.unicode

        if event.type == pygame.KEYUP:
                if (event.key == pygame.K_a) | (event.key == pygame.K_LEFT):
                    gun.moving_left = False
                elif (event.key == pygame.K_d) | (event.key == pygame.K_RIGHT):
                    gun.moving_right=False

    if not game_over:
        # --- Update Logic ---
        starfield.update()
        all_sprites.update()
        gun.update_fizzle()
        gun.move()

        # Check for projectile hitting the current asteroid
        hits = pygame.sprite.spritecollide(current_asteroid, projectiles, True)
        if hits:
            score += 10
            
            # Remove old asteroid
            current_asteroid.kill()
            
            # Create a new one
            current_asteroid = Asteroid(speed=random.uniform(.5,1.8))
            asteroids.add(current_asteroid)
            all_sprites.add(current_asteroid)

        # Check if the current asteroid hit the ground (Game Over handled in Asteroid.update)
        if current_asteroid not in all_sprites:
             # This means the asteroid was killed by the ground check (game over) or a hit
             if not game_over:
                 # If it was hit, generate a new one immediately
                 current_asteroid = Asteroid()
                 asteroids.add(current_asteroid)
                 all_sprites.add(current_asteroid)

        

        # --- Drawing ---
        screen.fill(BLACK)
        starfield.draw(screen)
        all_sprites.draw(screen)
        gun.draw(screen)
        
        draw_hud(screen)
        draw_input_box(screen, current_input, gun.fizzle_effect)
        

    else:
        # Game Over Screen
        draw_game_over(screen)

    # Always update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()