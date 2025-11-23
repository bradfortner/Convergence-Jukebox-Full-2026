"""
CONVERGENCE JUKEBOX - PYGAME MIGRATION VERSION
Version 0.90.0 - Pure Pygame Implementation (Step 1: Background Display)

This version begins the migration from FreeSimpleGUI to pure Pygame.

Migration Goals:
- Eliminate Pygame/Tkinter z-order conflicts
- Enable seamless rotating record popup integration
- Create foundation for future touchscreen/arcade features

Version 0.90.0 Changes:
- Created Pygame window with background image display
- Window: 1280x720, no title bar (NOFRAME)
- All FreeSimpleGUI code commented out for reference
- Clean slate for building Pygame interface section by section

Next Steps:
- Add selection buttons (a/b/c, 1-7) overlay
- Implement keyboard input handling
- Port remaining UI elements

Original Code Reference:
- All original 0.83.60 code is preserved at bottom of file for reference
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

# ============================================================================
# SECTION 3: MAIN APPLICATION
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

    # Main loop
    clock = pygame.time.Clock()
    running = True

    print("Convergence Jukebox v0.90.0 - Pygame Background Display")
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

        # Update display
        pygame.display.flip()

        # Cap at 60 FPS
        clock.tick(60)

    # Cleanup
    pygame.quit()
    sys.exit(0)

# ============================================================================
# SECTION 4: PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()


# ============================================================================
# ORIGINAL FREESIMPLEGUI CODE FROM v0.83.60 (COMMENTED OUT FOR REFERENCE)
# ============================================================================

"""
All original code from version 0.83.60 has been preserved in the original file:
0.83.60 - Convergence-Jukebox-Full-2026.py

This includes:
- All imports (FreeSimpleGUI, VLC, PIL, etc.)
- JukeboxEngine class (music playback management)
- GUI layout modules and functions
- Event handling and main loop
- Helper functions and utilities
- All module imports and dependencies

During migration, refer to 0.83.60 for:
- Button positions and layout coordinates
- Keyboard event mappings
- Music engine integration points
- Display update logic
- Search window functionality
"""
