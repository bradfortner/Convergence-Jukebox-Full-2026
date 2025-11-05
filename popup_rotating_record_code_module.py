"""
Rotating Record Pop-up Code Module
Displays a rotating record during playback based on idle time and song progress
Dynamically generates record images with song title and artist information

All popup parameters are defined here to keep popup logic self-contained.
"""
from pathlib import Path
import os
import time
import random
import threading
import pygame
from PIL import Image, ImageDraw, ImageFont
import FreeSimpleGUI as sg

# ============================================================================
# POPUP CONFIGURATION PARAMETERS
# All timing and behavior parameters are defined here for easy customization
# ============================================================================

# Time in seconds after playback starts before popup can appear
POPUP_MIN_PLAYBACK_TIME = 20

# Time in seconds of idle time (no keypresses) required before popup appears
POPUP_MIN_IDLE_TIME = 20

# Seconds remaining in song threshold - popup closes when song has <= this time remaining
POPUP_CLOSE_SECONDS_REMAINING = 5

# DEPRECATED: Default song duration in seconds (fallback if duration cannot be parsed from metadata)
# NOTE: Duration should ALWAYS be obtained from VLC metadata (jukebox.song_duration)
#       which contains the actual song duration from the media file.
#       At worst, the popup will close when the song ends naturally via the time_remaining check.
#       This fallback should not be needed in normal operation.
# POPUP_DEFAULT_SONG_DURATION = 600

# Popup window properties
POPUP_WINDOW_TITLE = ''  # Empty = no title bar
POPUP_WINDOW_LOCATION = (730, 265)  # (x, y) position on screen
POPUP_WINDOW_BACKGROUND = 'black'
POPUP_WINDOW_NO_TITLEBAR = True
POPUP_WINDOW_KEEP_ON_TOP = True

# Record generation settings
BLANK_RECORDS_DIR = "record_labels/blank_record_labels"
BACKGROUND_PATH = "images/45rpm_background.png"
FONT_PATH = "fonts/OpenSans-ExtraBold.ttf"
OUTPUT_FILENAME = 'final_record_pressing.png'
COMPOSITE_FILENAME = 'final_record_with_background.png'

# Text rendering configuration
MAX_TEXT_WIDTH = 300               # Maximum width for wrapped text (pixels)
SONG_Y = 90                        # Y position offset for song title (from center)
ARTIST_Y = 110                     # Y position offset for artist name (from center)
SONG_LINE_HEIGHT = 25              # Vertical spacing between song title lines
ARTIST_LINE_HEIGHT = 30            # Vertical spacing between artist name lines
POPUP_WIDTH = 420                  # Popup window width in pixels
POPUP_HEIGHT = 420                 # Popup window height in pixels

# PNG generation settings
PNG_OUTPUT_WIDTH = 750             # PNG image generation width in pixels
PNG_OUTPUT_HEIGHT = 750            # PNG image generation height in pixels

# Pygame rotation animation settings
RECORD_ROTATION_FPS = 30           # Frames per second for rotation animation
RECORD_ROTATION_SPEED = 8          # Degrees per frame (240° per second at 30fps = 8°/frame)
PYGAME_BACKGROUND_COLOR = (64, 64, 64)  # Dark grey background for pygame window

# ============================================================================


