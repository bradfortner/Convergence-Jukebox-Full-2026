"""
Pygame Search Module for Convergence Jukebox
Provides optimized title and artist search functionality using pygame interface

Features:
- Binary search for O(log n) performance with 16,000+ songs
- Pure pygame interface (no FreeSimpleGUI dependency)
- Keyboard-only navigation matching jukebox aesthetic
- Left-anchored prefix matching (case-insensitive)
- Returns up to 5 results per search
"""

import pygame
import os
import time
from typing import List, Dict, Optional, Tuple, Any

# ============================================================================
# CONSTANTS
# ============================================================================

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Colors (matching jukebox aesthetic)
COLOR_BLACK = (0, 0, 0)
COLOR_GOLDENROD = (218, 165, 32)      # goldenrod1
COLOR_FIREBRICK = (139, 35, 35)       # firebrick4
COLOR_WHITE = (255, 255, 255)

# Button dimensions
BUTTON_WIDTH = 45
BUTTON_HEIGHT = 45
BUTTON_SPACING = 10
BUTTON_BORDER = 6

# Grid positioning
GRID_START_X = 100
GRID_START_Y = 300

# Result button positioning
RESULT_X = 700
RESULT_Y = 300
RESULT_WIDTH = 500
RESULT_HEIGHT = 45
RESULT_SPACING = 20

# Header positioning
HEADER_Y = 240
SEARCH_TEXT_X = 400
SEARCH_TEXT_Y = 250

# Font settings
FONT_SIZE_BUTTON = 16
FONT_SIZE_HEADER = 18
FONT_SIZE_RESULT = 14

# Search settings
MIN_QUERY_LENGTH = 3  # Only search when query >= 3 characters
MAX_RESULTS = 5       # Show up to 5 results

# ============================================================================
# BINARY SEARCH FUNCTIONS
# ============================================================================

def binary_search_first_match(sorted_list: List[Dict], prefix: str, key_func) -> int:
    """
    Find the index of the first item that starts with prefix using binary search.

    Args:
        sorted_list: List sorted by the key returned by key_func
        prefix: The prefix to search for (case-insensitive)
        key_func: Function to extract the search key from each item

    Returns:
        Index of first match, or -1 if no match found
    """
    if not sorted_list or not prefix:
        return -1

    prefix_lower = prefix.lower()
    left, right = 0, len(sorted_list) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        item = key_func(sorted_list[mid])
        item_lower = item.lower()

        if item_lower.startswith(prefix_lower):
            result = mid
            right = mid - 1  # Keep searching left for first match
        elif item_lower < prefix_lower:
            left = mid + 1
        else:
            right = mid - 1

    return result


def search_titles_optimized(query: str, sorted_list: List[Dict], max_results: int = MAX_RESULTS) -> List[Dict]:
    """
    Search for song titles starting with query (optimized with binary search).

    Args:
        query: Search query string
        sorted_list: List of songs sorted by title (lowercase)
        max_results: Maximum number of results to return

    Returns:
        List of result dictionaries with 'display' and 'song_data' keys
    """
    if not query or len(query) < MIN_QUERY_LENGTH:
        return []

    # Binary search to find first match
    start_idx = binary_search_first_match(sorted_list, query, lambda x: x['title'])

    if start_idx == -1:
        return []

    # Collect consecutive matches (list is sorted, stop when prefix changes)
    results = []
    query_lower = query.lower()

    for i in range(start_idx, len(sorted_list)):
        if len(results) >= max_results:
            break

        if sorted_list[i]['title'].lower().startswith(query_lower):
            results.append({
                'display': f"{sorted_list[i]['artist']} - {sorted_list[i]['title']}",
                'song_data': sorted_list[i]
            })
        else:
            break  # No more matches (list is sorted)

    return results


