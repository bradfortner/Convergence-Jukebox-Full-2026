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

FONT_PATH = "fonts/Montserrat-Bold.ttf"
FONT_SIZE_TITLE = 36
FONT_SIZE_MENU = 28
FONT_SIZE_ITEM_NUMBER = 24
FONT_SIZE_MESSAGE = 24

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

def draw_message(surface, message_font, text):
    """Draw a temporary message at the bottom of the panel."""
    message_text = message_font.render(text, True, MESSAGE_COLOR)
    message_rect = message_text.get_rect(center=(PANEL_WIDTH // 2, PANEL_HEIGHT - 40))
    surface.blit(message_text, message_rect)

# --- Change Access Code Function ---
def change_access_code(screen, current_code):
    """Three-step workflow to change the operator access code.

    Args:
        screen: Pygame screen surface
        current_code: List of strings representing current access code (e.g., ['2', '1', '2', '4'])

    Returns:
        List of strings representing new code if successful, None if cancelled or failed
    """
    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        prompt_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        input_font = pygame.font.Font(FONT_PATH, 48)  # Larger font for code display
        message_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MESSAGE)
    except Exception:
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        prompt_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        input_font = pygame.font.SysFont(None, 48)
        message_font = pygame.font.SysFont(None, FONT_SIZE_MESSAGE)

    # Step 1: Verify current access code
    code_buffer = []
    step = 1  # 1 = verify current, 2 = enter new, 3 = confirm new
    new_code_first = []
    error_message = None
    error_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            # Clear error message on any key press
            if error_message:
                error_message = None
                error_timer = 0

            # ESC to cancel
            if event.key == pygame.K_ESCAPE:
                return None

            # Number keys 1-7 only
            num_map = {
                pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3',
                pygame.K_4: '4', pygame.K_5: '5', pygame.K_6: '6', pygame.K_7: '7',
                pygame.K_KP_1: '1', pygame.K_KP_2: '2', pygame.K_KP_3: '3',
                pygame.K_KP_4: '4', pygame.K_KP_5: '5', pygame.K_KP_6: '6', pygame.K_KP_7: '7'
            }

            if event.key in num_map and len(code_buffer) < 4:
                code_buffer.append(num_map[event.key])

            # Backspace or C to delete last digit
            elif event.key in (pygame.K_BACKSPACE, pygame.K_c) and len(code_buffer) > 0:
                code_buffer.pop()

            # S to confirm when 4 digits entered
            elif event.key == pygame.K_s and len(code_buffer) == 4:
                if step == 1:
                    # Verify current code
                    if code_buffer == current_code:
                        # Correct! Move to step 2
                        step = 2
                        code_buffer = []
                    else:
                        # Incorrect code
                        error_message = "Incorrect Code - Try Again"
                        error_timer = time.time()
                        code_buffer = []

                elif step == 2:
                    # Save first entry of new code
                    new_code_first = code_buffer[:]
                    step = 3
                    code_buffer = []

                elif step == 3:
                    # Confirm new code matches
                    if code_buffer == new_code_first:
                        # Success! Return new code
                        return new_code_first
                    else:
                        # Codes don't match
                        error_message = "Codes Don't Match - Try Again"
                        error_timer = time.time()
                        step = 2  # Go back to step 2
                        code_buffer = []
                        new_code_first = []

        # --- Drawing ---
        panel_surface.fill(BACKGROUND_COLOR)

        # Draw title
        title_text = title_font.render("Change Access Code", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 50))
        panel_surface.blit(title_text, title_rect)

        # Draw prompt based on step
        if step == 1:
            prompt = "Enter Current Access Code"
        elif step == 2:
            prompt = "Enter New Code (4 Digits, 1-7 Only)"
        elif step == 3:
            prompt = "Confirm New Access Code"

        prompt_text = prompt_font.render(prompt, True, TEXT_COLOR)
        prompt_rect = prompt_text.get_rect(center=(PANEL_WIDTH // 2, 150))
        panel_surface.blit(prompt_text, prompt_rect)

        # Draw code entry (show asterisks or digits)
        code_display = " ".join(["*" if i < len(code_buffer) else "_" for i in range(4)])
        code_text = input_font.render(code_display, True, HIGHLIGHT_COLOR)
        code_rect = code_text.get_rect(center=(PANEL_WIDTH // 2, 250))
        panel_surface.blit(code_text, code_rect)

        # Draw instructions
        instructions = "Press Digits 1 thru 7 | CORRECT to delete | SELECT to submit"
        inst_text = message_font.render(instructions, True, TEXT_COLOR)
        inst_rect = inst_text.get_rect(center=(PANEL_WIDTH // 2, 350))
        panel_surface.blit(inst_text, inst_rect)

        # Draw error message if exists and hasn't expired
        if error_message and (time.time() - error_timer < 3):
            error_text = message_font.render(error_message, True, MESSAGE_COLOR)
            error_rect = error_text.get_rect(center=(PANEL_WIDTH // 2, PANEL_HEIGHT - 40))
            panel_surface.blit(error_text, error_rect)

        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01)

    return None

# --- Main function for the operator panel ---
def display_operator_panel(screen, current_access_code=None):
    """Display operator panel with menu options.

    Args:
        screen: Pygame screen surface
        current_access_code: List of strings representing current access code (optional)

    Returns:
        String indicating selected action, or tuple ('change_code', new_code) if code changed
    """
    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        menu_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        item_num_font = pygame.font.Font(FONT_PATH, FONT_SIZE_ITEM_NUMBER)
        message_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MESSAGE)
    except Exception:
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        menu_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        item_num_font = pygame.font.SysFont(None, FONT_SIZE_ITEM_NUMBER)
        message_font = pygame.font.SysFont(None, FONT_SIZE_MESSAGE)

    # State management
    panel_state = 'main'  # Can be 'main' or 'security'
    highlighted_item_index = 0
    message = None
    message_timer = 0

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            # Clear message on any key press
            if message:
                message = None
                message_timer = 0

            if event.key == pygame.K_ESCAPE:
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
                elif event.key in (pygame.K_2, pygame.K_KP_2):
                    return MENU_ITEMS[1]
                elif event.key in (pygame.K_3, pygame.K_KP_3):
                    return MENU_ITEMS[2]
                elif event.key in (pygame.K_4, pygame.K_KP_4):
                    return MENU_ITEMS[3]
                elif event.key in (pygame.K_5, pygame.K_KP_5):
                    return MENU_ITEMS[4]
                elif event.key in (pygame.K_6, pygame.K_KP_6):
                    return MENU_ITEMS[5]
                elif event.key in (pygame.K_7, pygame.K_KP_7):
                    return MENU_ITEMS[6]


            # --- Security Menu State Logic ---
            elif panel_state == 'security':
                if event.key == pygame.K_UP:
                    highlighted_item_index = (highlighted_item_index - 1) % len(SECURITY_MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    highlighted_item_index = (highlighted_item_index + 1) % len(SECURITY_MENU_ITEMS)
                elif event.key in (pygame.K_1, pygame.K_KP_1):
                    highlighted_item_index = 0
                elif event.key in (pygame.K_2, pygame.K_KP_2):
                    highlighted_item_index = 1
                elif event.key in (pygame.K_3, pygame.K_KP_3):
                    highlighted_item_index = 2
                elif event.key == pygame.K_s:
                    selected_item = SECURITY_MENU_ITEMS[highlighted_item_index]
                    if selected_item == "Change Access Code":
                        if current_access_code:
                            new_code = change_access_code(screen, current_access_code)
                            if new_code:
                                # Return tuple indicating code change
                                return ('change_code', new_code)
                            else:
                                # User cancelled, go back to security menu
                                pass
                        else:
                            message = "Error: No access code loaded."
                            message_timer = time.time()
                    elif selected_item == "Back To Control Panel":
                        panel_state = 'main'
                        highlighted_item_index = 0 # Reset to top of main menu
                    elif selected_item == "Exit To Jukebox":
                        return "Return To Jukebox"

        # --- Drawing ---
        if panel_state == 'main':
            draw_menu(panel_surface, title_font, menu_font, item_num_font, "Operator Control Panel", MENU_ITEMS, highlighted_item_index)
        elif panel_state == 'security':
            draw_menu(panel_surface, title_font, menu_font, item_num_font, "Security Settings", SECURITY_MENU_ITEMS, highlighted_item_index)

        # Display message if it exists and hasn't expired
        if message and (time.time() - message_timer < 3):
            draw_message(panel_surface, message_font, message)
        else:
            message = None

        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01)