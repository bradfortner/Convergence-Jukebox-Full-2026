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
    "Select Year Range",
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
# --- Genre Selection Function ---
def select_random_music_genres(screen, song_list, genre_flags_file_path):
    """Display genre selection screen with checkboxes.

    Args:
        screen: Pygame screen surface
        song_list: List of song dictionaries from MusicMasterSongList
        genre_flags_file_path: Path to GenreFlagsList.txt

    Returns:
        True if genres were saved, False if cancelled
    """
    import json

    # Extract all unique genres from song list
    all_genres = set()
    excluded_values = {'n/a', 'none', 'norandom', 'image', 'noimage'}  # Values to exclude (case-insensitive)

    for song in song_list:
        comment = song.get('comment', '')
        if comment:
            genre_tags = comment.split()
            for tag in genre_tags:
                cleaned_tag = tag.strip()
                # Exclude empty strings, "N/A", and "None" (case-insensitive)
                if cleaned_tag and cleaned_tag.lower() not in excluded_values:
                    all_genres.add(cleaned_tag)

    # Sort genres alphabetically
    sorted_genres = sorted(all_genres)

    if not sorted_genres:
        print("[ERROR] No genres found in music collection")
        return False

    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        genre_font = pygame.font.Font(FONT_PATH, 22)  # Slightly smaller for genre list
        button_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        instruction_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MESSAGE)
    except Exception:
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        genre_font = pygame.font.SysFont(None, 22)
        button_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        instruction_font = pygame.font.SysFont(None, FONT_SIZE_MESSAGE)

    # State variables
    highlighted_index = 0
    scroll_offset = 0
    max_visible_items = 8  # Show 8 genres at a time (reduced to make room for button)

    # Total items = all genres + 1 save button
    total_items = len(sorted_genres) + 1
    save_button_index = len(sorted_genres)  # Save button is last item

    # Track checked genres in order of selection (FIFO queue)
    checked_genres = []  # Max 4 items

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            # C key or ESC = Cancel
            if event.key in (pygame.K_c, pygame.K_ESCAPE):
                print("[GENRE SELECT] Cancelled by user")
                return False

            # S key = SELECT - Toggle checkbox OR activate Save button
            elif event.key == pygame.K_s:
                if highlighted_index == save_button_index:
                    # Save button is highlighted - save and exit
                    save_list = ["null", "null", "null", "null"]
                    for i, genre in enumerate(checked_genres):
                        if i < 4:
                            save_list[i] = genre

                    try:
                        with open(genre_flags_file_path, 'w') as f:
                            json.dump(save_list, f)
                        print(f"[GENRE SELECT] Saved genres: {checked_genres}")
                        return True
                    except Exception as e:
                        print(f"[ERROR] Failed to save GenreFlagsList.txt: {e}")
                        return False
                else:
                    # A genre is highlighted - toggle checkbox
                    selected_genre = sorted_genres[highlighted_index]

                    if selected_genre in checked_genres:
                        # Uncheck
                        checked_genres.remove(selected_genre)
                    else:
                        # Check
                        if len(checked_genres) >= 4:
                            # Remove oldest (first in list)
                            removed = checked_genres.pop(0)
                            print(f"[GENRE SELECT] Auto-unchecked oldest: {removed}")
                        checked_genres.append(selected_genre)

            # UP arrow - move highlight up
            elif event.key == pygame.K_UP:
                if highlighted_index > 0:
                    highlighted_index -= 1
                    # Adjust scroll if needed (only for genres, not button)
                    if highlighted_index < save_button_index:
                        if highlighted_index < scroll_offset:
                            scroll_offset = highlighted_index

            # DOWN arrow - move highlight down
            elif event.key == pygame.K_DOWN:
                if highlighted_index < total_items - 1:
                    highlighted_index += 1
                    # Adjust scroll if needed (only for genres, not button)
                    if highlighted_index < save_button_index:
                        if highlighted_index >= scroll_offset + max_visible_items:
                            scroll_offset = highlighted_index - max_visible_items + 1

        # --- Drawing ---
        panel_surface.fill(BACKGROUND_COLOR)

        # Draw title
        title_text = title_font.render("Set Random Music Genres", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 40))
        panel_surface.blit(title_text, title_rect)

        # Draw genre count info
        count_text = instruction_font.render(f"Selected: {len(checked_genres)}/4", True, HIGHLIGHT_COLOR)
        count_rect = count_text.get_rect(center=(PANEL_WIDTH // 2, 80))
        panel_surface.blit(count_text, count_rect)

        # Draw genre list with checkboxes
        y_pos = 120
        visible_genres = sorted_genres[scroll_offset:scroll_offset + max_visible_items]

        for i, genre in enumerate(visible_genres):
            actual_index = scroll_offset + i
            is_highlighted = (actual_index == highlighted_index)
            is_checked = genre in checked_genres

            # Draw checkbox
            checkbox_x = 50
            checkbox_size = 20
            checkbox_rect = pygame.Rect(checkbox_x, y_pos, checkbox_size, checkbox_size)

            # Checkbox border
            border_color = HIGHLIGHT_COLOR if is_highlighted else TEXT_COLOR
            pygame.draw.rect(panel_surface, border_color, checkbox_rect, 2)

            # Checkbox fill if checked
            if is_checked:
                inner_rect = pygame.Rect(checkbox_x + 4, y_pos + 4, checkbox_size - 8, checkbox_size - 8)
                pygame.draw.rect(panel_surface, HIGHLIGHT_COLOR, inner_rect)

            # Draw genre name
            text_color = HIGHLIGHT_COLOR if is_highlighted else TEXT_COLOR
            genre_text = genre_font.render(genre, True, text_color)
            panel_surface.blit(genre_text, (checkbox_x + checkbox_size + 10, y_pos))

            y_pos += 30

        # Draw scroll indicators
        if scroll_offset > 0:
            up_arrow = instruction_font.render("^ More above ^", True, TEXT_COLOR)
            panel_surface.blit(up_arrow, (PANEL_WIDTH // 2 - up_arrow.get_width() // 2, 100))

        if scroll_offset + max_visible_items < len(sorted_genres):
            down_arrow = instruction_font.render("v More below v", True, TEXT_COLOR)
            panel_surface.blit(down_arrow, (PANEL_WIDTH // 2 - down_arrow.get_width() // 2, y_pos + 10))

        # Draw "Save Genres" button at bottom
        button_y = PANEL_HEIGHT - 100
        save_button_highlighted = (highlighted_index == save_button_index)
        button_color = HIGHLIGHT_COLOR if save_button_highlighted else TEXT_COLOR

        save_button_text = button_font.render("Save Genres", True, button_color)
        save_button_rect = save_button_text.get_rect(center=(PANEL_WIDTH // 2, button_y))
        panel_surface.blit(save_button_text, save_button_rect)

        # Draw instructions at bottom
        instructions = [
            "UP/DOWN: Navigate | SELECT: Check/Uncheck or Save",
            "CORRECT: Cancel"
        ]

        inst_y = PANEL_HEIGHT - 60
        for instruction in instructions:
            inst_text = instruction_font.render(instruction, True, TEXT_COLOR)
            inst_rect = inst_text.get_rect(center=(PANEL_WIDTH // 2, inst_y))
            panel_surface.blit(inst_text, inst_rect)
            inst_y += 25

        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01)

    return False

# --- Toggle Random Music Function ---
def toggle_random_music(screen, current_setting):
    """Display random music toggle screen with checkbox.

    Args:
        screen: Pygame screen surface
        current_setting: Boolean - True if random music is enabled, False otherwise

    Returns:
        Boolean or None - New setting if saved, None if cancelled
    """
    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        label_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        button_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        instruction_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MESSAGE)
    except Exception:
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        label_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        button_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        instruction_font = pygame.font.SysFont(None, FONT_SIZE_MESSAGE)

    # State variables
    random_music_enabled = current_setting  # Local copy to modify
    highlighted_index = 0  # 0 = checkbox, 1 = save button
    total_items = 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            # C key or ESC = Cancel
            if event.key in (pygame.K_c, pygame.K_ESCAPE):
                print("[RANDOM MUSIC] Cancelled by user")
                return None

            # S key = SELECT - Toggle checkbox OR save
            elif event.key == pygame.K_s:
                if highlighted_index == 0:
                    # Checkbox is highlighted - toggle it
                    random_music_enabled = not random_music_enabled
                    print(f"[RANDOM MUSIC] Toggled to: {random_music_enabled}")
                elif highlighted_index == 1:
                    # Save button is highlighted - save and exit
                    print(f"[RANDOM MUSIC] Saving setting: {random_music_enabled}")
                    return random_music_enabled

            # UP arrow - move highlight up
            elif event.key == pygame.K_UP:
                if highlighted_index > 0:
                    highlighted_index -= 1

            # DOWN arrow - move highlight down
            elif event.key == pygame.K_DOWN:
                if highlighted_index < total_items - 1:
                    highlighted_index += 1

        # --- Drawing ---
        panel_surface.fill(BACKGROUND_COLOR)

        # Draw title
        title_text = title_font.render("Random Music Settings", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 50))
        panel_surface.blit(title_text, title_rect)

        # Draw checkbox and label
        checkbox_y = 150
        checkbox_x = 150
        checkbox_size = 30

        # Checkbox is item 0
        checkbox_highlighted = (highlighted_index == 0)

        # Draw checkbox
        checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        border_color = HIGHLIGHT_COLOR if checkbox_highlighted else TEXT_COLOR
        pygame.draw.rect(panel_surface, border_color, checkbox_rect, 3)

        # Checkbox fill if enabled
        if random_music_enabled:
            inner_rect = pygame.Rect(checkbox_x + 6, checkbox_y + 6, checkbox_size - 12, checkbox_size - 12)
            pygame.draw.rect(panel_surface, HIGHLIGHT_COLOR, inner_rect)

        # Draw label
        label_color = HIGHLIGHT_COLOR if checkbox_highlighted else TEXT_COLOR
        label_text = label_font.render("Play Random Music", True, label_color)
        panel_surface.blit(label_text, (checkbox_x + checkbox_size + 20, checkbox_y))

        # Draw explanation text
        if random_music_enabled:
            explain_text = "Random songs will play when no paid songs are queued"
        else:
            explain_text = "Only paid songs will play - jukebox silent when queue is empty"

        explain_font = instruction_font
        explain_render = explain_font.render(explain_text, True, TEXT_COLOR)
        explain_rect = explain_render.get_rect(center=(PANEL_WIDTH // 2, 250))
        panel_surface.blit(explain_render, explain_rect)

        # Draw "Save Settings" button at bottom
        button_y = PANEL_HEIGHT - 120
        save_button_highlighted = (highlighted_index == 1)
        button_color = HIGHLIGHT_COLOR if save_button_highlighted else TEXT_COLOR

        save_button_text = button_font.render("Save Settings", True, button_color)
        save_button_rect = save_button_text.get_rect(center=(PANEL_WIDTH // 2, button_y))
        panel_surface.blit(save_button_text, save_button_rect)

        # Draw instructions at bottom
        instructions = [
            "UP/DOWN: Navigate | SELECT: Toggle or Save",
            "CORRECT: Cancel"
        ]

        inst_y = PANEL_HEIGHT - 70
        for instruction in instructions:
            inst_text = instruction_font.render(instruction, True, TEXT_COLOR)
            inst_rect = inst_text.get_rect(center=(PANEL_WIDTH // 2, inst_y))
            panel_surface.blit(inst_text, inst_rect)
            inst_y += 25

        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01)

    return None

# --- Toggle Credits Function ---
def toggle_credits(screen, current_setting):
    """Display credits toggle screen with checkbox.

    Args:
        screen: Pygame screen surface
        current_setting: Boolean - True if credits are required, False otherwise

    Returns:
        Boolean or None - New setting if saved, None if cancelled
    """
    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        label_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        button_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        instruction_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MESSAGE)
    except Exception:
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        label_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        button_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        instruction_font = pygame.font.SysFont(None, FONT_SIZE_MESSAGE)

    # State variables
    credits_enabled = current_setting  # Local copy to modify
    highlighted_index = 0  # 0 = checkbox, 1 = save button
    total_items = 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            # C key or ESC = Cancel
            if event.key in (pygame.K_c, pygame.K_ESCAPE):
                print("[CREDITS] Cancelled by user")
                return None

            # S key = SELECT - Toggle checkbox OR save
            elif event.key == pygame.K_s:
                if highlighted_index == 0:
                    # Checkbox is highlighted - toggle it
                    credits_enabled = not credits_enabled
                    print(f"[CREDITS] Toggled to: {credits_enabled}")
                elif highlighted_index == 1:
                    # Save button is highlighted - save and exit
                    print(f"[CREDITS] Saving setting: {credits_enabled}")
                    return credits_enabled

            # UP arrow - move highlight up
            elif event.key == pygame.K_UP:
                if highlighted_index > 0:
                    highlighted_index -= 1

            # DOWN arrow - move highlight down
            elif event.key == pygame.K_DOWN:
                if highlighted_index < total_items - 1:
                    highlighted_index += 1

        # --- Drawing ---
        panel_surface.fill(BACKGROUND_COLOR)

        # Draw title
        title_text = title_font.render("Credit Settings", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 50))
        panel_surface.blit(title_text, title_rect)

        # Draw checkbox and label
        checkbox_y = 150
        checkbox_x = 150
        checkbox_size = 30

        # Checkbox is item 0
        checkbox_highlighted = (highlighted_index == 0)

        # Draw checkbox
        checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        border_color = HIGHLIGHT_COLOR if checkbox_highlighted else TEXT_COLOR
        pygame.draw.rect(panel_surface, border_color, checkbox_rect, 3)

        # Checkbox fill if enabled
        if credits_enabled:
            inner_rect = pygame.Rect(checkbox_x + 6, checkbox_y + 6, checkbox_size - 12, checkbox_size - 12)
            pygame.draw.rect(panel_surface, HIGHLIGHT_COLOR, inner_rect)

        # Draw label
        label_color = HIGHLIGHT_COLOR if checkbox_highlighted else TEXT_COLOR
        label_text = label_font.render("Credits Required", True, label_color)
        panel_surface.blit(label_text, (checkbox_x + checkbox_size + 20, checkbox_y))

        # Draw explanation text
        if credits_enabled:
            explain_text = "Users must insert quarters to select and play songs"
        else:
            explain_text = "Free play mode - no quarters required to select songs"

        explain_font = instruction_font
        explain_render = explain_font.render(explain_text, True, TEXT_COLOR)
        explain_rect = explain_render.get_rect(center=(PANEL_WIDTH // 2, 250))
        panel_surface.blit(explain_render, explain_rect)

        # Draw "Save Settings" button at bottom
        button_y = PANEL_HEIGHT - 120
        save_button_highlighted = (highlighted_index == 1)
        button_color = HIGHLIGHT_COLOR if save_button_highlighted else TEXT_COLOR

        save_button_text = button_font.render("Save Settings", True, button_color)
        save_button_rect = save_button_text.get_rect(center=(PANEL_WIDTH // 2, button_y))
        panel_surface.blit(save_button_text, save_button_rect)

        # Draw instructions at bottom
        instructions = [
            "UP/DOWN: Navigate | SELECT: Toggle or Save",
            "CORRECT: Cancel"
        ]

        inst_y = PANEL_HEIGHT - 70
        for instruction in instructions:
            inst_text = instruction_font.render(instruction, True, TEXT_COLOR)
            inst_rect = inst_text.get_rect(center=(PANEL_WIDTH // 2, inst_y))
            panel_surface.blit(inst_text, inst_rect)
            inst_y += 25

        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01)

    return None


# --- Select Year Range Function ---
def select_year_range(screen, song_list, current_enabled, current_start, current_end):
    """Display year range selection screen with dual spinners and checkbox.

    Args:
        screen: Pygame screen surface
        song_list: List of song dictionaries from MusicMasterSongList
        current_enabled: Boolean - True if year range filter is active
        current_start: Integer - Current starting year
        current_end: Integer - Current ending year

    Returns:
        Tuple or None - (enabled, start_year, end_year) if saved, None if cancelled
    """
    # Extract all unique years from song list
    all_years = set()
    for song in song_list:
        year_str = song.get('year', '')
        if year_str and year_str.isdigit():
            year = int(year_str)
            if year > 0:  # Skip invalid years
                all_years.add(year)

    # Sort years
    sorted_years = sorted(all_years)

    if not sorted_years:
        print("[ERROR] No valid years found in music collection")
        return None

    min_year = min(sorted_years)
    max_year = max(sorted_years)

    panel_surface = pygame.Surface((PANEL_WIDTH, PANEL_HEIGHT))

    # Load fonts
    try:
        title_font = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        label_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        year_font = pygame.font.Font(FONT_PATH, 48)  # Large font for year display
        button_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MENU)
        instruction_font = pygame.font.Font(FONT_PATH, FONT_SIZE_MESSAGE)
    except Exception:
        title_font = pygame.font.SysFont(None, FONT_SIZE_TITLE)
        label_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        year_font = pygame.font.SysFont(None, 48)
        button_font = pygame.font.SysFont(None, FONT_SIZE_MENU)
        instruction_font = pygame.font.SysFont(None, FONT_SIZE_MESSAGE)

    # State variables
    year_range_enabled = current_enabled

    # Default to 1967 if not previously set or if previous setting is invalid
    default_year = 1967 if 1967 in sorted_years else sorted_years[len(sorted_years) // 2]

    # Use current settings if valid, otherwise default to 1967
    if current_start in sorted_years and current_end in sorted_years:
        start_year = current_start
        end_year = current_end
    else:
        start_year = default_year
        end_year = default_year

    # Find indices in sorted_years list
    start_year_index = sorted_years.index(start_year)
    end_year_index = sorted_years.index(end_year)

    highlighted_index = 0  # 0 = start year wheel, 1 = end year wheel, 2 = checkbox, 3 = save button
    total_items = 4

    # Track if left wheel has been changed (for auto-matching right wheel)
    left_wheel_changed = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            # C key or ESC = Cancel
            if event.key in (pygame.K_c, pygame.K_ESCAPE):
                print("[YEAR RANGE] Cancelled by user")
                return None

            # S key = SELECT - Confirm current item and move to next
            elif event.key == pygame.K_s:
                if highlighted_index == 0:
                    # Left wheel - confirm and jump to right wheel
                    highlighted_index = 1
                    print(f"[YEAR RANGE] Start year confirmed: {start_year}, moving to end year")
                elif highlighted_index == 1:
                    # Right wheel - confirm and jump to checkbox
                    highlighted_index = 2
                    print(f"[YEAR RANGE] End year confirmed: {end_year}, moving to checkbox")
                elif highlighted_index == 2:
                    # Checkbox - toggle it
                    year_range_enabled = not year_range_enabled
                    print(f"[YEAR RANGE] Toggled to: {year_range_enabled}")
                elif highlighted_index == 3:
                    # Save button - save and exit
                    print(f"[YEAR RANGE] Saving: enabled={year_range_enabled}, start={start_year}, end={end_year}")
                    return (year_range_enabled, start_year, end_year)

            # UP arrow - Increment year on current wheel
            elif event.key == pygame.K_UP:
                if highlighted_index == 0:
                    # Left wheel - increment start year
                    if start_year_index < len(sorted_years) - 1:
                        start_year_index += 1
                        start_year = sorted_years[start_year_index]
                        # First change: auto-match right wheel
                        if not left_wheel_changed:
                            end_year = start_year
                            end_year_index = start_year_index
                            left_wheel_changed = True
                        # After first change: ensure end >= start
                        elif end_year < start_year:
                            end_year = start_year
                            end_year_index = start_year_index
                        print(f"[YEAR RANGE] Start year: {start_year}")
                elif highlighted_index == 1:
                    # Right wheel - increment end year
                    if end_year_index < len(sorted_years) - 1:
                        end_year_index += 1
                        end_year = sorted_years[end_year_index]
                        print(f"[YEAR RANGE] End year: {end_year}")
                elif highlighted_index == 2:
                    # Navigate up from checkbox to right wheel
                    highlighted_index = 1
                elif highlighted_index == 3:
                    # Navigate up from save button to checkbox
                    highlighted_index = 2

            # DOWN arrow - Decrement year on current wheel
            elif event.key == pygame.K_DOWN:
                if highlighted_index == 0:
                    # Left wheel - decrement start year
                    if start_year_index > 0:
                        start_year_index -= 1
                        start_year = sorted_years[start_year_index]
                        # First change: auto-match right wheel
                        if not left_wheel_changed:
                            end_year = start_year
                            end_year_index = start_year_index
                            left_wheel_changed = True
                        # After first change: don't auto-adjust
                        print(f"[YEAR RANGE] Start year: {start_year}")
                elif highlighted_index == 1:
                    # Right wheel - decrement end year (but not below start year)
                    if end_year_index > 0:
                        new_index = end_year_index - 1
                        new_year = sorted_years[new_index]
                        if new_year >= start_year:
                            end_year_index = new_index
                            end_year = new_year
                            print(f"[YEAR RANGE] End year: {end_year}")
                        else:
                            print(f"[YEAR RANGE] End year cannot be before start year")
                elif highlighted_index == 2:
                    # Navigate down from checkbox to save button
                    highlighted_index = 3
                elif highlighted_index == 3:
                    # Already at bottom
                    pass

            # LEFT arrow - Move to previous item
            elif event.key == pygame.K_LEFT:
                if highlighted_index > 0:
                    highlighted_index -= 1

            # RIGHT arrow - Move to next item
            elif event.key == pygame.K_RIGHT:
                if highlighted_index < total_items - 1:
                    highlighted_index += 1

        # --- Drawing ---
        panel_surface.fill(BACKGROUND_COLOR)

        # Draw title
        title_text = title_font.render("Select Year Range", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(PANEL_WIDTH // 2, 40))
        panel_surface.blit(title_text, title_rect)

        # Draw year spinners section
        spinner_y = 120

        # LEFT WHEEL - Start year spinner (item 0)
        start_highlighted = (highlighted_index == 0)
        start_color = HIGHLIGHT_COLOR if start_highlighted else TEXT_COLOR

        start_year_text = year_font.render(str(start_year), True, start_color)
        start_year_rect = start_year_text.get_rect(center=(PANEL_WIDTH // 2 - 120, spinner_y))
        panel_surface.blit(start_year_text, start_year_rect)

        # Draw up/down arrows for start year if highlighted
        if start_highlighted:
            up_arrow = instruction_font.render("▲", True, start_color)
            down_arrow = instruction_font.render("▼", True, start_color)
            panel_surface.blit(up_arrow, (start_year_rect.centerx - up_arrow.get_width() // 2, start_year_rect.top - 30))
            panel_surface.blit(down_arrow, (start_year_rect.centerx - down_arrow.get_width() // 2, start_year_rect.bottom + 10))

        # "through" text
        through_text = label_font.render("through", True, TEXT_COLOR)
        through_rect = through_text.get_rect(center=(PANEL_WIDTH // 2, spinner_y))
        panel_surface.blit(through_text, through_rect)

        # RIGHT WHEEL - End year spinner (item 1)
        end_highlighted = (highlighted_index == 1)
        end_color = HIGHLIGHT_COLOR if end_highlighted else TEXT_COLOR

        end_year_text = year_font.render(str(end_year), True, end_color)
        end_year_rect = end_year_text.get_rect(center=(PANEL_WIDTH // 2 + 120, spinner_y))
        panel_surface.blit(end_year_text, end_year_rect)

        # Draw up/down arrows for end year if highlighted
        if end_highlighted:
            up_arrow = instruction_font.render("▲", True, end_color)
            down_arrow = instruction_font.render("▼", True, end_color)
            panel_surface.blit(up_arrow, (end_year_rect.centerx - up_arrow.get_width() // 2, end_year_rect.top - 30))
            panel_surface.blit(down_arrow, (end_year_rect.centerx - down_arrow.get_width() // 2, end_year_rect.bottom + 10))

        # Draw checkbox and label (item 2)
        checkbox_y = 250
        checkbox_x = 150
        checkbox_size = 30

        checkbox_highlighted = (highlighted_index == 2)

        # Draw checkbox
        checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        border_color = HIGHLIGHT_COLOR if checkbox_highlighted else TEXT_COLOR
        pygame.draw.rect(panel_surface, border_color, checkbox_rect, 3)

        # Checkbox fill if enabled
        if year_range_enabled:
            inner_rect = pygame.Rect(checkbox_x + 6, checkbox_y + 6, checkbox_size - 12, checkbox_size - 12)
            pygame.draw.rect(panel_surface, HIGHLIGHT_COLOR, inner_rect)

        # Draw label
        label_color = HIGHLIGHT_COLOR if checkbox_highlighted else TEXT_COLOR
        label_text = label_font.render("Select Year Range", True, label_color)
        panel_surface.blit(label_text, (checkbox_x + checkbox_size + 20, checkbox_y))

        # Draw explanation text
        if year_range_enabled:
            explain_text = f"Random playlist will only include songs from {start_year} through {end_year}"
        else:
            explain_text = "All years will be included in random playlist"

        explain_font = instruction_font
        explain_render = explain_font.render(explain_text, True, TEXT_COLOR)
        explain_rect = explain_render.get_rect(center=(PANEL_WIDTH // 2, 320))
        panel_surface.blit(explain_render, explain_rect)

        # Draw "Save Settings" button at bottom (item 3)
        button_y = PANEL_HEIGHT - 120
        save_button_highlighted = (highlighted_index == 3)
        button_color = HIGHLIGHT_COLOR if save_button_highlighted else TEXT_COLOR

        save_button_text = button_font.render("Save Settings", True, button_color)
        save_button_rect = save_button_text.get_rect(center=(PANEL_WIDTH // 2, button_y))
        panel_surface.blit(save_button_text, save_button_rect)

        # Draw instructions at bottom
        if highlighted_index == 0:
            instructions = [
                "UP/DOWN: Change Start Year | SELECT: Confirm and Move to End Year",
                "LEFT/RIGHT: Navigate | CORRECT: Cancel"
            ]
        elif highlighted_index == 1:
            instructions = [
                "UP/DOWN: Change End Year | SELECT: Confirm and Move to Checkbox",
                "LEFT/RIGHT: Navigate | CORRECT: Cancel"
            ]
        else:
            instructions = [
                "UP/DOWN or LEFT/RIGHT: Navigate | SELECT: Toggle or Save",
                "CORRECT: Cancel"
            ]

        inst_y = PANEL_HEIGHT - 70
        for instruction in instructions:
            inst_text = instruction_font.render(instruction, True, TEXT_COLOR)
            inst_rect = inst_text.get_rect(center=(PANEL_WIDTH // 2, inst_y))
            panel_surface.blit(inst_text, inst_rect)
            inst_y += 25

        # Blit panel to main screen
        screen.blit(panel_surface, (PANEL_POS_X, PANEL_POS_Y))
        pygame.display.flip()

        time.sleep(0.01)

    return None