def search_artists_optimized(query: str, sorted_artist_list: List[str],
                            music_master_song_list: List[Dict],
                            max_results: int = MAX_RESULTS) -> List[Dict]:
    """
    Search for artists starting with query (optimized with binary search).

    Args:
        query: Search query string
        sorted_artist_list: List of unique artist names sorted alphabetically
        music_master_song_list: Full song list (for finding first song by artist)
        max_results: Maximum number of results to return

    Returns:
        List of result dictionaries with 'display' and 'artist_name' keys
    """
    if not query or len(query) < MIN_QUERY_LENGTH:
        return []

    # Binary search artist list
    query_lower = query.lower()
    left, right = 0, len(sorted_artist_list) - 1
    first_match_idx = -1

    while left <= right:
        mid = (left + right) // 2
        artist_lower = sorted_artist_list[mid].lower()

        if artist_lower.startswith(query_lower):
            first_match_idx = mid
            right = mid - 1  # Keep searching left
        elif artist_lower < query_lower:
            left = mid + 1
        else:
            right = mid - 1

    if first_match_idx == -1:
        return []

    # Collect consecutive matches
    results = []
    for i in range(first_match_idx, len(sorted_artist_list)):
        if len(results) >= max_results:
            break

        artist = sorted_artist_list[i]
        if artist.lower().startswith(query_lower):
            results.append({
                'display': artist,
                'artist_name': artist
            })
        else:
            break

    return results


def find_first_song_by_artist(artist_name: str, music_master_song_list: List[Dict]) -> Optional[int]:
    """
    Find the song number of the first song by a given artist.

    Args:
        artist_name: The artist name to search for
        music_master_song_list: The full song list

    Returns:
        Song number (from 'number' field) or None if not found
    """
    for song in music_master_song_list:
        if song['artist'] == artist_name:
            return song['number']
    return None


# ============================================================================
# BUTTON GRID MAPPING
# ============================================================================

# Button grid mapping: {button_key: (row, col)}
# Result buttons are on the SAME ROW as keyboard buttons, in column 11 (right side)
BUTTON_GRID = {
    # Row 0: Numbers (cols 0-10) + result_one (col 11)
    '1': (0, 0), '2': (0, 1), '3': (0, 2), '4': (0, 3), '5': (0, 4),
    '6': (0, 5), '7': (0, 6), '8': (0, 7), '9': (0, 8), '0': (0, 9), '-': (0, 10),
    'RESULT_0': (0, 11),
    # Row 1: Letters A-K (cols 0-10) + result_two (col 11)
    'A': (1, 0), 'B': (1, 1), 'C': (1, 2), 'D': (1, 3), 'E': (1, 4),
    'F': (1, 5), 'G': (1, 6), 'H': (1, 7), 'I': (1, 8), 'J': (1, 9), 'K': (1, 10),
    'RESULT_1': (1, 11),
    # Row 2: Letters L-V (cols 0-10) + result_three (col 11)
    'L': (2, 0), 'M': (2, 1), 'N': (2, 2), 'O': (2, 3), 'P': (2, 4),
    'Q': (2, 5), 'R': (2, 6), 'S': (2, 7), 'T': (2, 8), 'U': (2, 9), 'V': (2, 10),
    'RESULT_2': (2, 11),
    # Row 3: Letters W-Z, apostrophe (cols 0-4) + result_four (col 11)
    'W': (3, 0), 'X': (3, 1), 'Y': (3, 2), 'Z': (3, 3), "'": (3, 4),
    'RESULT_3': (3, 11),
    # Row 4: Special buttons (cols 0-3) + result_five (col 11)
    'DELETE': (4, 0), 'SPACE': (4, 1), 'CLEAR': (4, 2), 'EXIT': (4, 3),
    'RESULT_4': (4, 11)
}

# Reverse mapping: {(row, col): button_key}
GRID_TO_BUTTON = {v: k for k, v in BUTTON_GRID.items()}

# Row column limits for navigation (including result button at col 11)
ROW_COL_LIMITS = {
    0: 11,  # Row 0: Numbers (0-10) + result button (11)
    1: 11,  # Row 1: A-K (0-10) + result button (11)
    2: 11,  # Row 2: L-V (0-10) + result button (11)
    3: 11,  # Row 3: W-Z, ' (0-4) + gap + result button (11)
    4: 11   # Row 4: DELETE, SPACE, CLEAR, EXIT (0-3) + gap + result button (11)
}


# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def draw_button(surface: pygame.Surface, x: int, y: int, width: int, height: int,
                text: str, font: pygame.font.Font, is_focused: bool = False,
                border_width: int = BUTTON_BORDER) -> pygame.Rect:
    """
    Draw a button with text.

    Args:
        surface: Pygame surface to draw on
        x, y: Button position
        width, height: Button dimensions
        text: Button text
        font: Pygame font object
        is_focused: Whether button is currently focused
        border_width: Width of button border

    Returns:
        pygame.Rect of the button area
    """
    rect = pygame.Rect(x, y, width, height)

    # Choose colors based on focus state
    if is_focused:
        bg_color = COLOR_FIREBRICK
        text_color = COLOR_GOLDENROD
    else:
        bg_color = COLOR_GOLDENROD
        text_color = COLOR_FIREBRICK

    # Draw button background
    pygame.draw.rect(surface, bg_color, rect)

    # Draw border
    pygame.draw.rect(surface, COLOR_BLACK, rect, border_width)

    # Draw text (centered)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

    return rect


def draw_wide_button(surface: pygame.Surface, x: int, y: int, width: int, height: int,
                     text: str, font: pygame.font.Font, is_focused: bool = False,
                     is_visible: bool = True) -> pygame.Rect:
    """
    Draw a wide button (for results and special functions).

    Returns:
        pygame.Rect of the button area
    """
    if not is_visible:
        return pygame.Rect(x, y, width, height)

    rect = pygame.Rect(x, y, width, height)

    # Choose colors
    if is_focused:
        bg_color = COLOR_FIREBRICK
        text_color = COLOR_GOLDENROD
    else:
        bg_color = COLOR_GOLDENROD
        text_color = COLOR_FIREBRICK

    # Draw button
    pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, COLOR_BLACK, rect, BUTTON_BORDER)

    # Draw text (left-aligned for results, centered for functions)
    text_surf = font.render(text, True, text_color)
    if width > 200:  # Result button (left-aligned)
        text_rect = text_surf.get_rect(midleft=(rect.left + 10, rect.centery))
    else:  # Function button (centered)
        text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

    return rect


# ============================================================================
# MAIN SEARCH INTERFACE
# ============================================================================

