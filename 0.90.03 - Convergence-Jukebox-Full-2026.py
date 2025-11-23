"""
CONVERGENCE JUKEBOX - PYGAME MIGRATION VERSION
Version 0.90.03 - Pure Pygame Implementation (Step 2c: Adjust Button Grid Position)

This version begins the migration from FreeSimpleGUI to pure Pygame.

Migration Goals:
- Eliminate Pygame/Tkinter z-order conflicts
- Enable seamless rotating record popup integration
- Create foundation for future touchscreen/arcade features

Version 0.90.03 Changes:
- Adjusted button grid position to (430, 250) for testing alignment
- Testing positioning against background image

Next Steps:
- Fine-tune button grid positioning
- Add keyboard input handling for button selection
- Implement song data loading and display
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

# ============================================================================
# SECTION 2: CONSTANTS
# ============================================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_IMAGE_PATH = "images/Full Jukebox Background Master 2026.png"

# Button grid layout constants
GRID_START_X = 430  # Testing position for alignment with background
GRID_START_Y = 250

# Button image paths
BUTTON_ID_BG = "images/button_id_bg.png"
BUTTON_ID_BLACK_BG = "images/button_id_black_bg.png"
SELECTION_TOP_BG = "images/new_selection_top_bg.png"

# ============================================================================
# SECTION 3: BUTTON GRID CLASS
# ============================================================================

class ButtonGrid:
    """Manages the selection button grid (A1-A7, B1-B7, C1-C7)"""

    def __init__(self, start_x, start_y):
        """Initialize the button grid

        Args:
            start_x: X position to start drawing the grid
            start_y: Y position to start drawing the grid
        """
        self.start_x = start_x
        self.start_y = start_y

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
                row_buttons.append({
                    'type': 'title',
                    'text': f'Song Title {song_offset}',  # Placeholder
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
                artist_row.append({
                    'type': 'artist',
                    'text': f'Artist {song_offset}',  # Placeholder
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

    # Create button grid
    try:
        button_grid = ButtonGrid(GRID_START_X, GRID_START_Y)
    except pygame.error as e:
        print(f"Error creating button grid: {e}")
        pygame.quit()
        sys.exit(1)

    # Main loop
    clock = pygame.time.Clock()
    running = True

    print("Convergence Jukebox v0.90.03 - Testing Button Grid Position (430, 250)")
    print("Press ESC to exit")

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Draw background
        screen.blit(background, (0, 0))

        # Draw button grid on top of background
        button_grid.draw(screen)

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
