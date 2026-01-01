# operator_panel_module.py

import pygame
import sys
import time

# --- Constants ---
PANEL_WIDTH = 800
PANEL_HEIGHT = 500
PANEL_POS_X = (1280 - PANEL_WIDTH) // 2
PANEL_POS_Y = (720 - PANEL_HEIGHT) // 2

BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 150, 255)
MESSAGE_COLOR = (255, 255, 0) # Yellow for messages
ERROR_COLOR = (255, 50, 50) # Red for errors

FONT_PATH = "fonts/Montserrat-Bold.ttf"
FONT_SIZE_TITLE = 36
FONT_SIZE_MENU = 28
FONT_SIZE_ITEM_NUMBER = 24
FONT_SIZE_MESSAGE = 24
FONT_SIZE_INPUT = 32

CURRENT_ACCESS_CODE = "7777"

# --- Menu Definitions ---
MENU_ITEMS = [
    "Security Settings", # Changed from "Change Control Panel Access Code"
    "Set Random Music Genres",
    "Turn Random Music On/Off",
    "Turn Credits On/Off",
    "For Future Use",
    "More Selections",
    "Return To Jukebox",
]

SECURITY_MENU_ITEMS = [
    "Change Access Code",
    "Back To Control Panel",
    "Exit To Jukebox",
]

# --- Drawing Functions ---
def draw_menu(surface, title_font, menu_font, item_num_font, title, items, highlighted_index):
    """Generic function to draw a menu screen."""
    surface.fill(BACKGROUND_COLOR)
    
    # Draw title
    title_text = title_font.render(title, True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 50))
    surface.blit(title_text, title_rect)

    # Draw menu items
    for i, item in enumerate(items):
        item_number_text = item_num_font.render(f"{i + 1}.", True, TEXT_COLOR)
        item_number_rect = item_number_text.get_rect(topleft=(50, 120 + i * 40))
        surface.blit(item_number_text, item_number_rect)

        color = HIGHLIGHT_COLOR if i == highlighted_index else TEXT_COLOR
        menu_item_text = menu_font.render(item, True, color)
        menu_item_rect = menu_item_text.get_rect(topleft=(item_number_rect.right + 10, 120 + i * 40))
        surface.blit(menu_item_text, menu_item_rect)