def display_search_popup(search_type: str, title_sorted_list: List[Dict],
                        artist_sorted_list: List[str],
                        music_master_song_list: List[Dict]) -> Optional[Dict]:
    """
    Display pygame search window and handle user input.

    Args:
        search_type: "title" or "artist"
        title_sorted_list: Pre-sorted list of songs by title
        artist_sorted_list: Pre-sorted list of unique artist names
        music_master_song_list: Original unsorted song list

    Returns:
        {'song_number': int, 'song_selected': str, 'song_data': dict, 'last_keypress_time': float} for title search
        {'song_number': int, 'song_selected': None, 'last_keypress_time': float} for artist search
        None if cancelled

        last_keypress_time is the timestamp of the last keypress in the search window,
        used by main file to reset the rotating record popup idle timer.
    """
    # Initialize pygame if not already initialized
    if not pygame.get_init():
        pygame.init()

    # Create window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Search For {'Title' if search_type == 'title' else 'Artist'}")

    # Load fonts
    try:
        font_button = pygame.font.Font(None, FONT_SIZE_BUTTON + 20)
        font_header = pygame.font.Font(None, FONT_SIZE_HEADER + 20)
        font_result = pygame.font.Font(None, FONT_SIZE_RESULT + 20)
    except Exception:
        font_button = pygame.font.SysFont('arial', FONT_SIZE_BUTTON)
        font_header = pygame.font.SysFont('arial', FONT_SIZE_HEADER)
        font_result = pygame.font.SysFont('arial', FONT_SIZE_RESULT)

    # State variables
    keys_entered = ""
    search_results = []
    current_focused = 'A'  # Start with A button focused
    button_rects = {}  # Store button rectangles for click detection
    last_keypress_time = time.time()  # Track last keypress for idle timer reset

    # Load logo if available
    logo_surf = None
    logo_path = "images/jukebox_2025_logo.png"
    if os.path.exists(logo_path):
        try:
            logo_image = pygame.image.load(logo_path)
            logo_surf = pygame.transform.scale(logo_image, (439, 226))
        except Exception:
            pass

    # Load magnifying glass icon
    magglass_surf = None
    magglass_path = "images/magglass.png"
    if os.path.exists(magglass_path):
        try:
            magglass_image = pygame.image.load(magglass_path)
            magglass_surf = pygame.transform.scale(magglass_image, (25, 25))
        except Exception:
            pass

    # Main event loop
    clock = pygame.time.Clock()
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            elif event.type == pygame.KEYDOWN:
                # Update last keypress time for idle timer
                last_keypress_time = time.time()

                # ESC key - exit
                if event.key == pygame.K_ESCAPE:
                    return None

                # S key - special handling (SELECT for keyboard navigation, or type 'S' directly)
                elif event.key == pygame.K_s:
                    # If focused on S button itself, add 'S' to search
                    if current_focused == 'S':
                        keys_entered += 'S'
                    # If focused on a result button, select that result
                    elif current_focused.startswith('RESULT_'):
                        result_idx = int(current_focused.split('_')[1])
                        if result_idx < len(search_results):
                            # Handle selection
                            result = search_results[result_idx]
                            if search_type == "title":
                                song_data = result['song_data']
                                return {
                                    'song_number': song_data['number'],
                                    'song_selected': 'A1',
                                    'song_data': song_data,
                                    'last_keypress_time': last_keypress_time
                                }
                            else:  # artist search
                                artist_name = result['artist_name']
                                song_number = find_first_song_by_artist(artist_name, music_master_song_list)
                                if song_number is not None:
                                    return {
                                        'song_number': song_number,
                                        'song_selected': None,
                                        'last_keypress_time': last_keypress_time
                                    }
                    # If focused on any other keyboard button, add that character
                    elif current_focused in BUTTON_GRID:
                        if current_focused == 'SPACE':
                            keys_entered += " "
                        elif current_focused == 'DELETE':
                            if keys_entered:
                                keys_entered = keys_entered[:-1]
                        elif current_focused == 'CLEAR':
                            keys_entered = ""
                            search_results = []
                        elif current_focused == 'EXIT':
                            return None
                        elif len(current_focused) == 1 or current_focused == "'":
                            # Single character button (letter, number, or apostrophe)
                            keys_entered += current_focused
                    else:
                        # Not focused on any special button, just typing S directly
                        keys_entered += 'S'

                # Other letter keys (A-Z except S)
                elif event.key >= pygame.K_a and event.key <= pygame.K_z:
                    char = chr(event.key).upper()
                    keys_entered += char

                # Number keys
                elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
                    char = chr(event.key)
                    keys_entered += char

                # Special characters
                elif event.key == pygame.K_SPACE:
                    keys_entered += " "
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    keys_entered += "-"
                elif event.key == pygame.K_QUOTE:
                    keys_entered += "'"

                # Backspace / Delete
                elif event.key == pygame.K_BACKSPACE:
                    if keys_entered:
                        keys_entered = keys_entered[:-1]

                # Clear
                elif event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                    keys_entered = ""
                    search_results = []

                # Arrow key navigation
                elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    current_focused = handle_arrow_navigation(
                        current_focused, event.key, len(search_results)
                    )

                # Special function keys
                elif event.key == pygame.K_DELETE:
                    if keys_entered:
                        keys_entered = keys_entered[:-1]

            # Mouse click handling
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    # Check if clicked on any button
                    for button_key, button_rect in button_rects.items():
                        if button_rect.collidepoint(mouse_pos):
                            # Clicked on a keyboard button - add that character
                            if button_key in BUTTON_GRID and not button_key.startswith('RESULT_'):
                                if button_key == 'SPACE':
                                    keys_entered += " "
                                elif button_key == 'DELETE':
                                    if keys_entered:
                                        keys_entered = keys_entered[:-1]
                                elif button_key == 'CLEAR':
                                    keys_entered = ""
                                    search_results = []
                                elif button_key == 'EXIT':
                                    return None
                                elif len(button_key) == 1 or button_key == "'":
                                    # Single character button
                                    keys_entered += button_key
                                # Also set focus to clicked button
                                current_focused = button_key
                            # Clicked on a result button - select that result
                            elif button_key.startswith('RESULT_'):
                                result_idx = int(button_key.split('_')[1])
                                if result_idx < len(search_results):
                                    result = search_results[result_idx]
                                    if search_type == "title":
                                        song_data = result['song_data']
                                        return {
                                            'song_number': song_data['number'],
                                            'song_selected': 'A1',
                                            'song_data': song_data,
                                            'last_keypress_time': last_keypress_time
                                        }
                                    else:  # artist search
                                        artist_name = result['artist_name']
                                        song_number = find_first_song_by_artist(artist_name, music_master_song_list)
                                        if song_number is not None:
                                            return {
                                                'song_number': song_number,
                                                'song_selected': None,
                                                'last_keypress_time': last_keypress_time
                                            }
                            break  # Stop checking other buttons

        # Perform search if query is long enough
        if len(keys_entered) >= MIN_QUERY_LENGTH:
            if search_type == "title":
                search_results = search_titles_optimized(keys_entered, title_sorted_list)
            else:
                search_results = search_artists_optimized(
                    keys_entered, artist_sorted_list, music_master_song_list
                )
        else:
            search_results = []

        # Render everything
        screen.fill(COLOR_BLACK)

        # Draw logo
        if logo_surf:
            logo_x = (SCREEN_WIDTH - logo_surf.get_width()) // 2
            screen.blit(logo_surf, (logo_x, 20))

        # Draw header with magnifying glass and search box all on white background
        header_text = f"Search For {'Title' if search_type == 'title' else 'Artist'}"

        # Single white background for entire header row (text + icon + search box)
        header_bg_rect = pygame.Rect(300, HEADER_Y, 680, 40)
        pygame.draw.rect(screen, COLOR_WHITE, header_bg_rect)

        # Draw "Search For Title/Artist" text
        header_surf = font_header.render(header_text, True, COLOR_BLACK)
        header_text_x = 320
        screen.blit(header_surf, (header_text_x, HEADER_Y + 10))

        # Draw magnifying glass icon after header text
        if magglass_surf:
            magglass_x = header_text_x + header_surf.get_width() + 10
            magglass_y = HEADER_Y + 8
            screen.blit(magglass_surf, (magglass_x, magglass_y))

            # Draw search text box after magnifying glass (starts empty, no placeholder)
            search_text_x = magglass_x + 35
            if keys_entered:
                search_surf = font_header.render(keys_entered, True, COLOR_BLACK)
                screen.blit(search_surf, (search_text_x, HEADER_Y + 10))

        # Draw keyboard grid
        button_rects = draw_keyboard_grid(screen, font_button, current_focused)

        # Draw result buttons and merge their rects
        result_rects = draw_result_buttons(screen, font_result, search_results, current_focused, search_type, keys_entered)
        button_rects.update(result_rects)

        # Update display
        pygame.display.flip()
        clock.tick(30)

    return None


