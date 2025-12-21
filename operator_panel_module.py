
import pygame
import sys

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

def show_operator_panel(screen):
    """
    Displays the operator control panel as a modal-like window.
    It takes over the event loop until it's explicitly closed.
    """
    panel_width = 800
    panel_height = 600
    panel_x = (screen.get_width() - panel_width) // 2
    panel_y = (screen.get_height() - panel_height) // 2

    # Create a surface for the panel
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_surface.fill((0, 0, 0, 200)) # Semi-transparent black background

    panel_font_title = pygame.font.Font(None, 60)
    panel_font_exit = pygame.font.Font(None, 40)

    title_text_surface = panel_font_title.render("Operator Control Panel", True, WHITE)
    title_text_rect = title_text_surface.get_rect(center=(panel_width // 2, 50))

    exit_button_text_surface = panel_font_exit.render("EXIT (ESC)", True, WHITE)
    exit_button_rect = exit_button_text_surface.get_rect(center=(panel_width // 2, panel_height - 50))
    exit_button_padding = 20
    exit_button_bg_rect = exit_button_rect.inflate(exit_button_padding * 2, exit_button_padding * 2)

    panel_active = True
    while panel_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    panel_active = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Adjust mouse position to panel's coordinate system
                    mouse_x, mouse_y = event.pos
                    relative_mouse_x = mouse_x - panel_x
                    relative_mouse_y = mouse_y - panel_y

                    if exit_button_bg_rect.collidepoint(relative_mouse_x, relative_mouse_y):
                        panel_active = False

        # Clear panel surface
        panel_surface.fill((0, 0, 0, 200)) # Semi-transparent black background

        # Draw exit button background
        pygame.draw.rect(panel_surface, GRAY, exit_button_bg_rect, border_radius=10)
        pygame.draw.rect(panel_surface, WHITE, exit_button_bg_rect, 3, border_radius=10) # White border

        # Draw title and exit text on the panel surface
        panel_surface.blit(title_text_surface, title_text_rect)
        panel_surface.blit(exit_button_text_surface, exit_button_rect)

        # Blit the panel surface onto the main screen
        screen.blit(panel_surface, (panel_x, panel_y))
        pygame.display.flip()

if __name__ == '__main__':
    # For testing the panel directly
    pygame.init()
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Operator Panel Test")

    # Fill background for context
    screen.fill((50, 50, 150)) # A blue background for testing

    show_operator_panel(screen)
    pygame.quit()
    sys.exit()