def wrap_text(text, font, max_width, draw):
    """
    Wrap text to fit within a specified pixel width.

    Breaks text into lines by word boundaries to ensure no line exceeds
    the maximum width. Uses the font metrics to calculate actual pixel widths.

    Args:
        text (str): The text to wrap
        font (ImageFont): Pillow font object for measuring text width
        max_width (int): Maximum width in pixels for each line
        draw (ImageDraw): Pillow draw object for text metrics

    Returns:
        list: List of wrapped text lines, each within max_width
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Test if adding the next word would exceed max width
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            # Word fits on current line
            current_line = test_line
        else:
            # Word doesn't fit, save current line and start new one
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    # Append any remaining text
    if current_line:
        lines.append(current_line.strip())

    return lines


def fit_text_to_width(text, base_font_path, start_size, max_width, max_lines, draw):
    """
    Auto-fit text by reducing font size until it fits within constraints.

    Iteratively reduces font size by 2pt increments until text fits within
    the specified width and line limits. Prefers single-line text, but allows
    up to max_lines if necessary.

    Args:
        text (str): The text to fit
        base_font_path (str): Path to the TTF font file
        start_size (int): Starting font size in points
        max_width (int): Maximum width in pixels
        max_lines (int): Maximum number of lines allowed
        draw (ImageDraw): Pillow draw object for text metrics

    Returns:
        tuple: (list of wrapped lines, font size used, font object)
    """
    font_size = start_size
    min_font_size = 16  # Don't go smaller than 16pt

    while font_size >= min_font_size:
        # Create font at current size
        font = ImageFont.truetype(base_font_path, font_size)
        lines = wrap_text(text, font, max_width, draw)

        # Prefer single line - return immediately if text fits on one line
        if len(lines) == 1:
            return lines, font_size, font

        # If text fits within max_lines, check if we should try smaller font
        if len(lines) <= max_lines:
            # Test if reducing font size would still fit
            test_font = ImageFont.truetype(base_font_path, font_size - 2)
            test_lines = wrap_text(text, test_font, max_width, draw)
            if len(test_lines) <= max_lines:
                # Can fit with smaller font, so keep reducing
                font_size -= 2
                continue
            else:
                # Current size is good, smaller size would break max_lines
                return lines, font_size, font

        # Text doesn't fit, reduce size and try again
        font_size -= 2

    # Last resort - use minimum font size
    font = ImageFont.truetype(base_font_path, min_font_size)
    return wrap_text(text, font, max_width, draw), min_font_size, font


def rotate_record_pygame(image_path, rotation_stop_flag, window_x, window_y, window_width, window_height, no_titlebar=True):
    """
    Rotate a record image in real-time using pygame with specified window parameters.

    Displays the record image in a pygame window with smooth rotation animation
    at 30 FPS. Respects the specified position, size, and titlebar settings.

    Args:
        image_path: Path to the record image file to rotate
        rotation_stop_flag: threading.Event to signal when to stop rotation
        window_x: X coordinate for window position
        window_y: Y coordinate for window position
        window_width: Width of the pygame window
        window_height: Height of the pygame window
        no_titlebar: If True, attempts to create borderless window
    """
    try:
        print(f"\n=== rotate_record_pygame THREAD STARTED ===")
        print(f"Loading image: {image_path}")

        # Load image with PIL
        pil_image = Image.open(image_path)

        # Convert to RGB if necessary (ensures compatibility)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Set window position BEFORE pygame initialization
        import sys
        import ctypes
        print(f"Setting window position to ({window_x}, {window_y})")
        import os as os_module
        os.environ['SDL_WINDOWPOS'] = f'{window_x},{window_y}'

        # Initialize pygame
        pygame.init()

        # Create window with specified size (position may vary by OS)
        if no_titlebar:
            # Create borderless window
            screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
        else:
            screen = pygame.display.set_mode((window_width, window_height))

        pygame.display.set_caption("Record Playing")

        # Now forcefully move the window to correct position on Windows
        if sys.platform == 'win32':
            try:
                import time as time_module
                time_module.sleep(0.1)

                # Get the actual window handle from pygame
                wm_info = pygame.display.get_wm_info()
                if 'window' in wm_info:
                    hwnd = wm_info['window']
                    print(f"Got window handle: {hwnd}")

                    # Move the window to the specified position
                    # SWP_SHOWWINDOW = 0x40 to ensure window is shown
                    result = ctypes.windll.user32.SetWindowPos(hwnd, 0, window_x, window_y, window_width, window_height, 0x40)
                    if result:
                        print(f"Window successfully moved to ({window_x}, {window_y})")
                    else:
                        print(f"SetWindowPos returned 0 - may indicate failure")
                else:
                    print("Could not get window handle from pygame")
            except Exception as e:
                print(f"Error moving window: {e}")

        # Convert PIL image to pygame surface using raw bytes
        # This preserves exact color values without any compression or color space conversion
        raw_bytes = pil_image.tobytes()
        original_surface = pygame.image.fromstring(raw_bytes, pil_image.size, 'RGB')

        clock = pygame.time.Clock()

        # Get center for rotation
        center_x = window_width // 2
        center_y = window_height // 2

        angle = 0
        running = True

        print(f"Pygame record rotation started at ({window_x}, {window_y}) with size {window_width}x{window_height}")

        while running and not rotation_stop_flag.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Close popup on any keypress
                elif event.type == pygame.KEYDOWN:
                    print(f"Pygame: Keypress detected - closing popup")
                    rotation_stop_flag.set()
                    running = False

            # Fill background with dark grey
            screen.fill(PYGAME_BACKGROUND_COLOR)

            # Rotate the surface by the current angle
            rotated_surface = pygame.transform.rotate(original_surface, angle)

            # Get the rect of rotated surface and center it
            rotated_rect = rotated_surface.get_rect(center=(center_x, center_y))

            # Display rotated image
            screen.blit(rotated_surface, rotated_rect)
            pygame.display.flip()

            # Decrement angle: 240° per second at 30 fps = 8° per frame (reversed direction)
            angle = (angle - RECORD_ROTATION_SPEED) % 360

            # Maintain target FPS
            clock.tick(RECORD_ROTATION_FPS)

        pygame.quit()
        print("Pygame record rotation stopped")

    except Exception as e:
        print(f"Error in pygame record rotation: {e}")
        try:
            pygame.quit()
        except:
            pass


def display_rotating_record_popup(song_title, artist_name):
    """
    Display a rotating record popup during song playback using pygame.

    This popup dynamically generates a record image with the song title and artist
    and displays it in a pygame window with smooth rotation animation. The popup
    appears after specified idle time and playback duration, and closes on any
    keypress or when the song has specified seconds remaining.

    Args:
        song_title (str): The title of the currently playing song
        artist_name (str): The artist name for the currently playing song

    Returns:
        tuple: (rotation_stop_flag, popup_start_time) for lifecycle management
               - rotation_stop_flag: threading.Event to signal when to stop rotation
               - popup_start_time: time.time() when popup was created
    """

    try:
        print(f"\n=== POPUP FUNCTION CALLED with title='{song_title}', artist='{artist_name}' ===")

        # Get all .png files from the blank_record_labels directory
        print("Scanning for available record labels...")
        png_files = [f for f in os.listdir(BLANK_RECORDS_DIR) if f.endswith('.png')]

        if not png_files:
            raise FileNotFoundError(f"No .png files found in {BLANK_RECORDS_DIR}")

        print(f"Found {len(png_files)} available record labels")

        # Randomly select one blank record label
        selected_label = random.choice(png_files)
        label_path = os.path.join(BLANK_RECORDS_DIR, selected_label)

        print(f"Randomly selected label: {selected_label}")

        # Determine font color based on filename
        # If filename starts with "w_", use white font; otherwise use black
        # Use RGBA tuples (R, G, B, Alpha) where 255 = fully opaque
        font_color = (255, 255, 255, 255) if selected_label.startswith("w_") else (0, 0, 0, 255)
        color_mode = "WHITE" if selected_label.startswith("w_") else "BLACK"
        print(f"Font color mode: {color_mode}")

        # Load the selected record label image
        print("Loading blank record label template...")
        base_img = Image.open(label_path)

        # Resize template to PNG output dimensions for higher quality
        print(f"Resizing template to {PNG_OUTPUT_WIDTH}x{PNG_OUTPUT_HEIGHT}...")
        base_img = base_img.resize((PNG_OUTPUT_WIDTH, PNG_OUTPUT_HEIGHT), Image.Resampling.LANCZOS)

        # Get image dimensions for positioning calculations
        width, height = base_img.size

        # Calculate Y positions based on image center
        song_y = (height // 2) + SONG_Y
        artist_y = (height // 2) + ARTIST_Y

        print(f"Creating record label with {color_mode} text...")
        print("-" * 80)

        # Create a working copy of the base image and convert to RGBA
        img = base_img.copy()
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        draw = ImageDraw.Draw(img)

        # Auto-fit song title text
        # Start at 28pt, allow max 2 lines
        song_lines, song_font_size, song_font = fit_text_to_width(
            song_title, FONT_PATH, 28, MAX_TEXT_WIDTH, 2, draw
        )

        # Auto-fit artist name text
        # Start at 25pt, allow max 2 lines
        artist_lines, artist_font_size, artist_font = fit_text_to_width(
            artist_name, FONT_PATH, 25, MAX_TEXT_WIDTH, 2, draw
        )

        # Draw song title lines, centered horizontally
        for i, line in enumerate(song_lines):
            # Calculate width of this line to center it
            song_bbox = draw.textbbox((0, 0), line, font=song_font)
            song_width = song_bbox[2] - song_bbox[0]
            song_x = (width - song_width) // 2  # Center horizontally

            # Draw the line at calculated position with determined font color
            draw.text(
                (song_x, song_y + (i * SONG_LINE_HEIGHT)),
                line,
                font=song_font,
                fill=font_color
            )

        # Adjust artist Y position based on number of song lines
        # This prevents overlap if song title wraps to multiple lines
        artist_y_adjusted = artist_y + ((len(song_lines) - 1) * SONG_LINE_HEIGHT)

        # Draw artist name lines, centered horizontally
        for i, line in enumerate(artist_lines):
            # Calculate width of this line to center it
            artist_bbox = draw.textbbox((0, 0), line, font=artist_font)
            artist_width = artist_bbox[2] - artist_bbox[0]
            artist_x = (width - artist_width) // 2  # Center horizontally

            # Draw the line at calculated position with determined font color
            draw.text(
                (artist_x, artist_y_adjusted + (i * ARTIST_LINE_HEIGHT)),
                line,
                font=artist_font,
                fill=font_color
            )

        # Save the record image with fixed filename at high quality (800x800)
        img.save(OUTPUT_FILENAME, 'PNG')
        print(f"  Saved: {OUTPUT_FILENAME} at {PNG_OUTPUT_WIDTH}x{PNG_OUTPUT_HEIGHT}")

        # Use the record label for pygame rotation animation
        display_image = OUTPUT_FILENAME

        # Final completion message
        print("-" * 80)
        print(f"Record generation complete!")
        print(f"Selected label: {selected_label}")
        print(f"Font color: {color_mode}")
        print(f"Output location: {display_image} in current directory")

        # Store popup creation time for lifecycle management
        popup_start_time = time.time()

        # Create rotation stop flag for animation thread control
        rotation_stop_flag = threading.Event()

        # Extract window position from tuple
        window_x, window_y = POPUP_WINDOW_LOCATION

        # Start pygame rotation animation in background thread
        rotation_thread = threading.Thread(
            target=rotate_record_pygame,
            args=(
                display_image,
                rotation_stop_flag,
                window_x,
                window_y,
                POPUP_WIDTH,
                POPUP_HEIGHT,
                POPUP_WINDOW_NO_TITLEBAR
            ),
            daemon=True
        )
        rotation_thread.start()

        print("Pygame record rotation popup started")

        # Return rotation control flag and start time for lifecycle management
        return rotation_stop_flag, popup_start_time

    except Exception as e:
        print(f"Error displaying rotating record popup: {e}")
        import traceback
        traceback.print_exc()
        return None, None