def draw_keyboard_grid(surface: pygame.Surface, font: pygame.font.Font,
                       current_focused: str) -> Dict[str, pygame.Rect]:
    """Draw the keyboard button grid and return button rectangles."""
    button_rects = {}

    # Draw number row (Row 0)
    for i, char in enumerate(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-']):
        x = GRID_START_X + i * (BUTTON_WIDTH + BUTTON_SPACING)
        y = GRID_START_Y
        is_focused = (current_focused == char)
        rect = draw_button(surface, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, char, font, is_focused)
        button_rects[char] = rect

    # Draw letter row 1 (A-K, Row 1)
    for i, char in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']):
        x = GRID_START_X + i * (BUTTON_WIDTH + BUTTON_SPACING)
        y = GRID_START_Y + (BUTTON_HEIGHT + BUTTON_SPACING)
        is_focused = (current_focused == char)
        rect = draw_button(surface, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, char, font, is_focused)
        button_rects[char] = rect

    # Draw letter row 2 (L-V, Row 2)
    for i, char in enumerate(['L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V']):
        x = GRID_START_X + i * (BUTTON_WIDTH + BUTTON_SPACING)
        y = GRID_START_Y + 2 * (BUTTON_HEIGHT + BUTTON_SPACING)
        is_focused = (current_focused == char)
        rect = draw_button(surface, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, char, font, is_focused)
        button_rects[char] = rect

    # Draw letter row 3 (W-Z, ', Row 3)
    for i, char in enumerate(['W', 'X', 'Y', 'Z', "'"]):
        x = GRID_START_X + i * (BUTTON_WIDTH + BUTTON_SPACING)
        y = GRID_START_Y + 3 * (BUTTON_HEIGHT + BUTTON_SPACING)
        is_focused = (current_focused == char)
        rect = draw_button(surface, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, char, font, is_focused)
        button_rects[char] = rect

    # Draw function buttons (Row 4)
    func_buttons = [
        ('DELETE', 'DELETE', 140),
        ('SPACE', 'SPACE', 90),
        ('CLEAR', 'CLEAR', 90),
        ('EXIT', 'EXIT', 90)
    ]

    x_offset = GRID_START_X
    y = GRID_START_Y + 4 * (BUTTON_HEIGHT + BUTTON_SPACING)

    for key, label, width in func_buttons:
        is_focused = (current_focused == key)
        rect = draw_wide_button(surface, x_offset, y, width, BUTTON_HEIGHT,
                               label, font, is_focused)
        button_rects[key] = rect
        x_offset += width + BUTTON_SPACING

    return button_rects


def draw_result_buttons(surface: pygame.Surface, font: pygame.font.Font,
                       search_results: List[Dict], current_focused: str,
                       search_type: str, keys_entered: str) -> Dict[str, pygame.Rect]:
    """Draw the result display buttons on the right side and return their rectangles."""
    result_rects = {}

    for i in range(MAX_RESULTS):
        x = RESULT_X
        y = RESULT_Y + i * (RESULT_HEIGHT + RESULT_SPACING)

        button_key = f'RESULT_{i}'
        is_focused = (current_focused == button_key)

        if i < len(search_results):
            # Show result
            text = search_results[i]['display']
            rect = draw_wide_button(surface, x, y, RESULT_WIDTH, RESULT_HEIGHT,
                           text, font, is_focused, is_visible=True)
            result_rects[button_key] = rect
        elif len(search_results) == 0 and i == 0 and len(keys_entered) >= MIN_QUERY_LENGTH:
            # Show "not found" message ONLY when user has typed enough characters
            if search_type == "title":
                text = "Song Title Not On Jukebox"
            else:
                text = "Artist Not On Jukebox"
            rect = draw_wide_button(surface, x, y, RESULT_WIDTH, RESULT_HEIGHT,
                           text, font, False, is_visible=True)
            result_rects[button_key] = rect

    return result_rects


def handle_arrow_navigation(current_focused: str, arrow_key: int,
                           num_results: int) -> str:
    """
    Handle arrow key navigation through the button grid.

    Args:
        current_focused: Currently focused button key
        arrow_key: pygame key constant (K_UP, K_DOWN, K_LEFT, K_RIGHT)
        num_results: Number of search results (for result button navigation)

    Returns:
        New focused button key
    """
    if current_focused not in BUTTON_GRID:
        return current_focused

    current_row, current_col = BUTTON_GRID[current_focused]

    # Handle navigation
    if arrow_key == pygame.K_UP:
        target_row = current_row - 1
        target_col = current_col

        # Stay within bounds
        if target_row < 0:
            return current_focused

        # Adjust column if target row has fewer columns
        if target_row in ROW_COL_LIMITS:
            if target_col > ROW_COL_LIMITS[target_row]:
                target_col = ROW_COL_LIMITS[target_row]

            # If navigating to result button column when no results exist
            if target_col == 11 and num_results == 0:
                # Navigate to last keyboard button in that row instead
                if target_row == 3:
                    target_col = 4  # Apostrophe
                elif target_row == 4:
                    target_col = 3  # EXIT
                else:
                    target_col = 10  # Last letter in rows 0, 1, 2

            if (target_row, target_col) in GRID_TO_BUTTON:
                return GRID_TO_BUTTON[(target_row, target_col)]

    elif arrow_key == pygame.K_DOWN:
        target_row = current_row + 1
        target_col = current_col

        # Stay within bounds (only rows 0-4 exist)
        if target_row > 4:
            return current_focused

        # Adjust column if target row has fewer columns
        if target_row in ROW_COL_LIMITS:
            # Handle shorter rows (row 3 has cols 0-4, row 4 has cols 0-3)
            if target_row == 3 and target_col > 4 and target_col < 11:
                target_col = 4  # Jump to last button in row
            elif target_row == 4 and target_col > 3 and target_col < 11:
                target_col = 3  # Jump to last button in row
            elif target_col > ROW_COL_LIMITS[target_row]:
                target_col = ROW_COL_LIMITS[target_row]

            # If navigating to result button column when no results exist
            if target_col == 11 and num_results == 0:
                # Navigate to last keyboard button in that row instead
                if target_row == 3:
                    target_col = 4  # Apostrophe
                elif target_row == 4:
                    target_col = 3  # EXIT
                else:
                    target_col = 10  # Last letter in rows 0, 1, 2

            if (target_row, target_col) in GRID_TO_BUTTON:
                return GRID_TO_BUTTON[(target_row, target_col)]

    elif arrow_key == pygame.K_RIGHT:
        target_row = current_row
        target_col = current_col + 1

        # Handle gap between keyboard buttons and result buttons
        # Row 3: cols 0-4 (W-Z, '), then gap, then col 11 (result)
        # Row 4: cols 0-3 (DELETE, SPACE, CLEAR, EXIT), then gap, then col 11 (result)
        if target_row == 3 and target_col > 4 and target_col < 11:
            target_col = 11  # Jump to result button
        elif target_row == 4 and target_col > 3 and target_col < 11:
            target_col = 11  # Jump to result button

        # Wrap or stay at edge
        if target_row in ROW_COL_LIMITS:
            if target_col > ROW_COL_LIMITS[target_row]:
                target_col = 0  # Wrap to start of row

            # Check if trying to navigate to result button when no results exist
            if target_col == 11 and num_results == 0:
                # Wrap to start of row instead of getting stuck
                target_col = 0

            if (target_row, target_col) in GRID_TO_BUTTON:
                return GRID_TO_BUTTON[(target_row, target_col)]

    elif arrow_key == pygame.K_LEFT:
        target_row = current_row
        target_col = current_col - 1

        # Handle gap ONLY when navigating LEFT FROM result button (current_col == 11)
        # Row 3: result at col 11, jump back to col 4 (')
        # Row 4: result at col 11, jump back to col 3 (EXIT)
        # Rows 0,1,2: result at col 11, jump back to col 10 (last keyboard button)
        if current_col == 11 and target_col == 10:
            # Coming from result button, jump over gap
            if target_row == 3:
                target_col = 4  # Jump to apostrophe
            elif target_row == 4:
                target_col = 3  # Jump to EXIT
            # Rows 0, 1, 2 stay at col 10 (no jump needed)

        # Wrap or stay at edge
        if target_col < 0:
            if target_row in ROW_COL_LIMITS:
                target_col = ROW_COL_LIMITS[target_row]  # Wrap to end of row (result button if visible)
                # Can't wrap to invisible result button
                if target_col == 11 and num_results == 0:
                    # Wrap to last keyboard button instead
                    if target_row == 3:
                        target_col = 4
                    elif target_row == 4:
                        target_col = 3
                    else:
                        target_col = 10

        if target_row in ROW_COL_LIMITS and 0 <= target_col <= ROW_COL_LIMITS[target_row]:
            if (target_row, target_col) in GRID_TO_BUTTON:
                return GRID_TO_BUTTON[(target_row, target_col)]

    return current_focused