def draw_input_screen(surface, title_font, input_font, prompt, code_buffer):
    """Draws the screen for entering a code."""
    surface.fill(BACKGROUND_COLOR)
    
    # Draw title
    title_text = title_font.render("Change Access Code", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 50))
    surface.blit(title_text, title_rect)

    # Draw prompt
    prompt_text = input_font.render(prompt, True, TEXT_COLOR)
    prompt_rect = prompt_text.get_rect(center=(PANEL_WIDTH // 2, 150))
    surface.blit(prompt_text, prompt_rect)

    # Draw code input display (e.g., ****)
    display_code = "*" * len(code_buffer)
    code_text = input_font.render(display_code, True, HIGHLIGHT_COLOR)
    code_rect = code_text.get_rect(center=(PANEL_WIDTH // 2, 200))
    surface.blit(code_text, code_rect)

def draw_message(surface, message_font, text, color=MESSAGE_COLOR):
    """Draw a temporary message at the bottom of the panel."""
    message_text = message_font.render(text, True, color)
    message_rect = message_text.get_rect(center=(PANEL_WIDTH // 2, PANEL_HEIGHT - 40))
    surface.blit(message_text, message_rect)

# --- Main function for the operator panel ---
def display_operator_panel(screen):
    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        menu_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        item_num_font = pygame.font.Font(FONT_PATH, FONT_SIZE_ITEM_NUMBER)
        message_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MESSAGE)
        input_font = pygame.font.Font(FONT_PATH, FONT_SIZE_INPUT)
    except Exception:
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        menu_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        item_num_font = pygame.font.SysFont(None, FONT_SIZE_ITEM_NUMBER)
        message_font = pygame.font.SysFont(None, FONT_SIZE_MESSAGE)
        input_font = pygame.font.SysFont(None, FONT_SIZE_INPUT)

    # State management
    panel_state = 'main'  # Can be 'main', 'security', or 'enter_current_code'
    highlighted_item_index = 0
    message = None
    message_timer = 0
    message_color = MESSAGE_COLOR
    
    code_buffer = []

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            # Clear message on any key press, except in the 'enter_current_code' state
            if message and panel_state != 'enter_current_code':
                message = None
                message_timer = 0

            if event.key == pygame.K_ESCAPE:
                if panel_state == 'enter_current_code':
                    panel_state = 'security' # Go back to security menu
                    highlighted_item_index = 0
                    code_buffer = []
                else:
                    return "Return To Jukebox"

            # --- Main Menu State Logic ---
            if panel_state == 'main':
                if event.key == pygame.K_UP:
                    highlighted_item_index = (highlighted_item_index - 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    highlighted_item_index = (highlighted_item_index + 1) % len(MENU_ITEMS)
                elif event.key in (pygame.K_1, pygame.K_KP_1):
                    panel_state = 'security'
                    highlighted_item_index = 0 # Reset for new menu
                elif event.key == pygame.K_s:
                    selected_item = MENU_ITEMS[highlighted_item_index]
                    if selected_item == "Security Settings":
                        panel_state = 'security'
                        highlighted_item_index = 0
                    else:
                        return selected_item
                # Numbered navigation for other items
                elif event.key in (pygame.K_2, pygame.K_KP_2): return MENU_ITEMS[1]
                elif event.key in (pygame.K_3, pygame.K_KP_3): return MENU_ITEMS[2]
                elif event.key in (pygame.K_4, pygame.K_KP_4): return MENU_ITEMS[3]
                elif event.key in (pygame.K_5, pygame.K_KP_5): return MENU_ITEMS[4]
                elif event.key in (pygame.K_6, pygame.K_KP_6): return MENU_ITEMS[5]
                elif event.key in (pygame.K_7, pygame.K_KP_7): return MENU_ITEMS[6]


            # --- Security Menu State Logic ---
            elif panel_state == 'security':
                if event.key == pygame.K_UP:
                    highlighted_item_index = (highlighted_item_index - 1) % len(SECURITY_MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    highlighted_item_index = (highlighted_item_index + 1) % len(SECURITY_MENU_ITEMS)
                elif event.key in (pygame.K_1, pygame.K_KP_1): highlighted_item_index = 0
                elif event.key in (pygame.K_2, pygame.K_KP_2): highlighted_item_index = 1
                elif event.key in (pygame.K_3, pygame.K_KP_3): highlighted_item_index = 2
                elif event.key == pygame.K_s:
                    selected_item = SECURITY_MENU_ITEMS[highlighted_item_index]
                    if selected_item == "Change Access Code":
                        panel_state = 'enter_current_code'
                        code_buffer = []
                        message = None # Clear any previous messages
                    elif selected_item == "Back To Control Panel":
                        panel_state = 'main'
                        highlighted_item_index = 0 # Reset to top of main menu
                    elif selected_item == "Exit To Jukebox":
                        return "Return To Jukebox"

            # --- Enter Current Code State Logic ---
            elif panel_state == 'enter_current_code':
                num_map = {
                    pygame.K_0: '0', pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4',
                    pygame.K_5: '5', pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8', pygame.K_9: '9',
                    pygame.K_KP_0: '0', pygame.K_KP_1: '1', pygame.K_KP_2: '2', pygame.K_KP_3: '3', pygame.K_KP_4: '4',
                    pygame.K_KP_5: '5', pygame.K_KP_6: '6', pygame.K_KP_7: '7', pygame.K_KP_8: '8', pygame.K_KP_9: '9'
                }
                if event.key in num_map and len(code_buffer) < 4:
                    code_buffer.append(num_map[event.key])
                elif event.key == pygame.K_BACKSPACE and len(code_buffer) > 0:
                    code_buffer.pop()

                # Check code when 4 digits are entered
                if len(code_buffer) == 4:
                    entered_code = "".join(code_buffer)
                    if entered_code == CURRENT_ACCESS_CODE:
                        print("Correct code entered. Returning to jukebox.")
                        return "Return To Jukebox"
                    else:
                        message = "Invalid Code. Try again."
                        message_color = ERROR_COLOR
                        message_timer = time.time()
                        code_buffer = []

        # --- Drawing ---
        if panel_state == 'main':
            draw_menu(panel_surface, title_font, menu_font, item_num_font, "Operator Control Panel", MENU_ITEMS, highlighted_item_index)
        elif panel_state == 'security':
            draw_menu(panel_surface, title_font, menu_font, item_num_font, "Security Settings", SECURITY_MENU_ITEMS, highlighted_item_index)
        elif panel_state == 'enter_current_code':
            draw_input_screen(panel_surface, title_font, input_font, "Enter Current 4-Digit Code:", code_buffer)

        # Display message if it exists and hasn't expired
        if message and (time.time() - message_timer < 3):
            draw_message(panel_surface, message_font, message, message_color)
        else:
            message = None

        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01)