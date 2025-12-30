# operator_panel_module.py

import pygame
import sys
import time

# --- Constants for raspi-config style display ---
PANEL_WIDTH = 800
PANEL_HEIGHT = 500
PANEL_POS_X = (1280 - PANEL_WIDTH) // 2
PANEL_POS_Y = (720 - PANEL_HEIGHT) // 2

BACKGROUND_COLOR = (0, 0, 0) # Black background
TEXT_COLOR = (255, 255, 255) # White text
HIGHLIGHT_COLOR = (0, 150, 255) # Blue highlight

FONT_PATH = "fonts/Montserrat-Bold.ttf" # Assuming this font exists
FONT_SIZE_TITLE = 36
FONT_SIZE_MENU = 28
FONT_SIZE_ITEM_NUMBER = 24

MENU_ITEMS = [
    "Change Control Panel Access Code",
    "Set Random Music Genres",
    "For Future Use",
    "For Future Use",
    "For Future Use",
    "More Selections",
    "Return To Jukebox",
]

# --- Main function for the operator panel ---
def display_operator_panel(screen):
    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))
    panel_surface.fill(BACKGROUND_COLOR)

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        menu_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        item_num_font = pygame.font.Font(FONT_PATH, FONT_SIZE_ITEM_NUMBER)
    except Exception:
        # Fallback to default font if custom font not found
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        menu_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        item_num_font = pygame.font.SysFont(None, FONT_SIZE_ITEM_NUMBER)


    title_text = title_font.render("Operator Control Panel", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 50))
    panel_surface.blit(title_text, title_rect)

    # Initial highlight
    highlighted_item_index = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None # Exit panel without selection
                elif event.key == pygame.K_UP:
                    highlighted_item_index = (highlighted_item_index - 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    highlighted_item_index = (highlighted_item_index + 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_s: # S key for selection
                    return MENU_ITEMS[highlighted_item_index] # Return selected item
                elif pygame.K_1 <= event.key <= pygame.K_7: # Number keys 1-7 for direct selection
                    selected_num = int(pygame.key.name(event.key))
                    if 1 <= selected_num <= len(MENU_ITEMS):
                        return MENU_ITEMS[selected_num - 1] # Return selected item


        # Redraw panel content
        panel_surface.fill(BACKGROUND_COLOR) # Clear previous frame
        panel_surface.blit(title_text, title_rect)

        # Render menu items
        for i, item in enumerate(MENU_ITEMS):
            item_number_text = item_num_font.render(f"{i + 1}.", True, TEXT_COLOR)
            item_number_rect = item_number_text.get_rect(topleft=(50, 120 + i * 40))
            panel_surface.blit(item_number_text, item_number_rect)

            color = HIGHLIGHT_COLOR if i == highlighted_item_index else TEXT_COLOR
            menu_item_text = menu_font.render(item, True, color)
            menu_item_rect = menu_item_text.get_rect(topleft=(item_number_rect.right + 10, 120 + i * 40))
            panel_surface.blit(menu_item_text, menu_item_rect)


        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01) # Small delay to prevent busy-waiting if event queue is empty