"""
================================================================================
RECORD ARTIST TITLES GENERATOR - 1.6
================================================================================

OVERVIEW:
This script generates a custom vinyl record label image by overlaying artist and
song titles onto a randomly selected blank record template. It randomly selects
one record from the artist/song data in a pickle file, creates a single PNG file,
and displays an animated rotating visualization of the record.

KEY FEATURES:
- Random label selection: Randomly chooses one blank record label from available templates
- Font color auto-detection: Selects white font for labels starting with "w_", black otherwise
- Random selection: Randomly chooses one record from the entire dataset
- Single output: Generates exactly one record label image per execution
- Auto-fit text: Dynamically adjusts font sizes to fit text within defined areas
- Text wrapping: Breaks long titles into multiple lines with proper formatting
- Centered text: All text is horizontally centered on the record label
- Fixed filename: Output file is always named final_record_pressing.png
- Threaded animation: Displays rotating record animation after generation

INPUT (REQUIRED FILES):
- artist_song.pkl: Pickle file containing list of [artist, song] tuples
- record_labels/blank_record_labels/*.png: Blank record label templates
  (Files starting with "w_" will use white font; others use black font)

OUTPUT:
- final_record_pressing.png: Single randomly-selected record label image
  (saved to current directory, overwrites previous output)
- Animated display: Shows rotating record at 45 fps with dark grey background

ANIMATION DETAILS:
- Frame rate: 45 fps
- Rotation speed: 360° per second (8° per frame)
- Background: Dark grey (64, 64, 64)
- Close window to stop animation

CONFIGURATION:
- Font: OpenSans ExtraBold (fonts/OpenSans-ExtraBold.ttf)
- Max width: 300 pixels for text
- Start font size: 28pt, minimum: 16pt
- Song text: Up to 2 lines, positioned at vertical center + 90px
- Artist text: Up to 2 lines, positioned at vertical center + 125px
- Font color: White for "w_*" labels, black for others

CHANGES FROM 1.5:
- Random label selection: Now selects random .png from blank_record_labels directory
- Font color detection: Automatically sets white/black font based on label filename
- Removed hardcoded test_record_blank_record.png dependency

================================================================================
"""

import pickle
import random
import threading
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from rotate_record_module import display_record_playing


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


# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Load artist and song data from pickle file
print("Loading artist and song data...")
with open('artist_song.pkl', 'rb') as f:
    artist_song = pickle.load(f)
print(f"Loaded {len(artist_song)} records")

# Randomly select one record from the dataset
selected_idx = random.randint(0, len(artist_song) - 1)
artist, song = artist_song[selected_idx]
print(f"Randomly selected record #{selected_idx}: {artist} - {song}")

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
font_color = "white" if selected_label.startswith("w_") else "black"
print(f"Font color mode: {font_color.upper()}")

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

print(f"Creating record label...")
print("-" * 80)

# Create a working copy of the base image
img = base_img.copy()
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

# Save with optimization and compression to maintain quality antialiased fonts
img.save(filename, optimize=True, compress_level=9)
print(f"  Saved: {filename}")

# Final completion message
print("-" * 80)
print(f"\nRecord generation complete!")
print(f"Selected label: {selected_label}")
print(f"Font color: {font_color.upper()}")
print(f"Successfully created 1 random record label image")
print(f"Output location: {filename} in current directory")

# Launch animation in separate thread
print("\nLaunching record player animation...")
animation_thread = threading.Thread(target=display_record_playing, args=(filename,), daemon=True)
animation_thread.start()

# Keep the main thread alive while animation runs
try:
    animation_thread.join()
except KeyboardInterrupt:
    print("\nAnimation interrupted by user")
