"""
CONVERGENCE JUKEBOX - PYGAME MIGRATION VERSION
Version 0.90.05 - Pure Pygame Implementation (Step 4: Arrow Key Navigation)

This version begins the migration from FreeSimpleGUI to pure Pygame.

Migration Goals:
- Eliminate Pygame/Tkinter z-order conflicts
- Enable seamless rotating record popup integration
- Create foundation for future touchscreen/arcade features

Version 0.90.05 Changes:
- Added left and right arrow buttons (100×47 pixels)
- Left arrow positioned at (-85, -180) relative, Right arrow at (425, -180) relative
- Arrow keys navigate through song pages (±21 songs)
- Arrows disabled at list boundaries with buzz sound
- Button grid updates when navigating pages
- Uses pygame.mixer for buzz.mp3 sound

Next Steps:
- Add keyboard input handling for button selection (a/b/c, 1-7)
- Port remaining UI elements

Original Code Reference:
- All original 0.83.60 code is preserved in 0.83.60 - Convergence-Jukebox-Full-2026.py
"""

# ============================================================================
# SECTION 1: IMPORTS
# ============================================================================

import pygame
import sys
import os
import json

# ============================================================================
# SECTION 2: CONSTANTS
# ============================================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_IMAGE_PATH = "images/Full Jukebox Background Master 2026.png"
SONG_LIST_PATH = "MusicMasterSongList.txt"
BUZZ_SOUND_PATH = "jukebox_required_audio_files/buzz.mp3"

# Button grid layout constants
GRID_START_X = 465  # Testing position for alignment with background
GRID_START_Y = 218

# Arrow button constants (relative positions converted to absolute)
# Original relative_location=(425, -180) and (-85, -180)
# Need to calculate absolute positions based on background window
ARROW_RIGHT_X = 1015
ARROW_RIGHT_Y = 160  # 720 - 180
ARROW_LEFT_X = 520  # 1280 - 85
ARROW_LEFT_Y = 160   # 720 - 180

# Button image paths
BUTTON_ID_BG = "images/button_id_bg.png"
BUTTON_ID_BLACK_BG = "images/button_id_black_bg.png"
SELECTION_TOP_BG = "images/new_selection_top_bg.png"
ARROW_LEFT_IMG = "images/lg_arrow_left.png"
ARROW_RIGHT_IMG = "images/lg_arrow_right.png"

# ============================================================================
# SECTION 3: BUTTON GRID CLASS
# ============================================================================

class ButtonGrid:
    """Manages the selection button grid (A1-A7, B1-B7, C1-C7)"""

    def __init__(self, start_x, start_y, song_list, selection_window_number=0):
        """Initialize the button grid

        Args:
            start_x: X position to start drawing the grid
            start_y: Y position to start drawing the grid
            song_list: List of song dictionaries from MusicMasterSongList.txt
            selection_window_number: Starting index for displaying songs (default 0)
        """
        self.start_x = start_x
        self.start_y = start_y
        self.song_list = song_list
        self.selection_window_number = selection_window_number

        # Load button images
        try:
            self.button_id_img = pygame.image.load(BUTTON_ID_BG)
            self.button_black_img = pygame.image.load(BUTTON_ID_BLACK_BG)
            self.selection_bg_img = pygame.image.load(SELECTION_TOP_BG)
        except pygame.error as e:
            print(f"Error loading button images: {e}")
            raise

        # Create fonts
        self.font_id = pygame.font.SysFont('Helvetica', 16, bold=True)
        self.font_song = pygame.font.SysFont('Helvetica', 12, bold=True)

        # Build button grid structure
        self.buttons = self._create_button_layout()

    def _create_button_layout(self):
        """Create the button grid layout data structure

        Returns:
            List of button definitions with positions and properties
        """
        buttons = []

        # Define button columns (A, B, C)
        columns = ['A', 'B', 'C']

        # Current Y position tracker
        current_y = self.start_y

        # Create 7 rows
        for row in range(1, 8):
            row_buttons = []
            current_x = self.start_x

            # Create 3 columns per row
            for col_idx, col_letter in enumerate(columns):
                # Calculate song index offset (A=0, B=14, C=28, then +2 per row)
                song_offset = (col_idx * 14) + ((row - 1) * 2)

                # ID Button (e.g., "A1", "B1", "C1")
                button_id = f"{col_letter}{row}"
                row_buttons.append({
                    'type': 'id',
                    'text': button_id,
                    'x': current_x,
                    'y': current_y,
                    'image': self.button_id_img,
                    'font': self.font_id
                })
                current_x += self.button_id_img.get_width()

                # Song Title Button
                song_idx = self.selection_window_number + song_offset
                title_text = ""
                if song_idx < len(self.song_list):
                    title_text = self.song_list[song_idx]['title'][:22]

                row_buttons.append({
                    'type': 'title',
                    'text': title_text,
                    'x': current_x,
                    'y': current_y,
                    'image': self.selection_bg_img,
                    'font': self.font_song,
                    'song_index': song_offset
                })
                current_x += self.selection_bg_img.get_width()

            buttons.append(row_buttons)
            current_y += self.button_id_img.get_height()

            # Add artist row (spacer + artist text)
            artist_row = []
            current_x = self.start_x

            for col_idx, col_letter in enumerate(columns):
                song_offset = (col_idx * 14) + ((row - 1) * 2)

                # Black spacer
                artist_row.append({
                    'type': 'spacer',
                    'text': '',
                    'x': current_x,
                    'y': current_y,
                    'image': self.button_black_img,
                    'font': self.font_id
                })
                current_x += self.button_black_img.get_width()

                # Artist name
                song_idx = self.selection_window_number + song_offset
                artist_text = ""
                if song_idx < len(self.song_list):
                    artist_text = self.song_list[song_idx]['artist'][:22]

                artist_row.append({
                    'type': 'artist',
                    'text': artist_text,
                    'x': current_x,
                    'y': current_y,
                    'image': self.selection_bg_img,
                    'font': self.font_song,
                    'song_index': song_offset
                })
                current_x += self.selection_bg_img.get_width()

            buttons.append(artist_row)
            current_y += self.button_black_img.get_height()

        return buttons

    def update_selection_window(self, new_selection_window_number):
        """Update the grid to show a different page of songs

        Args:
            new_selection_window_number: New starting index for songs
        """
        self.selection_window_number = new_selection_window_number
        # Rebuild the button layout with new song data
        self.buttons = self._create_button_layout()

    def draw(self, screen):
        """Draw all buttons in the grid

        Args:
            screen: Pygame surface to draw on
        """
        for row in self.buttons:
            for button in row:
                # Draw button background image
                screen.blit(button['image'], (button['x'], button['y']))

                # Draw button text if present
                if button['text']:
                    # Render text
                    text_color = (0, 0, 0)  # Black text
                    text_surface = button['font'].render(button['text'], True, text_color)

                    # Center text on button
                    text_rect = text_surface.get_rect()
                    button_rect = button['image'].get_rect()
                    text_rect.center = (
                        button['x'] + button_rect.width // 2,
                        button['y'] + button_rect.height // 2
                    )

                    screen.blit(text_surface, text_rect)

