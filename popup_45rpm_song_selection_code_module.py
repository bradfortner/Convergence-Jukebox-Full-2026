"""
45RPM Song Selection Record Pop-up Code Module
Handles the display of 45rpm record labels with song selection information as animated popups
"""
import threading
import os
import random
import time
from PIL import Image, ImageDraw, ImageFont
import vlc
import FreeSimpleGUI as sg


def display_45rpm_popup(MusicMasterSongList, counter, jukebox_selection_window, add_credit_callback=None):
    """
    Display an animated 45rpm record popup with song title and artist information.

    This function creates a visual representation of a 45rpm record label with the
    selected song's title and artist, then displays it as an animated popup.

    Args:
        MusicMasterSongList (list): List containing song information dictionaries
        counter (int): Index of the current song in MusicMasterSongList
        jukebox_selection_window: The FreeSimpleGUI window object to hide/unhide

    Returns:
        None
    """

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


    # Record Title Name
    song = str(MusicMasterSongList[counter]['title'])
    # Record Artist Name
    artist = str(MusicMasterSongList[counter]['artist'])

    # Path to blank record labels directory
    blank_records_dir = "record_labels/blank_record_labels"

    # Get all .png files from the blank_record_labels directory
    print("\nScanning for available record labels...")
    png_files = [f for f in os.listdir(blank_records_dir) if f.endswith('.png')]

    if not png_files:
        raise FileNotFoundError(f"No .png files found in {blank_records_dir}")

    print(f"Found {len(png_files)} available record labels")

    # Randomly select one blank record label
    selected_label = random.choice(png_files)
    label_path = os.path.join(blank_records_dir, selected_label)

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

    # Configuration settings
    font_path = "fonts/OpenSans-ExtraBold.ttf"          # Font to use for text
    max_text_width = 300               # Maximum width for wrapped text (pixels)
    song_y = (height // 2) + 90        # Y position for song title (below center)
    artist_y = (height // 2) + 125     # Y position for artist name (below song)
    song_line_height = 25              # Vertical spacing between song title lines
    artist_line_height = 30            # Vertical spacing between artist name lines

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
        song, font_path, 28, max_text_width, 2, draw
    )

    # Auto-fit artist name text
    # Start at 28pt, allow max 2 lines
    artist_lines, artist_font_size, artist_font = fit_text_to_width(
        artist, font_path, 28, max_text_width, 2, draw
    )

    # Draw song title lines, centered horizontally
    for i, line in enumerate(song_lines):
        # Calculate width of this line to center it
        song_bbox = draw.textbbox((0, 0), line, font=song_font)
        song_width = song_bbox[2] - song_bbox[0]
        song_x = (width - song_width) // 2  # Center horizontally

        # Draw the line at calculated position with determined font color
        draw.text(
            (song_x, song_y + (i * song_line_height)),
            line,
            font=song_font,
            fill=font_color
        )

    # Adjust artist Y position based on number of song lines
    # This prevents overlap if song title wraps to multiple lines
    artist_y_adjusted = artist_y + ((len(song_lines) - 1) * song_line_height)

    # Draw artist name lines, centered horizontally
    for i, line in enumerate(artist_lines):
        # Calculate width of this line to center it
        artist_bbox = draw.textbbox((0, 0), line, font=artist_font)
        artist_width = artist_bbox[2] - artist_bbox[0]
        artist_x = (width - artist_width) // 2  # Center horizontally

        # Draw the line at calculated position with determined font color
        draw.text(
            (artist_x, artist_y_adjusted + (i * artist_line_height)),
            line,
            font=artist_font,
            fill=font_color
        )

    # Save the record image with fixed filename
    filename = 'final_record_pressing.png'

    # Save as PNG - keep the image as-is without any modifications
    img.save(filename, 'PNG')
    print(f"  Saved: {filename}")

    # Final completion message
    print("-" * 80)
    print(f"\nRecord generation complete!")
    print(f"Selected label: {selected_label}")
    print(f"Font color: {color_mode}")
    print(f"Successfully created 1 random record label image")
    print(f"Output location: {filename} in current directory")

    # Composite the record label with the background
    try:
        # Load the background image
        background_path = "images/45rpm_background.png"
        background = Image.open(background_path)

        # Load the record label
        record_label = Image.open(filename)

        # Convert both to RGBA if needed
        if background.mode != 'RGBA':
            background = background.convert('RGBA')
        if record_label.mode != 'RGBA':
            record_label = record_label.convert('RGBA')

        # Calculate position to center the record label on the background
        bg_width, bg_height = background.size
        record_width, record_height = record_label.size
        x_position = (bg_width - record_width) // 2
        y_position = (bg_height - record_height) // 2

        # Create composite image
        composite = background.copy()
        composite.paste(record_label, (x_position, y_position), record_label)

        # Resize the composite image to desired popup window size
        # Matches the now_playing popup dimensions
        popup_width = 610
        popup_height = 610
        composite = composite.resize((popup_width, popup_height), Image.LANCZOS)

        # Save the composite image
        composite_filename = 'final_record_with_background.png'
        composite.save(composite_filename, 'PNG')
        print(f"Composite image saved: {composite_filename} (resized to {popup_width}x{popup_height})")

    except Exception as e:
        print(f"Warning: Could not create composite image: {e}")
        composite_filename = filename  # Fall back to record label without background


    # Play success sound
    try:
        success_sound_path = 'jukebox_required_audio_files/success.mp3'
        if os.path.exists(success_sound_path):
            p = vlc.MediaPlayer(success_sound_path)
            p.play()
            # Give VLC time to initialize and start playing the audio
            time.sleep(0.5)
            print(f"Playing success sound: {success_sound_path}")
        else:
            print(f"Warning: Success sound file not found at {success_sound_path}")
    except Exception as e:
        print(f"Warning: Could not play success sound: {e}")

    # Display the popup as an interactive window that accepts keyboard input
    # This popup window is part of the main event loop (sg.read_all_windows())
    # and can handle 'x' key presses to update credits
    try:
        layout = [
            [sg.Image(filename=composite_filename, key='--POPUP_IMAGE--')]
        ]

        popup_window = sg.Window(
            '',  # No title
            layout,
            no_titlebar=True,
            keep_on_top=True,
            location=(825, 280),
            background_color='black',
            margins=(0, 0),
            element_padding=(0, 0),
            finalize=True
        )

        # Bind keyboard input to the popup window
        popup_window.bind('<x>', '--POPUP_X_PRESSED--')
        popup_window.bind('<Escape>', '--POPUP_ESC--')

        # Store popup creation time for auto-close after 4 seconds
        # Extended to 4 seconds to allow success.mp3 audio to play fully
        popup_start_time = time.time()
        popup_duration = 4.0

        # Return the popup window to be processed by main event loop
        # The popup will be included in sg.read_all_windows() reads
        return popup_window, popup_start_time, popup_duration

    except Exception as e:
        print(f"Error displaying record label popup: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
