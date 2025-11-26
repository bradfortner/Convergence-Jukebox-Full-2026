"""
CONVERGENCE JUKEBOX - PYGAME MIGRATION VERSION
Version 0.90.51 - Fix Genre Tag Duplicates

This version begins the migration from FreeSimpleGUI to pure Pygame.

Migration Goals:
- Eliminate Pygame/Tkinter z-order conflicts
- Enable seamless rotating record popup integration
- Create foundation for future touchscreen/arcade features

Version 0.90.51 Changes:
- FIXED duplicate genre tags in log output
- Normalizes all genre tags to lowercase for consistency
- Strips whitespace and filters empty strings
- Eliminates case variation duplicates (e.g., "boomr&b" vs "boomR&B")

Version 0.90.50 Changes:
- FIXED genre logging to extract individual genre tags (not combinations)
- Splits comment field by spaces to get individual genre words
- Each unique genre tag listed only once in log
- Example: "classicrock canadian" logs as two separate entries

Version 0.90.49 Changes:
- ADDED genre list extraction and logging at startup
- Extracts all unique comment values (genres) from MusicMasterSongList
- Logs available genres to log.txt with timestamp
- Prints genre list to console for visibility
- Helps identify all music categories available in collection

Version 0.90.45 Changes:
- Reverted codebase to commit e7e4a9a (Version 0.90.41)
- Restored comprehensive logging system functionality
- Rolled back versions 0.90.42, 0.90.43, and 0.90.44

Version 0.90.41 Changes:
- ADDED comprehensive logging to log.txt for all jukebox events
- Log program startup with date/time
- Log songlist generation (new) and usage (existing)
- Log random playlist generation with active genre filters
- Log every random song played with title, artist
- Log every paid song played with title, artist
- Log quarter insertions (credits added)
- Log record image generation with song info and label .png filename
- Log when rotating record image pulled from cache
- Fixed AttributeError in logging code (used LOG_FILE_PATH constant)

Version 0.90.40 Changes:
- FIXED pygame double initialization crash (exit code 3489660927)
- Moved song list check/generation to BEFORE pygame.init() in main()
- Progress bar now gets exclusive pygame access, completes, then main app initializes
- Execution order: setup_files() → check/generate song list → pygame.init() → create window
- Progress bar thread calls pygame.init(), runs, then pygame.quit() cleanly
- Main app then calls pygame.init() fresh without conflicts
- Added detailed comments explaining why this order is critical
- Matches proven working pattern from original convergence_jukebox.py
- User experience: Progress bar shows → closes → main jukebox window opens

Technical Details:
- Pygame/SDL cannot be initialized twice (main thread + child thread)
- Progress bar must complete and call pygame.quit() before main init
- Song list generation now happens before any main pygame initialization
- Fatal error exit now uses sys.exit(1) instead of pygame.quit() (pygame not init yet)

Version 0.90.39 Changes:
- ADDED threaded pygame progress bar during MP3 metadata generation
- Progress bar shows real-time file count, percentage, and current filename
- Runs in separate thread to avoid blocking metadata extraction
- Displays "Loading Your Music Collection..." with green progress bar
- Updates on every file processed (not just every 100)
- Auto-closes after generation completes with 1 second pause
- Added import: MetadataProgressBar from metadata_progress_bar_module
- Modified generate_mp3_metadata() to initialize, update, and stop progress bar
- Removes need for console progress messages (GUI replaces text output)
- Matches original implementation from convergence_jukebox.py

Version 0.90.38 Changes:
- FIXED console flooding with VLC error messages
- Added '--quiet' and '--no-video' flags to VLC instance initialization
- Suppresses thousands of "stale plugins cache" error messages at startup
- Console output now clean and readable

Version 0.90.37 Changes:
- RESTORED song list generation functionality from original version (convergence_jukebox.py)
- Automatically scans music/ directory for MP3 files on first run
- Extracts ID3 metadata (title, artist, album, year, comment, duration) using TinyTag
- Generates MusicMasterSongList.txt with all song data
- Smart regeneration: only re-scans when MP3 file count changes
- Uses MusicMasterSongListCheck.txt to track song count for change detection
- Handles missing/corrupt metadata gracefully (continues processing)
- Duration stored in MM:SS format matching original implementation
- Console progress messages (no progress bar in Part 1)
- Jukebox now works out-of-box for new users with MP3 collection
- Added imports: glob, TinyTag
- Added constants: MUSIC_DIRECTORY, MUSIC_MASTER_SONG_LIST_CHECK_PATH
- Added functions: generate_mp3_metadata(), generate_music_master_song_list_dictionary()
- Modified main() startup to check/regenerate song list when needed

Version 0.90.32 Changes:
- RESTORED GenreFlags functionality from original version (0.83.60)
- Random playlist now respects genre filter settings from GenreFlagsList.txt
- Added 4 genre filter attributes to PlaybackEngine: genre0, genre1, genre2, genre3
- Added load_genre_flags() method to read filters from GenreFlagsList.txt
- Modified generate_random_playlist() to filter songs based on genre settings
- If all genres are "null": plays ALL songs (except 'norandom')
- If any genre is set: plays ONLY songs matching that genre in comment field
- Genre filters support OR logic (song matches if ANY filter matches)
- Displays active genre filters on startup with [GENRE FILTERS] prefix
- Warns if no songs match the current genre filter settings
- Example: GenreFlagsList.txt = ["rock", "null", "null", "null"] → only plays rock songs

Version 0.90.31 Changes:
- Added 3 more files to automatic initialization on startup
- YearRangeLabelList.txt: Year range to record label mapping (default: [])
- RecordLabelAssignList.txt: Artist to record label assignments (default: [])
- FullYearRangeLabelList.txt: Complete year range label data (default: [])
- Total files now checked/created: 7 (was 4 in v0.90.30)
- Added file path constants for all 3 new files
- Updated setup_files() docstring to reflect 7 files

Version 0.90.30 Changes:
- Restored file initialization from original version (0.83.60)
- Added setup_files() function to check and create required data files on startup
- Creates 4 files if missing: log.txt, GenreFlagsList.txt, MusicMasterSongListCheck.txt, PaidMusicPlayList.txt
- log.txt: Logs startup/restart events and playback errors
- GenreFlagsList.txt: Stores genre filter flags (default: ['null', 'null', 'null', 'null'])
- MusicMasterSongListCheck.txt: Tracks song list changes (default: [])
- PaidMusicPlayList.txt: Queue of user-selected paid songs (default: [])
- Prevents crashes on first run when files don't exist
- Added file path constants: LOG_FILE_PATH, GENRE_FLAGS_FILE_PATH, MUSIC_MASTER_SONG_LIST_CHECK_PATH
- setup_files() called at start of main() before pygame initialization

Version 0.90.29 Changes:
- Fixed search window header layout to match original exactly
- "Search For Title/Artist" text, magnifying glass, and search box now on same line
- All three elements on single white background bar (not separate boxes)
- Magnifying glass positioned between header text and search entry area
- Search text appears inline after magnifying glass (no separate box)
- Layout: [Search For Title] [🔍] [user typed text...]

Version 0.90.28 Changes:
- Added magnifying glass icon before search text box (matching original UI)
- Search text box now starts empty (no placeholder text)
- Fixed "Not On Jukebox" message to only appear when search finds no matches
- Message no longer displays on empty search box (only after typing 3+ characters)
- Restored original search window appearance and behavior
- Changes made to search_pygame_module.py only

Version 0.90.27 Changes:
- CRITICAL FIX: Rotating record popup no longer appears immediately after search closes
- Search window now tracks keypresses and returns last_keypress_time to main event loop
- Main file updates idle timer when search window closes to reset 20-second countdown
- User can now use search window without triggering popup when returning to main screen
- Modified search_pygame_module.py to track and return last keypress timestamp
- Modified main file to extract last_keypress_time from search result dict

Version 0.90.26 Changes:
- CRITICAL FIX: S key now works correctly in artist search
- S key logic reordered to check focus state FIRST before handling
- When typing directly: S adds 'S' to search query
- When navigating with arrows: S selects the focused button
- Typing "STONES" now works properly in artist search
- Removed duplicate S key handling code

Version 0.90.25 Changes:
- Added pygame-based title and artist search functionality
- Implemented optimized binary search for 16,000+ song library (~840x faster)
- Pre-sorted song lists at startup for O(log n) search performance
- Search only triggers when query >= 3 characters (reduces unnecessary searches)
- Full keyboard grid navigation (arrow keys, letters, numbers)
- Returns up to 5 results per search
- Press T for title search, A for artist search
- Replaces deprecated FreeSimpleGUI search module

Version 0.90.24 Changes:
- Added 45rpm song selection popup (appears when user selects a paid song)
- Generates custom record label with song title and artist
- Uses shared song_label_cache for consistency with rotating popup
- Respects artist-specific label assignments (RecordLabelAssignList.txt)
- Applies year-range filtering for era-appropriate labels
- Plays success sound effect on selection
- 3-second auto-close or ESC to dismiss
- Positioned at (32, 300) with 320x320 image size
- Green background behind record label

Version 0.90.23 Changes:
- Modified popup overlay behavior to hide buttons instead of dimming everything
- When popup appears: song buttons disappear, background/arrows/info screen stay visible
- Removed full-screen dark overlay (no longer dims entire interface)
- Matches behavior of previous FreeSimpleGUI version

Version 0.90.22 Changes:
- Added rotating record popup (idle screensaver) as overlay on main window
- Integrated song_label_cache_module for consistent label assignments
- Added record image generation with PIL (title/artist text rendering)
- Added Wurlitzer paddle-style tonearm animation
- Added idle timer tracking (20 second timeout)
- Popup shows after 20 seconds idle + 20 seconds playback
- Popup closes on any keypress or when song has <5 seconds remaining

Next Steps:
- Fine-tune search interface appearance
- Add more search options (genre, year, etc.)

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
import vlc
import time
import random
import math
import glob
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
from tinytag import TinyTag
from song_label_cache_module import get_or_assign_label
from search_pygame_module import display_search_popup
from metadata_progress_bar_module import MetadataProgressBar

# ============================================================================
# SECTION 2: CONSTANTS
# ============================================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_IMAGE_PATH = "images/Full Jukebox Background Master 2026.png"
SONG_LIST_PATH = "MusicMasterSongList.txt"
MUSIC_DIRECTORY = "music"
MUSIC_MASTER_SONG_LIST_CHECK_PATH = "MusicMasterSongListCheck.txt"
BUZZ_SOUND_PATH = "jukebox_required_audio_files/buzz.mp3"
SUCCESS_SOUND_PATH = "jukebox_required_audio_files/success.mp3"
PAID_MUSIC_PLAYLIST_PATH = "PaidMusicPlayList.txt"
CURRENT_SONG_PLAYING_PATH = "CurrentSongPlaying.txt"
LOG_FILE_PATH = "log.txt"
GENRE_FLAGS_FILE_PATH = "GenreFlagsList.txt"
MUSIC_MASTER_SONG_LIST_CHECK_PATH = "MusicMasterSongListCheck.txt"
YEAR_RANGE_LABEL_LIST_PATH = "YearRangeLabelList.txt"
RECORD_LABEL_ASSIGN_LIST_PATH = "RecordLabelAssignList.txt"
FULL_YEAR_RANGE_LABEL_LIST_PATH = "FullYearRangeLabelList.txt"

# Button grid layout constants
GRID_START_X = 465
GRID_START_Y = 218

# Arrow button constants
ARROW_RIGHT_X = 1015
ARROW_RIGHT_Y = 160
ARROW_LEFT_X = 520
ARROW_LEFT_Y = 160

# Control button constants
CONTROL_START_X = 455
CONTROL_START_Y = 586

# Info screen constants (relative_location=(-448, 0) → absolute position)
INFO_START_X = 32
INFO_START_Y = 100

# Color constants (RGB)
COLOR_SEAGREEN3 = (67, 205, 128)
COLOR_WHITE = (255, 255, 255)

# Button image paths
BUTTON_ID_BG = "images/button_id_bg.png"
BUTTON_ID_BLACK_BG = "images/button_id_black_bg.png"
SELECTION_TOP_BG = "images/new_selection_top_bg.png"
ARROW_LEFT_IMG = "images/lg_arrow_left.png"
ARROW_RIGHT_IMG = "images/lg_arrow_right.png"

# Control button image paths
A_BUTTON_IMG = "images/a_button.png"
B_BUTTON_IMG = "images/b_button.png"
C_BUTTON_IMG = "images/c_button.png"
NUM_BUTTON_IMG = "images/{}_button.png"  # Format with number 1-7
SELECT_BUTTON_IMG = "images/select_button.png"
CORRECT_BUTTON_IMG = "images/correct_button.png"
BLANK_BUTTON_IMG = "images/blank_button.png"

# Rotating record popup constants
POPUP_MIN_PLAYBACK_TIME = 20           # Song must play >= 20 seconds before popup
POPUP_MIN_IDLE_TIME = 20               # User idle >= 20 seconds before popup
POPUP_CLOSE_SECONDS_REMAINING = 5      # Close popup when song has <= 5 seconds left
BLANK_RECORDS_DIR = "record_labels/blank_record_labels"
FONT_PATH = "fonts/OpenSans-ExtraBold.ttf"
OUTPUT_FILENAME = 'final_record_pressing.png'
MAX_TEXT_WIDTH = 300                   # Maximum width for song title (pixels)
ARTIST_MAX_TEXT_WIDTH = 250            # Maximum width for artist name (pixels)
SONG_Y = 90                            # Y position offset for song title (from center)
ARTIST_Y = 120                         # Y position offset for artist name (from center)
SONG_LINE_HEIGHT = 25                  # Vertical spacing between song title lines
ARTIST_LINE_HEIGHT = 30                # Vertical spacing between artist name lines
PNG_OUTPUT_WIDTH = 750                 # PNG image generation width
PNG_OUTPUT_HEIGHT = 750                # PNG image generation height
RECORD_ROTATION_FPS = 15               # Frames per second for rotation
RECORD_ROTATION_SPEED = 5              # Degrees per frame (240° per second at 30fps)
PYGAME_BACKGROUND_COLOR = (64, 64, 64) # Dark grey background

# ============================================================================
# SECTION 3: UTILITY FUNCTIONS
# ============================================================================

def format_time_remaining(seconds):
    """Format seconds as MM:SS for display.

    Args:
        seconds (float): Number of seconds remaining

    Returns:
        str: Formatted time string like "03:45" or "00:12"
    """
    seconds = int(seconds)
    if seconds < 0:
        seconds = 0
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within a specified pixel width.

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
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines

def fit_text_to_width(text, base_font_path, start_size, max_width, max_lines, draw):
    """Auto-fit text by reducing font size until it fits within constraints.

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
    min_font_size = 16

    while font_size >= min_font_size:
        font = ImageFont.truetype(base_font_path, font_size)
        lines = wrap_text(text, font, max_width, draw)

        if len(lines) == 1:
            return lines, font_size, font

        if len(lines) <= max_lines:
            test_font = ImageFont.truetype(base_font_path, font_size - 2)
            test_lines = wrap_text(text, test_font, max_width, draw)
            if len(test_lines) <= max_lines:
                font_size -= 2
                continue
            else:
                return lines, font_size, font

        font_size -= 2

    font = ImageFont.truetype(base_font_path, min_font_size)
    return wrap_text(text, font, max_width, draw), min_font_size, font