# ============================================================================
# SECTION 4: MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()  # Initialize mixer for sound

    # Create window (no title bar)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Convergence Jukebox")

    # Load background image
    try:
        background = pygame.image.load(BACKGROUND_IMAGE_PATH)
        # Scale to fit screen if necessary
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for: {BACKGROUND_IMAGE_PATH}")
        pygame.quit()
        sys.exit(1)

    # Load song list
    try:
        with open(SONG_LIST_PATH, 'r') as f:
            song_list = json.load(f)
        print(f"Loaded {len(song_list)} songs from {SONG_LIST_PATH}")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading song list: {e}")
        pygame.quit()
        sys.exit(1)

    # Load arrow button images
    try:
        arrow_left_img = pygame.image.load(ARROW_LEFT_IMG)
        arrow_right_img = pygame.image.load(ARROW_RIGHT_IMG)
    except pygame.error as e:
        print(f"Error loading arrow images: {e}")
        pygame.quit()
        sys.exit(1)

    # Load buzz sound
    try:
        buzz_sound = pygame.mixer.Sound(BUZZ_SOUND_PATH)
    except pygame.error as e:
        print(f"Error loading buzz sound: {e}")
        buzz_sound = None

    # Create button grid with song data
    try:
        button_grid = ButtonGrid(GRID_START_X, GRID_START_Y, song_list, selection_window_number=0)
    except pygame.error as e:
        print(f"Error creating button grid: {e}")
        pygame.quit()
        sys.exit(1)

    # Initialize selection window number
    selection_window_number = 0

    # Main loop
    clock = pygame.time.Clock()
    running = True

    print("Convergence Jukebox v0.90.05 - Arrow Key Navigation")
    print("Press ESC to exit, LEFT/RIGHT arrow keys to navigate")

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    # Navigate to next page (right arrow)
                    new_window_number = selection_window_number + 21
                    # Check if at end of list
                    if new_window_number + 20 >= len(song_list):
                        new_window_number = len(song_list) - 21
                        if buzz_sound:
                            buzz_sound.play()
                    selection_window_number = new_window_number
                    button_grid.update_selection_window(selection_window_number)
                elif event.key == pygame.K_LEFT:
                    # Navigate to previous page (left arrow)
                    new_window_number = selection_window_number - 21
                    # Check if at beginning of list
                    if new_window_number < 0:
                        new_window_number = 0
                        if buzz_sound:
                            buzz_sound.play()
                    selection_window_number = new_window_number
                    button_grid.update_selection_window(selection_window_number)

        # Draw background
        screen.blit(background, (0, 0))

        # Draw button grid on top of background
        button_grid.draw(screen)

        # Draw arrow buttons
        # Determine if arrows should be enabled/disabled
        left_enabled = selection_window_number > 0
        right_enabled = selection_window_number + 20 < len(song_list) - 1

        # Draw arrows (could add grayed out version for disabled state)
        screen.blit(arrow_left_img, (ARROW_LEFT_X, ARROW_LEFT_Y))
        screen.blit(arrow_right_img, (ARROW_RIGHT_X, ARROW_RIGHT_Y))

        # Update display
        pygame.display.flip()

        # Cap at 60 FPS
        clock.tick(60)

    # Cleanup
    pygame.quit()
    sys.exit(0)

# ============================================================================
# SECTION 5: PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()


# ============================================================================
# ORIGINAL FREESIMPLEGUI CODE FROM v0.83.60 (COMMENTED OUT FOR REFERENCE)
# ============================================================================

"""
All original code from version 0.83.60 has been preserved in the original file:
0.83.60 - Convergence-Jukebox-Full-2026.py

Button Grid Reference from jukebox_selection_screen_layout_module.py:
- 3 columns (A, B, C) × 7 rows (1-7) = 21 selection buttons
- Each button shows title (top row) and artist (bottom row)
- ID buttons: 30×26 pixels (button_id_bg.png)
- Black spacers: 30×26 pixels (button_id_black_bg.png)
- Song/artist displays: 22 char width (new_selection_top_bg.png)
- Grid positioned at relative_location=(162, 56)
- No padding between buttons (pad=(0,0))
- Fonts: Helvetica 16 bold (IDs), Helvetica 12 bold (songs/artists)
"""
