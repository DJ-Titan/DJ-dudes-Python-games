import os
from pathlib import Path
import pygame
import sys
import pandas as pd
import datetime

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


clock = pygame.time.Clock()

class MenuSystem:
    def __init__(self, data_dir:Path, screen, font_large, font_medium):
        self.__screen = screen
        self.__data_dir = data_dir
        self.__font_large = font_large
        self.__font_medium = font_medium
    


    def load_profiles(self):
        """Scans the data directory for existing .xlsx files."""
        try:
            # We only want files, not directories, and only .xlsx files
            profile_files = [f for f in os.listdir(self.__data_dir) if f.endswith('.xlsx') and os.path.isfile(self.__data_dir / f)]
            # Return only the filenames without the extension
            return [Path(f).stem for f in profile_files]
        except FileNotFoundError:
            # Ensure the data directory exists
            self.__data_dir.mkdir(exist_ok=True)
            return []

    def draw_button(self, surface, text, rect, color, text_color=WHITE, font=None):
        """Draws a clickable button."""
        if font is None:
            font = self.__font_medium
        pygame.draw.rect(surface, color, rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=5)
        
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
        return rect # Return the rect in case it's used for click detection

    def get_input_box(self, x, y, width, height, current_text):
        """Draws a simple text input box for the New Profile screen."""
        input_box_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.__screen, (50, 50, 50), input_box_rect, border_radius=5)
        pygame.draw.rect(self.__screen, WHITE, input_box_rect, 2, border_radius=5)
        
        text_surface = self.__font_medium.render(current_text, True, WHITE)
        text_rect = text_surface.get_rect(midleft=(x + 10, y + height // 2))
        self.__screen.blit(text_surface, text_rect)
        return input_box_rect

    def profile_menu(self):
        """Displays the profile selection menu at startup."""
        
        menu_running = True
        profiles = self.load_profiles()
        
        # Menu States: 'main' or 'new_profile'
        menu_state = 'main' 
        new_profile_input = ""
        input_active = True
        
        # Calculate button layout
        BUTTON_WIDTH = 300
        BUTTON_HEIGHT = 50
        START_Y = SCREEN_HEIGHT // 2 - (len(profiles) // 2) * (BUTTON_HEIGHT + 10)
        
        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if menu_state == 'main':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        
                        # Check for 'Create New Profile' button
                        create_button_y = START_Y + len(profiles) * (BUTTON_HEIGHT + 10)
                        create_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, create_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                        if create_button_rect.collidepoint(mouse_x, mouse_y):
                            menu_state = 'new_profile'
                            new_profile_input = ""
                        
                        # Check for existing profile buttons
                        for i, profile_name in enumerate(profiles):
                            y = START_Y + i * (BUTTON_HEIGHT + 10)
                            rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, y, BUTTON_WIDTH, BUTTON_HEIGHT)
                            if rect.collidepoint(mouse_x, mouse_y):
                                print(f"Loading profile: {profile_name}")
                                # --- LOAD PROFILE ---
                                return profile_name
                
                elif menu_state == 'new_profile':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        
                        # Input box rect
                        input_box_x = SCREEN_WIDTH // 2 - 200
                        input_box_y = SCREEN_HEIGHT // 2
                        input_box_rect = pygame.Rect(input_box_x, input_box_y, 400, 50)
                        
                        # Back button rect
                        back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, input_box_y + 100, 150, 50)
                        
                        # Create button rect
                        create_confirm_rect = pygame.Rect(SCREEN_WIDTH // 2 + 50, input_box_y + 100, 150, 50)
                        
                        if back_button_rect.collidepoint(mouse_x, mouse_y):
                            menu_state = 'main'
                            profiles = self.load_profiles() # Refresh profiles list
                        elif create_confirm_rect.collidepoint(mouse_x, mouse_y) and new_profile_input:
                            # --- CREATE PROFILE ---
                            print(f"Creating profile: {new_profile_input}")
                            #### LOGIC TO GENERATE NEW PROFILE FILE
                            df_focus = pd.DataFrame({
                                1:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                2:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                3:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                4:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                5:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                6:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                7:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                8:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                9:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                10:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                11:['X','X','X','X','X','X','X','X','X','X','X','X'],
                                12:['X','X','X','X','X','X','X','X','X','X','X','X']
                            }, index=range(1,13))
                            df_performance = pd.DataFrame()
                            for first_term in range(1,13,1):
                                for second_term in range(1,13,1):
                                    df_temp = pd.DataFrame({
                                        'First':[first_term],
                                        'Second':[second_term],
                                        'Times Occurred':[None],
                                        'Times Wrong':[None],
                                        'Times Right':[None],
                                        'Avg Time to Answer':[None],
                                        'Last Time to Answer':[None],
                                    })
                                    df_performance = pd.concat([df_performance,df_temp])
                            df_performance = df_performance.reset_index(drop=True)

                            today = datetime.datetime.now().strftime('%Y-%m-%d')
                            df_daily_log = pd.DataFrame({'Date':[today],'Duration (Minutes)':[0]})

                            with pd.ExcelWriter(self.__data_dir.joinpath(f'{new_profile_input}.xlsx'), engine='openpyxl', mode='w') as writer:
                                df_focus.to_excel(writer,sheet_name = 'Focus Problems',index = True)
                                df_performance.to_excel(writer, sheet_name='Performance', index=False)
                                df_daily_log.to_excel(writer, sheet_name='Daily Log', index=False)

                            return new_profile_input
                        
                        # Check if the input box was clicked
                        if input_box_rect.collidepoint(mouse_x, mouse_y):
                            input_active = True
                        else:
                            input_active = False

                    if event.type == pygame.KEYDOWN and input_active:
                        if event.key == pygame.K_RETURN and new_profile_input:
                            # --- CREATE PROFILE on Enter ---
                            print(f"Creating profile: {new_profile_input}")
                            return new_profile_input
                        elif event.key == pygame.K_BACKSPACE:
                            new_profile_input = new_profile_input[:-1]
                        elif event.unicode.isalnum() or event.unicode in [' ', '_', '-']:
                            if len(new_profile_input) < 20: # Limit length
                                new_profile_input += event.unicode


            # --- Drawing Menu ---
            self.__screen.fill(BLACK)
            
            title_text = self.__font_large.render("Multiplication Asteroids", True, YELLOW)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.__screen.blit(title_text, title_rect)
            
            if menu_state == 'main':
                menu_title = self.__font_medium.render("Select Profile or Create New", True, WHITE)
                menu_title_rect = menu_title.get_rect(center=(SCREEN_WIDTH // 2, 180))
                self.__screen.blit(menu_title, menu_title_rect)
                
                # Draw existing profile buttons
                for i, profile_name in enumerate(profiles):
                    y = START_Y + i * (BUTTON_HEIGHT + 10)
                    rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, y, BUTTON_WIDTH, BUTTON_HEIGHT)
                    self.draw_button(self.__screen, profile_name, rect, BLUE)
                
                # Draw 'Create New Profile' button
                create_button_y = START_Y + len(profiles) * (BUTTON_HEIGHT + 10)
                create_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, create_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                self.draw_button(self.__screen, "Create New Profile", create_button_rect, GREEN, text_color=BLACK)
                
            elif menu_state == 'new_profile':
                instruction_text = self.__font_medium.render("Enter New Profile Name (e.g., JaneDoe)", True, WHITE)
                instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                self.__screen.blit(instruction_text, instruction_rect)
                
                # Draw input box
                input_box_x = SCREEN_WIDTH // 2 - 200
                input_box_y = SCREEN_HEIGHT // 2
                self.get_input_box(input_box_x, input_box_y, 400, 50, new_profile_input + ("|" if input_active else ""))
                
                # Draw Back button
                back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, input_box_y + 100, 150, 50)
                self.draw_button(self.__screen, "Back", back_button_rect, RED)
                
                # Draw Create button
                create_confirm_rect = pygame.Rect(SCREEN_WIDTH // 2 + 50, input_box_y + 100, 150, 50)
                confirm_color = GREEN if new_profile_input else (50, 50, 50)
                self.draw_button(self.__screen, "Create", create_confirm_rect, confirm_color)

            
            pygame.display.flip()
            clock.tick(60)

        # Should not be reached, but just in case
        return None