def generate_record_image(song_title, artist_name, year=None):
    """Generate a record label image with song title and artist.

    Args:
        song_title (str): The song title
        artist_name (str): The artist name
        year (int/str, optional): The year the song was created

    Returns:
        str: Path to the generated record image file
    """
    try:
        # Get all .png files from blank_record_labels directory
        png_files = [f for f in os.listdir(BLANK_RECORDS_DIR) if f.endswith('.png')]

        if not png_files:
            print(f"No .png files found in {BLANK_RECORDS_DIR}")
            return None

        # Get or assign label using cache
        selected_label = get_or_assign_label(song_title, artist_name, png_files, year)
        label_path = os.path.join(BLANK_RECORDS_DIR, selected_label)

        # Determine font color based on filename
        font_color = (255, 255, 255, 255) if selected_label.startswith("w_") else (0, 0, 0, 255)

        # Load the selected record label image
        base_img = Image.open(label_path)
        base_img = base_img.resize((PNG_OUTPUT_WIDTH, PNG_OUTPUT_HEIGHT), Image.Resampling.LANCZOS)

        width, height = base_img.size
        song_y = (height // 2) + SONG_Y
        artist_y = (height // 2) + ARTIST_Y

        # Create working copy
        img = base_img.copy()
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        draw = ImageDraw.Draw(img)

        # Auto-fit song title text
        song_lines, song_font_size, song_font = fit_text_to_width(
            song_title, FONT_PATH, 28, MAX_TEXT_WIDTH, 2, draw
        )

        # Auto-fit artist name text
        artist_lines, artist_font_size, artist_font = fit_text_to_width(
            artist_name, FONT_PATH, 25, ARTIST_MAX_TEXT_WIDTH, 2, draw
        )

        # Draw song title lines, centered
        for i, line in enumerate(song_lines):
            song_bbox = draw.textbbox((0, 0), line, font=song_font)
            song_width = song_bbox[2] - song_bbox[0]
            song_x = (width - song_width) // 2
            draw.text((song_x, song_y + (i * SONG_LINE_HEIGHT)), line, font=song_font, fill=font_color)

        # Adjust artist Y position based on number of song lines
        artist_y_adjusted = artist_y + ((len(song_lines) - 1) * SONG_LINE_HEIGHT)

        # Draw artist name lines, centered
        for i, line in enumerate(artist_lines):
            artist_bbox = draw.textbbox((0, 0), line, font=artist_font)
            artist_width = artist_bbox[2] - artist_bbox[0]
            artist_x = (width - artist_width) // 2
            draw.text((artist_x, artist_y_adjusted + (i * ARTIST_LINE_HEIGHT)), line, font=artist_font, fill=font_color)

        # Save the record image
        img.save(OUTPUT_FILENAME, 'PNG')
        print(f"Generated record image: {OUTPUT_FILENAME}")

        # Log record image creation
        from datetime import datetime
        now = datetime.now().replace(microsecond=0)
        log_date = now.strftime("%Y-%m-%d")
        log_time = now.strftime("%H:%M:%S")
        try:
            with open('log.txt', 'a') as log:
                log.write(f'\n{log_date}, {log_time}, {song_title}, {artist_name}, New Record Image Pressed, {selected_label}')
        except IOError as log_error:
            print(f"[ERROR] Failed to write to log.txt: {log_error}")

        return OUTPUT_FILENAME

    except Exception as e:
        print(f"Error generating record image: {e}")
        return None

# ============================================================================
# SECTION 4: TONEARM ANIMATION CLASSES
# ============================================================================

class ToneArmState(Enum):
    """States for tonearm animation."""
    PARKED = "parked"
    SWINGING_OUT = "swinging_out"
    LOWERING = "lowering"
    PLAYING = "playing"
    LIFTING = "lifting"
    RETURNING = "returning"

class ToneArm:
    """Base class for turntable tonearm with animation states."""

    def __init__(self, x, y, length=200):
        self.pivot_x = x
        self.pivot_y = y
        self.length = length

        self.play_angle = -22
        self.end_angle = 5
        self.current_angle = -22
        self.target_angle = -22

        self.state = ToneArmState.PLAYING
        self.current_height = 0

        self.play_wobble = 0
        self.wobble_timer = 0

        self.needle_color = (200, 50, 50)

    def is_playing(self):
        return True

    def get_state(self):
        return self.state

    def update(self, dt):
        self.wobble_timer += dt * 3
        self.play_wobble = math.sin(self.wobble_timer) * 0.5

        angle_diff = self.target_angle - self.current_angle
        if abs(angle_diff) > 0.1:
            move_speed = 5
            if angle_diff > 0:
                self.current_angle += min(move_speed * dt, angle_diff)
            else:
                self.current_angle += max(-move_speed * dt, angle_diff)

    def draw(self, surface):
        pass

class WurlitzerPaddleToneArm(ToneArm):
    """Authentic Wurlitzer jukebox tonearm with paddle design."""

    def __init__(self, x, y, length=180):
        super().__init__(x, y, length)

        self.arm_length = length * 0.85
        self.head_radius = length * 0.15
        self.base_width = 70
        self.top_width = 70

        self.play_angle = -8
        self.end_angle = 12
        self.current_angle = -22
        self.target_angle = -22

        self.arm_color = (140, 140, 145)
        self.arm_shadow = (100, 100, 105)
        self.arm_highlight = (170, 170, 175)
        self.head_color = (130, 130, 135)
        self.base_color = (120, 120, 125)
        self.pivot_brass = (180, 150, 100)

    def draw(self, surface):
        pivot_x = self.pivot_x
        pivot_y = self.pivot_y + self.current_height

        angle_rad = math.radians(self.current_angle + self.play_wobble)

        head_x = pivot_x + self.arm_length * math.sin(angle_rad)
        head_y = pivot_y - self.arm_length * math.cos(angle_rad)

        base_half = self.base_width / 2
        perp_angle = angle_rad + math.pi / 2

        base_left_x = pivot_x + base_half * math.cos(perp_angle)
        base_left_y = pivot_y + base_half * math.sin(perp_angle)
        base_right_x = pivot_x - base_half * math.cos(perp_angle)
        base_right_y = pivot_y - base_half * math.sin(perp_angle)

        top_half = self.top_width / 2
        top_offset = self.arm_length * 0.85

        top_center_x = pivot_x + top_offset * math.sin(angle_rad)
        top_center_y = pivot_y - top_offset * math.cos(angle_rad)

        top_left_x = top_center_x + top_half * math.cos(perp_angle)
        top_left_y = top_center_y + top_half * math.sin(perp_angle)
        top_right_x = top_center_x - top_half * math.cos(perp_angle)
        top_right_y = top_center_y - top_half * math.sin(perp_angle)

        # Draw base flare
        base_flare = self.base_width * 0.8
        base_points = []
        for i in range(8):
            angle_offset = (i / 7 - 0.5) * math.pi * 0.6
            base_angle = perp_angle + angle_offset
            bx = pivot_x + base_flare * math.cos(base_angle)
            by = pivot_y + base_flare * math.sin(base_angle)
            base_points.append((int(bx), int(by)))

        pygame.draw.polygon(surface, self.base_color, base_points)
        pygame.draw.polygon(surface, self.arm_shadow, base_points, 2)

        # Draw paddle arm
        paddle_points = [
            (int(base_left_x), int(base_left_y)),
            (int(base_right_x), int(base_right_y)),
            (int(top_right_x), int(top_right_y)),
            (int(top_left_x), int(top_left_y))
        ]

        pygame.draw.polygon(surface, self.arm_color, paddle_points)
        pygame.draw.line(surface, self.arm_highlight, (int(base_left_x), int(base_left_y)), (int(top_left_x), int(top_left_y)), 35)
        pygame.draw.line(surface, self.arm_shadow, (int(base_right_x), int(base_right_y)), (int(top_right_x), int(top_right_y)), 35)

        # Draw head
        pygame.draw.circle(surface, self.head_color, (int(head_x), int(head_y)), int(self.head_radius))
        pygame.draw.circle(surface, self.arm_shadow, (int(head_x), int(head_y)), int(self.head_radius), 2)

        # Draw grooves
        groove_length = self.head_radius * 0.6
        groove_spacing = self.head_radius * 0.25
        groove_angle = angle_rad

        for offset in [-groove_spacing, groove_spacing]:
            groove_start_x = head_x + offset * math.cos(perp_angle) - (groove_length/2) * math.sin(groove_angle)
            groove_start_y = head_y + offset * math.sin(perp_angle) + (groove_length/2) * math.cos(groove_angle)
            groove_end_x = head_x + offset * math.cos(perp_angle) + (groove_length/2) * math.sin(groove_angle)
            groove_end_y = head_y + offset * math.sin(perp_angle) - (groove_length/2) * math.cos(groove_angle)
            pygame.draw.line(surface, self.arm_shadow, (int(groove_start_x), int(groove_start_y)), (int(groove_end_x), int(groove_end_y)), 2)

        # Draw needle
        needle_length = self.head_radius * 0.4
        needle_x = head_x + (self.head_radius + needle_length) * math.sin(angle_rad)
        needle_y = head_y - (self.head_radius + needle_length) * math.cos(angle_rad)
        pygame.draw.line(surface, (80, 80, 85), (head_x, head_y), (needle_x, needle_y), 3)
        pygame.draw.circle(surface, self.needle_color, (int(needle_x), int(needle_y)), 3)

        # Draw pivots
        pivot_pos_y = pivot_y - self.arm_length * 0.3
        pivot_pos_x = pivot_x + self.arm_length * 0.3 * math.sin(angle_rad)
        pygame.draw.circle(surface, self.pivot_brass, (int(pivot_pos_x), int(pivot_pos_y)), 6)
        pygame.draw.circle(surface, (150, 120, 80), (int(pivot_pos_x), int(pivot_pos_y)), 6, 2)
        pygame.draw.circle(surface, (100, 80, 50), (int(pivot_pos_x), int(pivot_pos_y)), 2)

        pygame.draw.circle(surface, self.base_color, (pivot_x, pivot_y), 12)
        pygame.draw.circle(surface, self.arm_shadow, (pivot_x, pivot_y), 12, 2)
        pygame.draw.circle(surface, (80, 80, 85), (pivot_x, pivot_y), 5)
        pygame.draw.circle(surface, (60, 60, 65), (pivot_x, pivot_y), 2)

# ============================================================================
# SECTION 4.5: SONG SELECTION POPUP FUNCTIONS
# ============================================================================

def wrap_text(text, font, max_width, draw):
    """
    Wrap text to fit within a specified pixel width.

    Breaks text into lines by word boundaries to ensure no line exceeds
    the maximum width. Uses the font metrics to calculate actual pixel widths.
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines


def fit_text_to_width(text, base_font_path, start_size, max_width, max_lines, draw):
    """
    Auto-fit text by reducing font size until it fits within constraints.

    Iteratively reduces font size by 2pt increments until text fits within
    the specified width and line limits.
    """
    font_size = start_size
    min_font_size = 16

    while font_size >= min_font_size:
        font = ImageFont.truetype(base_font_path, font_size)
        lines = wrap_text(text, font, max_width, draw)

        if len(lines) == 1:
            return lines, font_size, font

        if len(lines) <= max_lines:
            test_font = ImageFont.truetype(base_font_path, font_size - 2)
            test_lines = wrap_text(text, test_font, max_width, draw)
            if len(test_lines) <= max_lines:
                font_size -= 2
                continue
            else:
                return lines, font_size, font

        font_size -= 2

    font = ImageFont.truetype(base_font_path, min_font_size)
    return wrap_text(text, font, max_width, draw), min_font_size, font


def generate_selection_record_label(song_title, artist_name, available_labels, year=None):
    """
    Generate a 45rpm record label image for song selection popup.

    Creates a custom record label with the song title and artist name,
    using the shared label cache to ensure consistency with the rotating popup.

    Args:
        song_title: Title of the song
        artist_name: Name of the artist
        available_labels: List of available label PNG files
        year: Year of the song (optional, for era filtering)

    Returns:
        Path to the generated composite image file
    """
    print(f"\n[SELECTION POPUP] Generating label for: {song_title} - {artist_name}")

    # Get or assign label using shared cache
    selected_label = get_or_assign_label(song_title, artist_name, available_labels, year)
    label_path = os.path.join("record_labels/blank_record_labels", selected_label)

    # Determine font color based on filename
    font_color = (255, 255, 255, 255) if selected_label.startswith("w_") else (0, 0, 0, 255)
    color_mode = "WHITE" if selected_label.startswith("w_") else "BLACK"
    print(f"[SELECTION POPUP] Using label: {selected_label} ({color_mode} text)")

    # Load the blank record label
    base_img = Image.open(label_path)
    width, height = base_img.size

    # Configuration
    font_path = "fonts/OpenSans-ExtraBold.ttf"
    max_text_width = 300
    artist_max_text_width = 250
    song_y = (height // 2) + 90
    artist_y = (height // 2) + 120
    song_line_height = 25
    artist_line_height = 30

    # Create working copy
    img = base_img.copy()
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    draw = ImageDraw.Draw(img)

    # Auto-fit song title text
    song_lines, song_font_size, song_font = fit_text_to_width(
        song_title, font_path, 28, max_text_width, 2, draw
    )

    # Auto-fit artist name text
    artist_lines, artist_font_size, artist_font = fit_text_to_width(
        artist_name, font_path, 25, artist_max_text_width, 2, draw
    )

    # Draw song title lines (centered)
    for i, line in enumerate(song_lines):
        song_bbox = draw.textbbox((0, 0), line, font=song_font)
        song_width = song_bbox[2] - song_bbox[0]
        song_x = (width - song_width) // 2
        draw.text(
            (song_x, song_y + (i * song_line_height)),
            line,
            font=song_font,
            fill=font_color
        )

    # Adjust artist Y position based on song lines
    artist_y_adjusted = artist_y + ((len(song_lines) - 1) * song_line_height)

    # Draw artist name lines (centered)
    for i, line in enumerate(artist_lines):
        artist_bbox = draw.textbbox((0, 0), line, font=artist_font)
        artist_width = artist_bbox[2] - artist_bbox[0]
        artist_x = (width - artist_width) // 2
        draw.text(
            (artist_x, artist_y_adjusted + (i * artist_line_height)),
            line,
            font=artist_font,
            fill=font_color
        )

    # Save the record image
    filename = 'final_record_pressing.png'
    img.save(filename, 'PNG')
    print(f"[SELECTION POPUP] Saved record label: {filename}")

    # Log record image creation
    from datetime import datetime
    now = datetime.now().replace(microsecond=0)
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S")
    try:
        with open('log.txt', 'a') as log:
            log.write(f'\n{log_date}, {log_time}, {song_title}, {artist_name}, New Record Image Pressed, {selected_label}')
    except IOError as log_error:
        print(f"[ERROR] Failed to write to log.txt: {log_error}")

    # Composite with green background
    try:
        record_label = Image.open(filename)

        # Create 610x610 green background
        bg_width = 610
        bg_height = 610
        green_color = (0, 128, 0, 255)
        background = Image.new('RGBA', (bg_width, bg_height), green_color)

        if record_label.mode != 'RGBA':
            record_label = record_label.convert('RGBA')

        # Center record on background
        record_width, record_height = record_label.size
        x_position = (bg_width - record_width) // 2
        y_position = (bg_height - record_height) // 2

        composite = background.copy()
        composite.paste(record_label, (x_position, y_position), record_label)

        # Resize to 320x320
        popup_width = 250
        popup_height = 250
        composite = composite.resize((popup_width, popup_height), Image.Resampling.LANCZOS)

        # Save composite
        composite_filename = 'final_record_with_background.png'
        composite.save(composite_filename, 'PNG')
        print(f"[SELECTION POPUP] Created composite: {composite_filename} ({popup_width}x{popup_height})")

        return composite_filename

    except Exception as e:
        print(f"[SELECTION POPUP] Error creating composite: {e}")
        return filename


# ============================================================================
# SECTION 5: BUTTON GRID CLASS
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
        self.font_id = pygame.font.SysFont('centurygothic', 16, bold=True)
        self.font_song = pygame.font.SysFont('centurygothic', 14, bold=True)

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
                    title_text = self.song_list[song_idx]['title']

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
                    artist_text = self.song_list[song_idx]['artist']

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

    def draw(self, screen, selection_letter=None, selection_number=None):
        """Draw all buttons in the grid

        Args:
            screen: Pygame surface to draw on
            selection_letter: Currently selected letter (A, B, or C) or None
            selection_number: Currently selected number (1-7) or None
        """
        for row in self.buttons:
            for button in row:
                # Determine if this button should be dimmed
                is_dimmed = False

                # If a letter is selected, dim other columns
                if selection_letter and button['type'] in ('id', 'title', 'artist', 'spacer'):
                    button_letter = None
                    if 'text' in button and len(button['text']) > 0:
                        button_letter = button['text'][0] if button['type'] == 'id' else None

                    # Check song_index to determine column
                    if 'song_index' in button:
                        song_idx = button['song_index']
                        if song_idx < 14:
                            button_letter = 'A'
                        elif song_idx < 28:
                            button_letter = 'B'
                        else:
                            button_letter = 'C'

                    if button_letter and button_letter != selection_letter:
                        is_dimmed = True

                # If a number is selected, dim other rows
                if selection_number and button['type'] in ('id', 'title', 'artist', 'spacer'):
                    if button['type'] == 'id' and len(button['text']) > 1:
                        button_number = int(button['text'][1])
                        if button_number != selection_number:
                            is_dimmed = True
                    elif 'song_index' in button:
                        # Calculate row from song_index
                        song_idx = button['song_index']
                        if song_idx < 14:
                            row_num = (song_idx // 2) + 1
                        elif song_idx < 28:
                            row_num = ((song_idx - 14) // 2) + 1
                        else:
                            row_num = ((song_idx - 28) // 2) + 1
                        if row_num != selection_number:
                            is_dimmed = True

                # Draw button background image
                img = button['image']
                if is_dimmed:
                    # Create dimmed version (50% opacity overlay)
                    dimmed = img.copy()
                    dimmed.set_alpha(128)
                    screen.blit(dimmed, (button['x'], button['y']))
                else:
                    screen.blit(img, (button['x'], button['y']))

                # Draw button text if present
                if button['text']:
                    # Render text
                    text_color = (0, 0, 0) if not is_dimmed else (128, 128, 128)
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
# SECTION 5: CONTROL BUTTON CLASS
# ============================================================================

class ControlButtons:
    """Manages the control buttons (A, B, C, 1-7, SELECT, CORRECT)"""

    def __init__(self, start_x, start_y):
        """Initialize control buttons

        Args:
            start_x: X position to start drawing buttons
            start_y: Y position to start drawing buttons
        """
        self.start_x = start_x
        self.start_y = start_y

        # Load button images
        try:
            self.a_button_img = pygame.image.load(A_BUTTON_IMG)
            self.b_button_img = pygame.image.load(B_BUTTON_IMG)
            self.c_button_img = pygame.image.load(C_BUTTON_IMG)
            self.select_button_img = pygame.image.load(SELECT_BUTTON_IMG)
            self.correct_button_img = pygame.image.load(CORRECT_BUTTON_IMG)
            self.blank_button_img = pygame.image.load(BLANK_BUTTON_IMG)

            # Load number button images (1-7)
            self.num_button_imgs = {}
            for i in range(1, 8):
                self.num_button_imgs[i] = pygame.image.load(NUM_BUTTON_IMG.format(i))
        except pygame.error as e:
            print(f"Error loading control button images: {e}")
            raise

        # Build button layout
        self.buttons = self._create_button_layout()

    def _create_button_layout(self):
        """Create control button layout

        Returns:
            List of button definitions
        """
        buttons = []

        # Row 1: Blank spacers, A, B, C, 1, 2
        current_x = self.start_x
        current_y = self.start_y

        # Skip initial blanks (35px + 4 × 50px = 235px)
        current_x += 35 + (4 * 50)

        # A button
        buttons.append({
            'key': 'A',
            'x': current_x,
            'y': current_y,
            'image': self.a_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 50, 50)
        })
        current_x += 50

        # B button
        buttons.append({
            'key': 'B',
            'x': current_x,
            'y': current_y,
            'image': self.b_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 50, 50)
        })
        current_x += 50

        # C button
        buttons.append({
            'key': 'C',
            'x': current_x,
            'y': current_y,
            'image': self.c_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 50, 50)
        })
        current_x += 50

        # Number buttons 1 and 2
        for num in [1, 2]:
            buttons.append({
                'key': str(num),
                'x': current_x,
                'y': current_y,
                'image': self.num_button_imgs[num],
                'enabled': False,
                'rect': pygame.Rect(current_x, current_y, 50, 50)
            })
            current_x += 50

        # Row 2: Skip blank (50px), CORRECT button (150px), skip blank (35px), then 3-7, skip blank, SELECT
        current_x = self.start_x
        current_y = self.start_y + 50 + 6  # 50px button height + 6px spacing

        # Skip blank (50px)
        current_x += 50

        # CORRECT button
        buttons.append({
            'key': 'CORRECT',
            'x': current_x,
            'y': current_y,
            'image': self.correct_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 150, 50)
        })
        current_x += 150

        # Skip blank (35px)
        current_x += 35

        # Number buttons 3-7
        for num in [3, 4, 5, 6, 7]:
            buttons.append({
                'key': str(num),
                'x': current_x,
                'y': current_y,
                'image': self.num_button_imgs[num],
                'enabled': False,
                'rect': pygame.Rect(current_x, current_y, 50, 50)
            })
            current_x += 50

        # Skip blank (35px)
        current_x += 35

        # SELECT button
        buttons.append({
            'key': 'SELECT',
            'x': current_x,
            'y': current_y,
            'image': self.select_button_img,
            'enabled': False,
            'rect': pygame.Rect(current_x, current_y, 150, 50)
        })

        return buttons

    def update_button_states(self, selection_letter=None, selection_number=None):
        """Update which buttons are enabled/disabled

        Args:
            selection_letter: Selected letter (A, B, C) or None
            selection_number: Selected number (1-7) or None
        """
        for button in self.buttons:
            key = button['key']

            if key in ['A', 'B', 'C']:
                # Letter buttons enabled if no letter selected, or this is the selected letter
                button['enabled'] = (selection_letter is None) or (key == selection_letter)

            elif key in ['1', '2', '3', '4', '5', '6', '7']:
                # Number buttons enabled only if letter selected but number not yet selected
                button['enabled'] = (selection_letter is not None) and (selection_number is None)

            elif key == 'SELECT':
                # SELECT enabled only if both letter and number selected
                button['enabled'] = (selection_letter is not None) and (selection_number is not None)

            elif key == 'CORRECT':
                # CORRECT button always enabled
                button['enabled'] = True

    def draw(self, screen, selection_letter=None, selection_number=None):
        """Draw all control buttons

        Args:
            screen: Pygame surface to draw on
            selection_letter: Currently selected letter (A, B, or C) or None
            selection_number: Currently selected number (1-7) or None
        """
        for button in self.buttons:
            # Determine if button should be dimmed
            should_dim = False

            # Dim if button is disabled
            if not button['enabled']:
                should_dim = True
            # Also dim if this button is the selected letter
            elif button['key'] in ['A', 'B', 'C'] and button['key'] == selection_letter:
                should_dim = True
            # Also dim if this button is the selected number
            elif button['key'] in ['1', '2', '3', '4', '5', '6', '7'] and button['key'] == str(selection_number):
                should_dim = True

            # Draw button
            img = button['image']
            if should_dim:
                # Create dimmed version
                dimmed = img.copy()
                dimmed.set_alpha(100)
                screen.blit(dimmed, (button['x'], button['y']))
            else:
                screen.blit(img, (button['x'], button['y']))

    def handle_click(self, pos):
        """Check if a button was clicked

        Args:
            pos: Mouse position (x, y)

        Returns:
            Button key if clicked and enabled, None otherwise
        """
        for button in self.buttons:
            if button['enabled'] and button['rect'].collidepoint(pos):
                return button['key']
        return None

# ============================================================================
# SECTION 6: INFO SCREEN CLASS
# ============================================================================

class InfoScreen:
    """Manages the info screen display (now playing, upcoming, credits)"""

    def __init__(self, start_x, start_y, song_list):
        """Initialize info screen

        Args:
            start_x: X position to start drawing
            start_y: Y position to start drawing
            song_list: Full song list for lookups
        """
        self.start_x = start_x
        self.start_y = start_y
        self.song_list = song_list

        # Create fonts
        self.font_header_large = pygame.font.SysFont('centurygothic', 26, bold=True)
        self.font_header_medium = pygame.font.SysFont('centurygothic', 18, bold=True)
        self.font_song_title = pygame.font.SysFont('centurygothic', 18, bold=True)
        self.font_song_artist = pygame.font.SysFont('centurygothic', 16, bold=True)
        self.font_info = pygame.font.SysFont('centurygothic', 12, bold=True)
        self.font_credits = pygame.font.SysFont('centurygothic', 26, bold=True)

        # Initialize display data
        self.current_song_index = None
        self.upcoming_songs = []
        self.credits = 0
        self.time_remaining = ""

    def update(self, current_song_index, upcoming_songs, credits, time_remaining_seconds=None):
        """Update info screen data

        Args:
            current_song_index: Index of currently playing song or None
            upcoming_songs: List of upcoming song indices
            credits: Number of credits available
            time_remaining_seconds: Seconds remaining in current song or None
        """
        self.current_song_index = current_song_index
        self.upcoming_songs = upcoming_songs[:10]  # Max 10 upcoming
        self.credits = credits

        if time_remaining_seconds is not None:
            self.time_remaining = format_time_remaining(time_remaining_seconds)
        else:
            self.time_remaining = ""

    def draw(self, screen):
        """Draw info screen on the display

        Args:
            screen: Pygame surface to draw on
        """
        current_y = self.start_y + 10

        # "Now Playing" header
        text = self.font_header_large.render("Now Playing", True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 30

        # Current song title
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            title_text = song['title']
            text = self.font_song_title.render(title_text, True, COLOR_WHITE)
            rect = text.get_rect(center=(self.start_x + 145, current_y))
            screen.blit(text, rect)
        current_y += 25

        # Current artist
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            artist_text = song['artist']
            text = self.font_song_artist.render(artist_text, True, COLOR_WHITE)
            rect = text.get_rect(center=(self.start_x + 145, current_y))
            screen.blit(text, rect)
        current_y += 25

        # Mode indicator
        mode_text = "  Mode: Playing Song"
        text = self.font_info.render(mode_text, True, COLOR_SEAGREEN3)
        screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Mini song title
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            mini_title = '  Title: ' + song['title']
            text = self.font_info.render(mini_title, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Mini artist
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            mini_artist = '  Artist: ' + song['artist']
            text = self.font_info.render(mini_artist, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Year & Time Remaining
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            if self.time_remaining:
                year_time = f"  Year: {song['year']}   Remaining: {self.time_remaining}"
            else:
                year_time = f"  Year: {song['year']}   Length: {song['duration']}"
            text = self.font_info.render(year_time, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Album
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            album_text = '  Album: ' + song['album']
            text = self.font_info.render(album_text, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 30

        # "Upcoming Selections" header
        text = self.font_header_medium.render("Upcoming Selections", True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 28

        # Spacer
        current_y += 5

        # 10 upcoming song slots
        for i in range(10):
            if i < len(self.upcoming_songs):
                # upcoming_songs now contains formatted strings (title - artist)
                upcoming_text = f"{i+1}. {self.upcoming_songs[i]}"
                text = self.font_info.render(upcoming_text, True, COLOR_SEAGREEN3)
                screen.blit(text, (self.start_x, current_y))
            current_y += 18

        # Spacer
        current_y += 5

        # Credits display
        credits_text = f"CREDITS {self.credits}"
        text = self.font_credits.render(credits_text, True, COLOR_WHITE)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 30

        # "Twenty-Five Cents Per Selection"
        text = self.font_info.render("Twenty-Five Cents Per Selection", True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 18

        # Total songs available
        total_text = f"{len(self.song_list)} Song Selections Available"
        text = self.font_info.render(total_text, True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)

# ============================================================================
# SECTION 7: VLC PLAYBACK ENGINE
# ============================================================================

class PlaybackEngine:
    """Manages VLC playback of songs from paid and random playlists"""

    def __init__(self, song_list, paid_playlist_path):
        """Initialize playback engine

        Args:
            song_list: Full list of songs
            paid_playlist_path: Path to PaidMusicPlayList.txt
        """
        self.song_list = song_list
        self.paid_playlist_path = paid_playlist_path
        # Suppress VLC error messages and warnings
        self.vlc_instance = vlc.Instance('--quiet', '--no-video')
        self.player = self.vlc_instance.media_player_new()
        self.current_song_index = None
        self.paid_playlist = []
        self.random_playlist = []
        self.upcoming_song_list = []  # Display strings for upcoming songs
        self.is_paid_song = False  # Track if current song is paid or random

        # Genre filter flags
        self.genre0 = 'null'
        self.genre1 = 'null'
        self.genre2 = 'null'
        self.genre3 = 'null'

    def load_paid_playlist(self):
        """Load paid playlist from file"""
        try:
            if os.path.exists(self.paid_playlist_path):
                with open(self.paid_playlist_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.paid_playlist = json.loads(content)
                    else:
                        self.paid_playlist = []
            else:
                self.paid_playlist = []
        except Exception as e:
            print(f"Error loading paid playlist: {e}")
            self.paid_playlist = []

    def save_paid_playlist(self):
        """Save paid playlist to file"""
        try:
            with open(self.paid_playlist_path, 'w') as f:
                json.dump(self.paid_playlist, f)
        except Exception as e:
            print(f"Error saving paid playlist: {e}")

    def load_genre_flags(self):
        """Load genre filter flags from GenreFlagsList.txt

        Reads the genre flags file and sets the 4 genre filter slots.
        If file doesn't exist or is invalid, defaults to 'null' for all slots.
        """
        try:
            if os.path.exists(GENRE_FLAGS_FILE_PATH):
                with open(GENRE_FLAGS_FILE_PATH, 'r') as f:
                    genre_list = json.load(f)
                self.genre0 = genre_list[0] if len(genre_list) > 0 else 'null'
                self.genre1 = genre_list[1] if len(genre_list) > 1 else 'null'
                self.genre2 = genre_list[2] if len(genre_list) > 2 else 'null'
                self.genre3 = genre_list[3] if len(genre_list) > 3 else 'null'

                # Print genre filter status
                print("\n[GENRE FILTERS]")
                if self.genre0 != 'null':
                    print(f"  Genre 0: {self.genre0}")
                if self.genre1 != 'null':
                    print(f"  Genre 1: {self.genre1}")
                if self.genre2 != 'null':
                    print(f"  Genre 2: {self.genre2}")
                if self.genre3 != 'null':
                    print(f"  Genre 3: {self.genre3}")
                if (self.genre0 == 'null' and self.genre1 == 'null' and
                    self.genre2 == 'null' and self.genre3 == 'null'):
                    print("  No genre filters set - playing all songs")
            else:
                # File doesn't exist, use defaults
                self.genre0 = self.genre1 = self.genre2 = self.genre3 = 'null'
                print("[GENRE FILTERS] No genre filters set - playing all songs")
        except Exception as e:
            print(f"[ERROR] Failed to load genre flags: {e}")
            self.genre0 = self.genre1 = self.genre2 = self.genre3 = 'null'

    def generate_random_playlist(self):
        """Generate random playlist from all songs (respects genre filters, skips 'norandom')"""
        # Load current genre filter settings
        self.load_genre_flags()

        self.random_playlist = []

        for index, song in enumerate(self.song_list):
            # Skip songs marked with 'norandom' in comment field
            if 'norandom' in song.get('comment', '').lower():
                continue

            # If no genre filters are set, add all songs
            if (self.genre0 == "null" and self.genre1 == "null" and
                self.genre2 == "null" and self.genre3 == "null"):
                self.random_playlist.append(index)
            else:
                # Add songs matching any of the genre filters
                comment = song.get('comment', '')
                if (self.genre0 != "null" and self.genre0 in comment) or \
                   (self.genre1 != "null" and self.genre1 in comment) or \
                   (self.genre2 != "null" and self.genre2 in comment) or \
                   (self.genre3 != "null" and self.genre3 in comment):
                    self.random_playlist.append(index)

        # Shuffle the playlist
        random.shuffle(self.random_playlist)
        print(f"[RANDOM PLAYLIST] Generated {len(self.random_playlist)} songs")
        if len(self.random_playlist) == 0:
            print("[WARNING] No songs match the current genre filters!")

        # Log random playlist generation with active genres
        from datetime import datetime
        now = datetime.now().replace(microsecond=0)
        log_date = now.strftime("%Y-%m-%d")
        log_time = now.strftime("%H:%M:%S")

        # Build genre list for log entry
        active_genres = []
        if self.genre0 != "null":
            active_genres.append(self.genre0)
        if self.genre1 != "null":
            active_genres.append(self.genre1)
        if self.genre2 != "null":
            active_genres.append(self.genre2)
        if self.genre3 != "null":
            active_genres.append(self.genre3)

        # If no genres set, log "all genres"
        if not active_genres:
            genre_text = "all genres"
        else:
            genre_text = ", ".join(active_genres)

        try:
            with open(LOG_FILE_PATH, 'a') as log:
                log.write(f'\n{log_date}, {log_time}, Random playlist generated with genres: {genre_text}')
        except IOError as log_error:
            print(f"[ERROR] Failed to write to log.txt: {log_error}")

    def update(self):
        """Update playback state - called every frame"""
        # Check if current song finished
        if self.player.get_state() == vlc.State.Ended:
            print("Song finished")

            # If this was a paid song, remove it from playlist AFTER playback completes
            if self.is_paid_song:
                print("Removing completed paid song from playlist")
                # Re-read file to capture any songs added during playback (0.82.8 bug fix)
                self.load_paid_playlist()

                # Remove first song (the one that just finished)
                if len(self.paid_playlist) > 0:
                    self.paid_playlist.pop(0)
                    self.save_paid_playlist()
                    print(f"Paid playlist now has {len(self.paid_playlist)} songs")

                # Note: upcoming_song_list is already updated when song started playing

            # Now play next song
            print("Loading next song")
            self.play_next_song()

    def play_next_song(self):
        """Play next song - paid songs first, then random songs"""
        # Reload paid playlist to capture any new additions
        self.load_paid_playlist()

        # Priority 1: Play paid songs first
        if len(self.paid_playlist) > 0:
            song_index = self.paid_playlist[0]

            if song_index < len(self.song_list):
                song = self.song_list[song_index]
                song_path = song['location']

                print(f"Playing PAID: {song['title']} by {song['artist']}")
                print(f"Path: {song_path}")

                # Write CurrentSongPlaying.txt before playing
                try:
                    with open(CURRENT_SONG_PLAYING_PATH, 'w') as f:
                        f.write(song_path)
                except Exception as e:
                    print(f"Error writing CurrentSongPlaying.txt: {e}")

                # Create media and play
                media = self.vlc_instance.media_new(song_path)
                self.player.set_media(media)
                self.player.play()

                self.current_song_index = song_index
                self.is_paid_song = True

                # Log paid song play
                from datetime import datetime
                now = datetime.now().replace(microsecond=0)
                log_date = now.strftime("%Y-%m-%d")
                log_time = now.strftime("%H:%M:%S")
                try:
                    with open(LOG_FILE_PATH, 'a') as log:
                        log.write(f'\n{log_date}, {log_time}, {song["title"]}, {song["artist"]}, Paid')
                except IOError as log_error:
                    print(f"[ERROR] Failed to write to log.txt: {log_error}")

                # Remove from upcoming display list (song is now playing, not upcoming)
                if len(self.upcoming_song_list) > 0:
                    # Check if this song matches the first upcoming entry
                    expected_str = f"{song['title']} - {song['artist']}"
                    if self.upcoming_song_list[0] == expected_str:
                        self.upcoming_song_list.pop(0)
                        print(f"Removed from upcoming list. {len(self.upcoming_song_list)} songs remaining in queue")

                # DO NOT remove from paid playlist here - will be removed after song completes
            else:
                print(f"Invalid paid song index: {song_index}")
                # Remove invalid entry immediately
                self.paid_playlist.pop(0)
                self.save_paid_playlist()
                # Try next song
                self.play_next_song()

        # Priority 2: Play random songs if no paid songs
        elif len(self.random_playlist) > 0:
            song_index = self.random_playlist[0]

            if song_index < len(self.song_list):
                song = self.song_list[song_index]
                song_path = song['location']

                print(f"Playing RANDOM: {song['title']} by {song['artist']}")
                print(f"Path: {song_path}")

                # Write CurrentSongPlaying.txt before playing
                try:
                    with open(CURRENT_SONG_PLAYING_PATH, 'w') as f:
                        f.write(song_path)
                except Exception as e:
                    print(f"Error writing CurrentSongPlaying.txt: {e}")

                # Create media and play
                media = self.vlc_instance.media_new(song_path)
                self.player.set_media(media)
                self.player.play()

                self.current_song_index = song_index
                self.is_paid_song = False

                # Log random song play
                from datetime import datetime
                now = datetime.now().replace(microsecond=0)
                log_date = now.strftime("%Y-%m-%d")
                log_time = now.strftime("%H:%M:%S")
                try:
                    with open(LOG_FILE_PATH, 'a') as log:
                        log.write(f'\n{log_date}, {log_time}, {song["title"]}, {song["artist"]}, Random')
                except IOError as log_error:
                    print(f"[ERROR] Failed to write to log.txt: {log_error}")

                # Remove from random playlist (move to end for continuous play)
                self.random_playlist.pop(0)
                self.random_playlist.append(song_index)  # Add to end for rotation
            else:
                print(f"Invalid random song index: {song_index}")
                # Remove invalid entry
                self.random_playlist.pop(0)
                # Try next song
                self.play_next_song()

        else:
            print("No songs available (regenerating random playlist)")
            self.generate_random_playlist()
            if len(self.random_playlist) > 0:
                self.play_next_song()

    def get_time_remaining(self):
        """Get time remaining in current song

        Returns:
            float: Seconds remaining or None if not playing
        """
        if self.player.is_playing():
            current_time_ms = self.player.get_time()
            duration_ms = self.player.get_length()

            if current_time_ms >= 0 and duration_ms > 0:
                elapsed_seconds = current_time_ms / 1000.0
                total_seconds = duration_ms / 1000.0
                return total_seconds - elapsed_seconds

        return None

    def get_upcoming_songs(self):
        """Get list of upcoming song display strings

        Returns:
            list: Formatted strings (title - artist) for upcoming songs
        """
        return self.upcoming_song_list.copy()

# ============================================================================
# SECTION 8: FILE INITIALIZATION
# ============================================================================

def setup_files():
    """
    Check for required files on disk. If they don't exist, create them with default content.

    This function ensures all necessary data files exist before the jukebox starts.
    Creates 7 files if missing:
    - log.txt: Playback and error logging
    - GenreFlagsList.txt: Genre filter flags
    - MusicMasterSongListCheck.txt: Song list change tracking
    - PaidMusicPlayList.txt: Queue of user-selected paid songs
    - YearRangeLabelList.txt: Year range to record label mapping
    - RecordLabelAssignList.txt: Artist to record label assignments
    - FullYearRangeLabelList.txt: Complete year range label data
    """
    from datetime import datetime

    # Get current timestamp for log file
    now = datetime.now().replace(microsecond=0)
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S")

    # Setup log file
    try:
        if not os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, 'w') as log:
                log.write(f'{log_date}, {log_time}, Jukebox Program Started For The Day')
            print(f"[INIT] Created log file: {LOG_FILE_PATH}")
        else:
            with open(LOG_FILE_PATH, 'a') as log:
                log.write(f'\n{log_date}, {log_time}, Jukebox Program Started For The Day')
    except IOError as e:
        print(f"[ERROR] Failed to setup log.txt: {e}")

    # Setup genre flags file
    try:
        if not os.path.exists(GENRE_FLAGS_FILE_PATH):
            with open(GENRE_FLAGS_FILE_PATH, 'w') as genre_flags_file:
                genre_flags_list = ['null', 'null', 'null', 'null']
                json.dump(genre_flags_list, genre_flags_file)
            print(f"[INIT] Created genre flags file: {GENRE_FLAGS_FILE_PATH}")
    except (IOError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to setup GenreFlagsList.txt: {e}")

    # Setup music master song list check file
    try:
        if not os.path.exists(MUSIC_MASTER_SONG_LIST_CHECK_PATH):
            with open(MUSIC_MASTER_SONG_LIST_CHECK_PATH, 'w') as check_file:
                json.dump([], check_file)
            print(f"[INIT] Created song list check file: {MUSIC_MASTER_SONG_LIST_CHECK_PATH}")
    except (IOError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to setup MusicMasterSongListCheck.txt: {e}")

    # Setup paid music playlist file
    try:
        if not os.path.exists(PAID_MUSIC_PLAYLIST_PATH):
            with open(PAID_MUSIC_PLAYLIST_PATH, 'w') as paid_list_file:
                json.dump([], paid_list_file)
            print(f"[INIT] Created paid playlist file: {PAID_MUSIC_PLAYLIST_PATH}")
    except (IOError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to setup PaidMusicPlayList.txt: {e}")

    # Setup year range label list file
    try:
        if not os.path.exists(YEAR_RANGE_LABEL_LIST_PATH):
            with open(YEAR_RANGE_LABEL_LIST_PATH, 'w') as year_range_file:
                year_range_file.write('[]')
            print(f"[INIT] Created year range label list file: {YEAR_RANGE_LABEL_LIST_PATH}")
    except IOError as e:
        print(f"[ERROR] Failed to setup YearRangeLabelList.txt: {e}")

    # Setup record label assign list file
    try:
        if not os.path.exists(RECORD_LABEL_ASSIGN_LIST_PATH):
            with open(RECORD_LABEL_ASSIGN_LIST_PATH, 'w') as label_assign_file:
                label_assign_file.write('[]')
            print(f"[INIT] Created record label assign list file: {RECORD_LABEL_ASSIGN_LIST_PATH}")
    except IOError as e:
        print(f"[ERROR] Failed to setup RecordLabelAssignList.txt: {e}")

    # Setup full year range label list file
    try:
        if not os.path.exists(FULL_YEAR_RANGE_LABEL_LIST_PATH):
            with open(FULL_YEAR_RANGE_LABEL_LIST_PATH, 'w') as full_year_range_file:
                full_year_range_file.write('[]')
            print(f"[INIT] Created full year range label list file: {FULL_YEAR_RANGE_LABEL_LIST_PATH}")
    except IOError as e:
        print(f"[ERROR] Failed to setup FullYearRangeLabelList.txt: {e}")

# ============================================================================
# SECTION 8B: SONG LIST GENERATION
# ============================================================================

def generate_mp3_metadata(music_dir):
    """
    Scan music directory and extract ID3 metadata from all MP3 files.
    Displays a threaded pygame progress bar during processing.

    Args:
        music_dir (str): Path to music directory

    Returns:
        list: List of tuples containing metadata (number, location, title, artist, album, year, comment, duration)
    """
    music_id3_metadata_list = []
    progress_bar = None

    try:
        mp3_music_files = glob.glob(os.path.join(music_dir, '*.mp3'))
    except Exception as e:
        print(f"[ERROR] Failed to search for MP3 files: {e}")
        return []

    if not mp3_music_files:
        print("[ERROR] No MP3 files found in music directory")
        return []

    print(f"\nFound {len(mp3_music_files)} MP3 files. Processing...")
    print("Please Be Patient - Regenerating Your Songlist From Scratch")
    print("Music Will Start When Finished\n")

    # Initialize and start progress bar in separate thread
    progress_bar = MetadataProgressBar(len(mp3_music_files))
    progress_bar.start()

    counter = 0

    for file_path in mp3_music_files:
        try:
            # Update progress bar with current file
            file_name = os.path.basename(file_path)
            progress_bar.update(counter, file_name)

            id3tag = TinyTag.get(file_path)

            if id3tag is None:
                print(f"[ERROR] Could not read metadata from {file_path}")
                continue

            # Convert duration to MM:SS format (matching original)
            get_song_duration_seconds = "%f" % id3tag.duration
            remove_song_duration_decimals = float(get_song_duration_seconds)
            song_duration_decimals_removed = int(remove_song_duration_decimals)
            song_duration_minutes_seconds = int(song_duration_decimals_removed)
            song_duration = time.strftime("%M:%S", time.gmtime(song_duration_minutes_seconds))

            song_metadata = (
                counter,
                file_path,
                "%s" % id3tag.title,
                "%s" % id3tag.artist,
                "%s" % id3tag.album,
                "%s" % id3tag.year,
                "%s" % id3tag.comment,
                song_duration
            )
            music_id3_metadata_list.append(song_metadata)
            counter += 1
        except Exception as e:
            print(f"[ERROR] Failed to extract metadata from {file_path}: {e}")
            continue

    # Stop progress bar and pause for 1 second
    if progress_bar:
        progress_bar.stop()
        time.sleep(1)  # Pause after progress bar closes

    if not music_id3_metadata_list:
        print("[ERROR] No valid metadata was extracted from MP3 files")
        return []

    print(f"\n[SUCCESS] Extracted metadata from {counter} songs")
    return music_id3_metadata_list

def generate_music_master_song_list_dictionary(music_id3_metadata_list, output_file, check_file):
    """
    Convert metadata tuples to dictionary format and save to files.

    Args:
        music_id3_metadata_list (list): List of metadata tuples
        output_file (str): Path to MusicMasterSongList.txt
        check_file (str): Path to MusicMasterSongListCheck.txt

    Returns:
        list: List of song dictionaries
    """
    try:
        print("\n[GENERATE] Creating Master Song List Dictionary...")

        # Assign keys for MusicMasterSongList Dictionary
        keys = ['number', 'location', 'title', 'artist', 'album', 'year', 'comment', 'duration']

        # Build MusicMasterSongList Dictionary
        music_master_song_list = [dict(zip(keys, sublst)) for sublst in music_id3_metadata_list]

        # Save MusicMasterSongList Dictionary
        try:
            with open(output_file, 'w') as master_list_file:
                json.dump(music_master_song_list, master_list_file)
            print(f"[SUCCESS] Saved master song list to {os.path.basename(output_file)}")

            # Log new songlist generation
            from datetime import datetime
            now = datetime.now().replace(microsecond=0)
            log_date = now.strftime("%Y-%m-%d")
            log_time = now.strftime("%H:%M:%S")
            try:
                with open(LOG_FILE_PATH, 'a') as log:
                    log.write(f'\n{log_date}, {log_time}, New Songlist Generated')
            except IOError as log_error:
                print(f"[ERROR] Failed to write to log.txt: {log_error}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to save MusicMasterSongList.txt: {e}")
            return []

        # Create and save file list size value
        list_size = len(music_master_song_list)
        try:
            with open(check_file, 'w') as check_file_handle:
                json.dump(list_size, check_file_handle)
            print(f"[SUCCESS] Saved song list check file ({list_size} songs)")
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to save MusicMasterSongListCheck.txt: {e}")
            return []

        return music_master_song_list
    except Exception as e:
        print(f"[ERROR] Unexpected error in generate_music_master_song_list_dictionary: {e}")
        return []

# ============================================================================
# SECTION 9: MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    # Initialize required data files
    setup_files()

    # ========================================================================
    # SONG LIST GENERATION/LOADING - MUST HAPPEN BEFORE PYGAME INIT
    # ========================================================================
    # The MetadataProgressBar uses pygame in a separate thread. This must
    # complete and call pygame.quit() before main pygame.init() is called
    # to avoid pygame double-initialization crash.
    # ========================================================================

    # Check if song list needs generation or loading
    song_list = []

    if os.path.exists(SONG_LIST_PATH):
        print("\n[CHECK] Found existing music database")

        # Count current MP3 files in directory
        try:
            current_file_count = len(glob.glob(os.path.join(MUSIC_DIRECTORY, '*.mp3')))
            print(f"[CHECK] Current MP3 files in directory: {current_file_count}")
        except Exception as e:
            print(f"[ERROR] Failed to count MP3 files: {e}")
            current_file_count = -1

        # Load stored file count from previous run
        try:
            with open(MUSIC_MASTER_SONG_LIST_CHECK_PATH, 'r') as check_file:
                stored_file_count = json.load(check_file)
                print(f"[CHECK] Stored MP3 file count: {stored_file_count}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to load MusicMasterSongListCheck.txt: {e}")
            stored_file_count = -1

        # Check for match
        if current_file_count == stored_file_count and current_file_count != -1:
            print("[SUCCESS] Music database matches current files")
            # Try to load existing MusicMasterSongList
            try:
                with open(SONG_LIST_PATH, 'r') as master_list_file:
                    song_list = json.load(master_list_file)
                print(f"[LOADED] {len(song_list)} songs from {SONG_LIST_PATH}")

                # Log existing songlist usage
                from datetime import datetime
                now = datetime.now().replace(microsecond=0)
                log_date = now.strftime("%Y-%m-%d")
                log_time = now.strftime("%H:%M:%S")
                try:
                    with open(LOG_FILE_PATH, 'a') as log:
                        log.write(f'\n{log_date}, {log_time}, Using Existing Songlist')
                except IOError as log_error:
                    print(f"[ERROR] Failed to write to log.txt: {log_error}")
            except (IOError, json.JSONDecodeError) as e:
                print(f"[ERROR] Failed to load MusicMasterSongList.txt: {e}")
                print("[REGENERATE] Corrupted file - regenerating...")
                # Fall through to regeneration
        else:
            print("[REGENERATE] Music database count mismatch - regenerating")
            # Fall through to regeneration

    # If song_list is still empty, regenerate
    if not song_list:
        print("\n" + "="*60)
        print("GENERATING SONG LIST FROM MUSIC DIRECTORY")
        print("="*60)

        # Generate metadata (this will use pygame in separate thread)
        music_id3_metadata_list = generate_mp3_metadata(MUSIC_DIRECTORY)

        if music_id3_metadata_list:
            # Convert to dictionary and save
            song_list = generate_music_master_song_list_dictionary(
                music_id3_metadata_list,
                SONG_LIST_PATH,
                MUSIC_MASTER_SONG_LIST_CHECK_PATH
            )

        print("="*60)
        print(f"SONG LIST GENERATION COMPLETE: {len(song_list)} songs")
        print("="*60 + "\n")

    # Verify we have songs
    if not song_list:
        print("\n[FATAL ERROR] No songs found in music directory!")
        sys.exit(1)

    # ========================================================================
    # EXTRACT AND LOG AVAILABLE GENRES FROM MUSIC COLLECTION
    # ========================================================================
    print("\n[ANALYZE] Extracting available genres from music collection...")

    # Extract all unique individual genre tags (split comment field by spaces)
    all_genres = set()
    for song in song_list:
        comment = song.get('comment', '')
        if comment:  # Only include non-empty comments
            # Split by spaces to get individual genre tags
            genre_tags = comment.split()
            for tag in genre_tags:
                # Normalize: strip whitespace, convert to lowercase, filter empty
                normalized_tag = tag.strip().lower()
                if normalized_tag:  # Only add non-empty tags
                    all_genres.add(normalized_tag)

    # Sort genres alphabetically for readability
    sorted_genres = sorted(all_genres)

    # Print to console
    print(f"[GENRES] Found {len(sorted_genres)} unique genre tags:")
    for genre in sorted_genres:
        print(f"         - {genre}")

    # Log to file with timestamp
    from datetime import datetime
    now = datetime.now().replace(microsecond=0)
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S")

    try:
        with open(LOG_FILE_PATH, 'a') as log:
            log.write(f'\n{log_date}, {log_time}, Genres Available ({len(sorted_genres)} unique tags):\n')
            for genre in sorted_genres:
                log.write(f'{log_date}, {log_time},   - {genre}\n')
    except IOError as log_error:
        print(f"[ERROR] Failed to write genres to log.txt: {log_error}")

    print(f"[SUCCESS] Genre list logged to {LOG_FILE_PATH}\n")

    # ========================================================================
    # PYGAME INITIALIZATION - AFTER SONG LIST GENERATION COMPLETES
    # ========================================================================

    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Create window (no title bar)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Convergence Jukebox")

    # Load background image
    try:
        background = pygame.image.load(BACKGROUND_IMAGE_PATH)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for: {BACKGROUND_IMAGE_PATH}")
        pygame.quit()
        sys.exit(1)

    # Create pre-sorted lists for optimized search (binary search)
    print("Creating optimized search indices...")
    title_sorted_list = sorted(song_list, key=lambda x: x['title'].lower())

    # Extract unique artist names and sort
    all_artists = list(set(song['artist'] for song in song_list))
    artist_sorted_list = sorted(all_artists, key=lambda x: x.lower())
    print(f"Search optimization complete: {len(song_list)} songs, {len(artist_sorted_list)} unique artists")

    # Load arrow button images
    try:
        arrow_left_img = pygame.image.load(ARROW_LEFT_IMG)
        arrow_right_img = pygame.image.load(ARROW_RIGHT_IMG)
    except pygame.error as e:
        print(f"Error loading arrow images: {e}")
        pygame.quit()
        sys.exit(1)

    # Load sound effects
    try:
        buzz_sound = pygame.mixer.Sound(BUZZ_SOUND_PATH)
    except pygame.error as e:
        print(f"Error loading buzz sound: {e}")
        buzz_sound = None

    try:
        success_sound = pygame.mixer.Sound(SUCCESS_SOUND_PATH)
    except pygame.error as e:
        print(f"Error loading success sound: {e}")
        success_sound = None

    # Create button grid with song data
    try:
        button_grid = ButtonGrid(GRID_START_X, GRID_START_Y, song_list, selection_window_number=0)
    except pygame.error as e:
        print(f"Error creating button grid: {e}")
        pygame.quit()
        sys.exit(1)

    # Create control buttons
    try:
        control_buttons = ControlButtons(CONTROL_START_X, CONTROL_START_Y)
    except pygame.error as e:
        print(f"Error creating control buttons: {e}")
        pygame.quit()
        sys.exit(1)

    # Create info screen
    try:
        info_screen = InfoScreen(INFO_START_X, INFO_START_Y, song_list)
    except Exception as e:
        print(f"Error creating info screen: {e}")
        pygame.quit()
        sys.exit(1)

    # Create playback engine
    try:
        playback_engine = PlaybackEngine(song_list, PAID_MUSIC_PLAYLIST_PATH)
    except Exception as e:
        print(f"Error creating playback engine: {e}")
        pygame.quit()
        sys.exit(1)

    # Initialize random playlist and start playback
    print("Generating random playlist...")
    playback_engine.generate_random_playlist()
    print("Starting music playback...")
    playback_engine.play_next_song()

    # Initialize state variables
    selection_window_number = 0
    selection_entry_letter = None
    selection_entry_number = None
    credits = 0

    # Initialize popup state variables (rotating record popup)
    last_keypress_time = time.time()
    popup_active = False
    popup_record_image = None
    popup_record_surface = None
    popup_rotation_angle = 0
    popup_tonearm = None
    popup_play_time = 0

    # Initialize selection popup state variables
    selection_popup_active = False
    selection_popup_surface = None
    selection_popup_start_time = 0
    selection_popup_duration = 3.0  # 3 seconds

    # Create rectangles for arrow button click detection
    arrow_left_rect = pygame.Rect(ARROW_LEFT_X, ARROW_LEFT_Y, arrow_left_img.get_width(), arrow_left_img.get_height())
    arrow_right_rect = pygame.Rect(ARROW_RIGHT_X, ARROW_RIGHT_Y, arrow_right_img.get_width(), arrow_right_img.get_height())

    # Main loop
    clock = pygame.time.Clock()
    running = True

    print("Convergence Jukebox v0.90.41 - Add Comprehensive Logging System")
    print("Press ESC to exit")
    print("Press X to add credit")
    print("Press T for title search, Shift+A for artist search")
    print("Press A/B/C to select column, 1-7 to select song, S to confirm")
    print("Music plays continuously: paid songs → random songs → check for more paid songs...")

    while running:
        # Update playback engine
        playback_engine.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Reset idle timer on ANY keypress
                last_keypress_time = time.time()

                # Close popup on ANY keypress
                if popup_active:
                    popup_active = False
                    popup_record_image = None
                    popup_record_surface = None
                    popup_tonearm = None
                    print("Popup closed by keypress")

                if event.key == pygame.K_ESCAPE:
                    # Check if selection popup is active first
                    if selection_popup_active:
                        selection_popup_active = False
                        selection_popup_surface = None
                        print("[SELECTION POPUP] Closed by ESC key")
                    else:
                        running = False

                # Credit button
                elif event.key == pygame.K_x:
                    credits += 1
                    print(f"Credit added! Total credits: {credits}")

                    # Log quarter insertion
                    from datetime import datetime
                    now = datetime.now().replace(microsecond=0)
                    log_date = now.strftime("%Y-%m-%d")
                    log_time = now.strftime("%H:%M:%S")
                    try:
                        with open(LOG_FILE_PATH, 'a') as log:
                            log.write(f'\n{log_date}, {log_time}, Quarter Inserted')
                    except IOError as log_error:
                        print(f"[ERROR] Failed to write to log.txt: {log_error}")

                # Search functions (T for title, Shift+A for artist)
                elif event.key == pygame.K_t:
                    print("Opening title search...")
                    search_result = display_search_popup(
                        "title",
                        title_sorted_list,
                        artist_sorted_list,
                        song_list
                    )
                    if search_result is not None:
                        # Update idle timer from search window's last keypress
                        if 'last_keypress_time' in search_result:
                            last_keypress_time = search_result['last_keypress_time']
                            print(f"[SEARCH] Idle timer reset from search window")

                        # Update selection window to show selected song
                        selection_window_number = search_result['song_number']
                        button_grid.update_selection_window(selection_window_number)
                        print(f"Search result: navigated to song #{search_result['song_number']}")

                        # If title search, update button grid to highlight A1
                        if search_result.get('song_selected') == 'A1':
                            selection_entry_letter = 'A'
                            selection_entry_number = 1
                            control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                            print("Song set to A1 position - ready to select with S key")

                elif event.key == pygame.K_a and (event.mod & pygame.KMOD_SHIFT):
                    print("Opening artist search...")
                    search_result = display_search_popup(
                        "artist",
                        title_sorted_list,
                        artist_sorted_list,
                        song_list
                    )
                    if search_result is not None:
                        # Update idle timer from search window's last keypress
                        if 'last_keypress_time' in search_result:
                            last_keypress_time = search_result['last_keypress_time']
                            print(f"[SEARCH] Idle timer reset from search window")

                        # Update selection window to show first song by artist
                        selection_window_number = search_result['song_number']
                        button_grid.update_selection_window(selection_window_number)
                        print(f"Artist search result: navigated to song #{search_result['song_number']}")

                # Arrow keys for navigation
                elif event.key == pygame.K_RIGHT:
                    new_window_number = selection_window_number + 21
                    if new_window_number + 20 >= len(song_list):
                        new_window_number = len(song_list) - 21
                        if buzz_sound:
                            buzz_sound.play()
                    selection_window_number = new_window_number
                    button_grid.update_selection_window(selection_window_number)

                elif event.key == pygame.K_LEFT:
                    new_window_number = selection_window_number - 21
                    if new_window_number < 0:
                        new_window_number = 0
                        if buzz_sound:
                            buzz_sound.play()
                    selection_window_number = new_window_number
                    button_grid.update_selection_window(selection_window_number)

                # Letter selection (A, B, C)
                elif event.key == pygame.K_a:
                    if selection_entry_letter is None:
                        selection_entry_letter = 'A'
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected column: A")

                elif event.key == pygame.K_b:
                    if selection_entry_letter is None:
                        selection_entry_letter = 'B'
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected column: B")

                elif event.key == pygame.K_c:
                    # Check if Shift is pressed (uppercase 'C' for CORRECT button)
                    if event.mod & pygame.KMOD_SHIFT:
                        # CORRECT button - reset selection (Shift+C)
                        selection_entry_letter = None
                        selection_entry_number = None
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print("CORRECT: Selection cleared")
                    elif selection_entry_letter is None:
                        # Column C selection (lowercase 'c')
                        selection_entry_letter = 'C'
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected column: C")

                # Number selection (1-7)
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                    if selection_entry_letter is not None and selection_entry_number is None:
                        num_map = {
                            pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4,
                            pygame.K_5: 5, pygame.K_6: 6, pygame.K_7: 7
                        }
                        selection_entry_number = num_map[event.key]
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected row: {selection_entry_number}")

                # SELECT (S key)
                elif event.key == pygame.K_s:
                    if selection_entry_letter is not None and selection_entry_number is not None:
                        if credits > 0:
                            # Calculate song index
                            letter_offset = {'A': 0, 'B': 14, 'C': 28}[selection_entry_letter]
                            row_offset = (selection_entry_number - 1) * 2
                            song_index = selection_window_number + letter_offset + row_offset

                            if song_index < len(song_list):
                                song = song_list[song_index]
                                print(f"Selected: {song['title']} by {song['artist']}")

                                # Add to paid playlist
                                playback_engine.load_paid_playlist()
                                playback_engine.paid_playlist.append(song_index)
                                playback_engine.save_paid_playlist()

                                # Add to upcoming display list (formatted title - artist)
                                upcoming_str = f"{song['title']} - {song['artist']}"
                                playback_engine.upcoming_song_list.append(upcoming_str)
                                print(f"Added to upcoming list: {upcoming_str}")

                                # Play success sound
                                if success_sound:
                                    success_sound.play()

                                # Generate and show selection popup
                                try:
                                    # Get available labels
                                    blank_records_dir = "record_labels/blank_record_labels"
                                    png_files = [f for f in os.listdir(blank_records_dir) if f.endswith('.png')]

                                    # Generate record label image
                                    year = song.get('year', None)
                                    composite_path = generate_selection_record_label(
                                        song['title'],
                                        song['artist'],
                                        png_files,
                                        year
                                    )

                                    # Activate selection popup
                                    selection_popup_active = True
                                    selection_popup_start_time = time.time()
                                    print(f"[SELECTION POPUP] Activated for 3 seconds")

                                except Exception as e:
                                    print(f"[SELECTION POPUP] Error: {e}")
                                    import traceback
                                    traceback.print_exc()

                                # If nothing playing, start playback
                                if not playback_engine.player.is_playing():
                                    playback_engine.play_next_song()

                                # Deduct credit
                                credits -= 1
                                print(f"Credits remaining: {credits}")

                            # Reset selection
                            selection_entry_letter = None
                            selection_entry_number = None
                            control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        else:
                            if buzz_sound:
                                buzz_sound.play()
                            print("No credits available!")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos

                    # Check arrow buttons
                    if arrow_right_rect.collidepoint(mouse_pos):
                        new_window_number = selection_window_number + 21
                        if new_window_number + 20 >= len(song_list):
                            new_window_number = len(song_list) - 21
                            if buzz_sound:
                                buzz_sound.play()
                        selection_window_number = new_window_number
                        button_grid.update_selection_window(selection_window_number)

                    elif arrow_left_rect.collidepoint(mouse_pos):
                        new_window_number = selection_window_number - 21
                        if new_window_number < 0:
                            new_window_number = 0
                            if buzz_sound:
                                buzz_sound.play()
                        selection_window_number = new_window_number
                        button_grid.update_selection_window(selection_window_number)

                    # Check control buttons
                    else:
                        clicked_key = control_buttons.handle_click(mouse_pos)
                        if clicked_key:
                            if clicked_key in ['A', 'B', 'C']:
                                if selection_entry_letter is None:
                                    selection_entry_letter = clicked_key
                                    control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                    print(f"Selected column: {clicked_key}")

                            elif clicked_key in ['1', '2', '3', '4', '5', '6', '7']:
                                if selection_entry_letter is not None and selection_entry_number is None:
                                    selection_entry_number = int(clicked_key)
                                    control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                    print(f"Selected row: {selection_entry_number}")

                            elif clicked_key == 'CORRECT':
                                selection_entry_letter = None
                                selection_entry_number = None
                                control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                print("Selection cleared")

                            elif clicked_key == 'SELECT':
                                if selection_entry_letter is not None and selection_entry_number is not None:
                                    if credits > 0:
                                        # Calculate song index
                                        letter_offset = {'A': 0, 'B': 14, 'C': 28}[selection_entry_letter]
                                        row_offset = (selection_entry_number - 1) * 2
                                        song_index = selection_window_number + letter_offset + row_offset

                                        if song_index < len(song_list):
                                            song = song_list[song_index]
                                            print(f"Selected: {song['title']} by {song['artist']}")

                                            # Add to paid playlist
                                            playback_engine.load_paid_playlist()
                                            playback_engine.paid_playlist.append(song_index)
                                            playback_engine.save_paid_playlist()

                                            # Add to upcoming display list (formatted title - artist)
                                            upcoming_str = f"{song['title']} - {song['artist']}"
                                            playback_engine.upcoming_song_list.append(upcoming_str)
                                            print(f"Added to upcoming list: {upcoming_str}")

                                            # Play success sound
                                            if success_sound:
                                                success_sound.play()

                                            # If nothing playing, start playback
                                            if not playback_engine.player.is_playing():
                                                playback_engine.play_next_song()

                                            # Deduct credit
                                            credits -= 1
                                            print(f"Credits remaining: {credits}")

                                        # Reset selection
                                        selection_entry_letter = None
                                        selection_entry_number = None
                                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                    else:
                                        if buzz_sound:
                                            buzz_sound.play()
                                        print("No credits available!")

        # Update info screen with current state
        time_remaining = playback_engine.get_time_remaining()
        upcoming = playback_engine.get_upcoming_songs()
        info_screen.update(playback_engine.current_song_index, upcoming, credits, time_remaining)

        # Rotating record popup logic
        try:
            if playback_engine.player and playback_engine.current_song_index is not None:
                # Get VLC time information
                current_time_ms = playback_engine.player.get_time()
                duration_ms = playback_engine.player.get_length()

                if current_time_ms > 0 and duration_ms > 0:
                    elapsed_seconds = current_time_ms / 1000.0
                    total_seconds = duration_ms / 1000.0
                    time_remaining_seconds = total_seconds - elapsed_seconds
                    time_since_keypress = time.time() - last_keypress_time

                    # Conditions to SHOW popup
                    should_show = (
                        elapsed_seconds >= POPUP_MIN_PLAYBACK_TIME and
                        time_since_keypress >= POPUP_MIN_IDLE_TIME and
                        time_remaining_seconds >= POPUP_CLOSE_SECONDS_REMAINING and
                        not popup_active
                    )

                    # Conditions to CLOSE popup
                    should_close = (
                        popup_active and
                        time_remaining_seconds < POPUP_CLOSE_SECONDS_REMAINING
                    )

                    # Show popup
                    if should_show:
                        song = song_list[playback_engine.current_song_index]
                        year = song.get('year', None)

                        print(f"\n=== SHOWING ROTATING RECORD POPUP ===")
                        print(f"Song: {song['title']} by {song['artist']}")
                        print(f"Elapsed: {elapsed_seconds:.1f}s, Remaining: {time_remaining_seconds:.1f}s")

                        # Check if record image already exists (cache check)
                        image_already_exists = os.path.exists(OUTPUT_FILENAME)

                        # Generate record image
                        popup_record_image = generate_record_image(song['title'], song['artist'], year)

                        # Log if image was pulled from cache (existed before generate call)
                        if image_already_exists:
                            from datetime import datetime
                            now = datetime.now().replace(microsecond=0)
                            log_date = now.strftime("%Y-%m-%d")
                            log_time = now.strftime("%H:%M:%S")
                            try:
                                with open(LOG_FILE_PATH, 'a') as log:
                                    log.write(f'\n{log_date}, {log_time}, Rotating Record Image Pulled From Cache')
                            except IOError as log_error:
                                print(f"[ERROR] Failed to write to log.txt: {log_error}")

                        if popup_record_image and os.path.exists(popup_record_image):
                            # Load and scale record image
                            pil_image = Image.open(popup_record_image)
                            if pil_image.mode != 'RGBA':
                                pil_image = pil_image.convert('RGBA')

                            # Scale to fit on screen (500x500)
                            record_size = 500
                            pil_image = pil_image.resize((record_size, record_size), Image.Resampling.LANCZOS)

                            # Convert PIL to pygame surface
                            raw_bytes = pil_image.tobytes()
                            popup_record_surface = pygame.image.fromstring(raw_bytes, pil_image.size, 'RGBA')

                            # Create tonearm
                            record_x = SCREEN_WIDTH // 2 + 170
                            record_y = SCREEN_HEIGHT // 2 + 110
                            tonearm_pivot_x = record_x - 200
                            tonearm_pivot_y = record_y + 280
                            popup_tonearm = WurlitzerPaddleToneArm(tonearm_pivot_x, tonearm_pivot_y, 350)

                            # Set tonearm position based on song progress
                            song_progress = elapsed_seconds / total_seconds if total_seconds > 0 else 0
                            initial_angle = popup_tonearm.play_angle + (popup_tonearm.end_angle - popup_tonearm.play_angle) * song_progress
                            popup_tonearm.current_angle = initial_angle
                            popup_tonearm.target_angle = initial_angle

                            popup_rotation_angle = 0
                            popup_play_time = elapsed_seconds
                            popup_active = True

                            print("Popup activated successfully")

                    # Close popup
                    if should_close:
                        popup_active = False
                        popup_record_image = None
                        popup_record_surface = None
                        popup_tonearm = None
                        print("Popup closed (song ending)")

        except Exception as e:
            print(f"Error in popup logic: {e}")
            pass

        # Check selection popup timeout
        if selection_popup_active:
            elapsed = time.time() - selection_popup_start_time
            if elapsed >= selection_popup_duration:
                selection_popup_active = False
                selection_popup_surface = None
                print("[SELECTION POPUP] Auto-closed after 3 seconds")

        # Update popup animation if active
        if popup_active and popup_tonearm:
            dt = 1.0 / 60.0  # Frame delta time

            # Update tonearm
            popup_tonearm.update(dt)

            # Update rotation
            popup_rotation_angle = (popup_rotation_angle - RECORD_ROTATION_SPEED) % 360

            # Update tonearm tracking
            popup_play_time += dt
            if playback_engine.player and playback_engine.current_song_index is not None:
                duration_ms = playback_engine.player.get_length()
                if duration_ms > 0:
                    total_seconds = duration_ms / 1000.0
                    progress = min(popup_play_time / total_seconds, 1.0)
                    current_target = popup_tonearm.play_angle + (popup_tonearm.end_angle - popup_tonearm.play_angle) * progress
                    popup_tonearm.target_angle = current_target

        # Draw background
        screen.blit(background, (0, 0))

        # Draw button grid (hide when popup active)
        if not popup_active:
            button_grid.draw(screen, selection_entry_letter, selection_entry_number)

        # Draw arrow buttons
        screen.blit(arrow_left_img, (ARROW_LEFT_X, ARROW_LEFT_Y))
        screen.blit(arrow_right_img, (ARROW_RIGHT_X, ARROW_RIGHT_Y))

        # Draw control buttons (hide when popup active)
        if not popup_active:
            control_buttons.draw(screen, selection_entry_letter, selection_entry_number)

        # Draw info screen
        info_screen.draw(screen)

        # Draw song selection popup (if active)
        if selection_popup_active:
            try:
                # Load the composite image
                selection_img = pygame.image.load('final_record_with_background.png')

                # Position at (32, 300)
                popup_x = 58
                popup_y = 350

                # Draw black border/background
                border_size = 2
                pygame.draw.rect(screen, (0, 0, 0),
                               (popup_x - border_size, popup_y - border_size,
                                selection_img.get_width() + border_size * 2,
                                selection_img.get_height() + border_size * 2))

                # Draw the record image
                screen.blit(selection_img, (popup_x, popup_y))

            except Exception as e:
                print(f"[SELECTION POPUP] Error rendering: {e}")
                selection_popup_active = False

        # Draw rotating record popup (if active)
        if popup_active and popup_record_surface and popup_tonearm:
            # Brown background circle behind record
            record_x = SCREEN_WIDTH // 2 + 170
            record_y = SCREEN_HEIGHT // 2 + 110
            brown_background = (101, 67, 33)
            background_radius = 275
            pygame.draw.circle(screen, brown_background, (record_x, record_y), background_radius)

            # Rotate record
            rotated_surface = pygame.transform.rotate(popup_record_surface, popup_rotation_angle)
            rotated_rect = rotated_surface.get_rect(center=(record_x, record_y))
            screen.blit(rotated_surface, rotated_rect)

            # Draw tonearm
            popup_tonearm.draw(screen)

        # Update display
        pygame.display.flip()

        # Cap at 60 FPS
        clock.tick(60)

    # Cleanup
    playback_engine.player.stop()
    pygame.quit()
    sys.exit(0)

# ============================================================================
# SECTION 9: PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
