"""
Rotating Record Pop-up Code Module
Displays a rotating record during playback based on idle time and song progress
Dynamically generates record images with song title and artist information

All popup parameters are defined here to keep popup logic self-contained.
"""
import threading
from pathlib import Path
import os
import time
import random
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
POPUP_WINDOW_LOCATION = (500, 100)  # (x, y) position on screen
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
ARTIST_Y = 125                     # Y position offset for artist name (from center)
SONG_LINE_HEIGHT = 25              # Vertical spacing between song title lines
ARTIST_LINE_HEIGHT = 30            # Vertical spacing between artist name lines
POPUP_WIDTH = 610                  # Popup window width in pixels
POPUP_HEIGHT = 610                 # Popup window height in pixels

# Record rotation animation settings
RECORD_ROTATION_ENABLED = True     # Enable/disable record rotation animation
RECORD_ROTATION_FPS = 30           # Frames per second for rotation animation
RECORD_ROTATION_SPEED = 8          # Degrees per frame (240° per second at 30fps = 8°/frame)
RECORD_ROTATION_ANGLE_STEP = 15    # Generate rotated frames every N degrees for efficiency

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


def generate_rotated_frames(image_path):
    """
    Pre-generate all rotated frames for the record animation.

    Creates a cache of rotated images at RECORD_ROTATION_ANGLE_STEP degree
    intervals, eliminating the need to rotate on-the-fly during animation.

    Args:
        image_path: Path to the base record image

    Returns:
        list: List of PIL Image objects, one for each rotation angle
    """
    try:
        pil_image = Image.open(image_path)

        # Convert to RGB if necessary
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGB')

        frames = []
        num_frames = 360 // RECORD_ROTATION_ANGLE_STEP

        print(f"Pre-caching {num_frames} rotated frames for smooth animation...")

        for i in range(num_frames):
            angle = (i * RECORD_ROTATION_ANGLE_STEP) % 360
            rotated_img = pil_image.rotate(-angle, expand=False)
            frames.append(rotated_img)

        print(f"Frame caching complete: {num_frames} frames ready")
        return frames

    except Exception as e:
        print(f"Error generating rotated frames: {e}")
        return []


def rotate_record_animation(popup_window, image_key, image_path, rotation_stop_flag):
    """
    Continuously rotate the record image in the popup window using pre-cached frames.

    This function runs in a background thread and cycles through pre-generated
    rotated frames at the specified FPS and rotation speed, updating the popup display.
    This approach eliminates disk I/O and expensive rotation calculations per frame.

    Args:
        popup_window: FreeSimpleGUI Window object containing the image
        image_key: The key of the image element in the popup
        image_path: Path to the record image file to use for frame generation
        rotation_stop_flag: threading.Event to signal when to stop rotation
    """
    try:
        # Pre-generate all rotated frames
        frames = generate_rotated_frames(image_path)

        if not frames:
            print("Warning: No frames generated, animation cannot start")
            return

        frame_index = 0
        frame_count = 0
        frames_per_step = max(1, RECORD_ROTATION_SPEED // RECORD_ROTATION_ANGLE_STEP)

        # Temporary file for storing current frame
        temp_rotated_path = 'temp_rotated_record.png'

        while not rotation_stop_flag.is_set():
            # Get current frame from cache
            current_frame = frames[frame_index % len(frames)]

            # Save frame temporarily for display
            current_frame.save(temp_rotated_path, 'PNG')

            try:
                # Update popup image
                popup_window[image_key].update(filename=temp_rotated_path)
            except:
                # Popup may have closed
                break

            # Move to next frame(s) based on rotation speed
            frame_index += frames_per_step
            frame_count += 1

            # Sleep to maintain frame rate
            time.sleep(1.0 / RECORD_ROTATION_FPS)

        # Clean up temp file
        try:
            os.remove(temp_rotated_path)
        except:
            pass

    except Exception as e:
        print(f"Error in record rotation animation: {e}")


def display_rotating_record_popup(song_title, artist_name):
    """
    Display a rotating record popup during song playback.

    This popup dynamically generates a record image with the song title and artist,
    displays it as an animated popup that rotates continuously. The popup appears
    after specified idle time and playback duration, and closes on any keypress
    or when the song has specified seconds remaining. The record continuously
    rotates at the specified FPS and rotation speed.

    Args:
        song_title (str): The title of the currently playing song
        artist_name (str): The artist name for the currently playing song

    Returns:
        tuple: (popup_window, popup_start_time, rotation_stop_flag) for lifecycle management
               - popup_window: FreeSimpleGUI Window object
               - popup_start_time: time.time() when popup was created
               - rotation_stop_flag: threading.Event to signal when to stop rotation thread
    """

    try:
        # Get all .png files from the blank_record_labels directory
        print("\nScanning for available record labels...")
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
        # Start at 28pt, allow max 2 lines
        artist_lines, artist_font_size, artist_font = fit_text_to_width(
            artist_name, FONT_PATH, 28, MAX_TEXT_WIDTH, 2, draw
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

        # Save the record image with fixed filename
        img.save(OUTPUT_FILENAME, 'PNG')
        print(f"  Saved: {OUTPUT_FILENAME}")

        # Use the record label directly for faster rotation animation
        display_image = OUTPUT_FILENAME

        # Final completion message
        print("-" * 80)
        print(f"Record generation complete!")
        print(f"Selected label: {selected_label}")
        print(f"Font color: {color_mode}")
        print(f"Output location: {display_image} in current directory")

        # Display the popup as an interactive window that accepts keyboard input
        layout = [
            [sg.Image(filename=display_image, key='--ROTATING_RECORD_IMAGE--')]
        ]

        popup_window = sg.Window(
            POPUP_WINDOW_TITLE,
            layout,
            no_titlebar=POPUP_WINDOW_NO_TITLEBAR,
            keep_on_top=POPUP_WINDOW_KEEP_ON_TOP,
            location=POPUP_WINDOW_LOCATION,
            background_color=POPUP_WINDOW_BACKGROUND,
            margins=(0, 0),
            element_padding=(0, 0),
            finalize=True
        )

        # Bind keyboard input to the popup window
        popup_window.bind('<KeyPress>', '--ROTATING_RECORD_KEY--')
        popup_window.bind('<Escape>', '--ROTATING_RECORD_ESC--')

        # Store popup creation time for lifecycle management
        popup_start_time = time.time()

        print("Rotating record popup created and displayed")

        # Create rotation stop flag for animation thread control
        rotation_stop_flag = threading.Event()

        # Start rotation animation thread if enabled
        if RECORD_ROTATION_ENABLED:
            rotation_thread = threading.Thread(
                target=rotate_record_animation,
                args=(popup_window, '--ROTATING_RECORD_IMAGE--', display_image, rotation_stop_flag),
                daemon=True
            )
            rotation_thread.start()
            print("Record rotation animation started")

        # Return the popup window and rotation control for lifecycle management
        return popup_window, popup_start_time, rotation_stop_flag

    except Exception as e:
        print(f"Error displaying rotating record popup: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
