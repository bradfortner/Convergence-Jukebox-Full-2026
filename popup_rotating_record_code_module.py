"""
Rotating Record Pop-up Code Module
Displays a rotating record with Wurlitzer tonearm during playback based on idle time and song progress
Dynamically generates record images with song title and artist information

All popup parameters are defined here to keep popup logic self-contained.
"""
from pathlib import Path
import os
import time
import random
import threading
import pygame
import math
from enum import Enum
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import FreeSimpleGUI as sg

# ============================================================================
# POPUP LOGGING FUNCTION
# ============================================================================

def log_popup_event(message):
    """Log popup events to log.txt with timestamp"""
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        with open('log.txt', 'a') as log:
            log.write('\n' + current_time + ', ' + message)
    except Exception as e:
        print(f"Error writing to log file: {e}")

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
POPUP_WINDOW_LOCATION = (553, 200)  # (x, y) position on screen
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
MAX_TEXT_WIDTH = 300               # Maximum width for wrapped text (pixels) - song title
ARTIST_MAX_TEXT_WIDTH = 250        # Maximum width for wrapped text (pixels) - artist name
SONG_Y = 90                        # Y position offset for song title (from center)
ARTIST_Y = 120                     # Y position offset for artist name (from center)
SONG_LINE_HEIGHT = 25              # Vertical spacing between song title lines
ARTIST_LINE_HEIGHT = 30            # Vertical spacing between artist name lines
POPUP_WIDTH = 500                  # Popup window width in pixels
POPUP_HEIGHT = 500                 # Popup window height in pixels

# PNG generation settings
PNG_OUTPUT_WIDTH = 750             # PNG image generation width in pixels
PNG_OUTPUT_HEIGHT = 750            # PNG image generation height in pixels

# Pygame rotation animation settings
RECORD_ROTATION_FPS = 30           # Frames per second for rotation animation
RECORD_ROTATION_SPEED = 8          # Degrees per frame (240° per second at 30fps = 8°/frame)
PYGAME_BACKGROUND_COLOR = (64, 64, 64)  # Dark grey background for pygame window

# ============================================================================


# ============================================================================
# TONEARM ANIMATION CLASSES
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
    """
    Base class for turntable tonearm with animation states.
    Provides common functionality for tonearm movement and state management.
    """

    def __init__(self, x, y, length=200):
        """
        Initialize tonearm at pivot position.

        Args:
            x: X coordinate of pivot point
            y: Y coordinate of pivot point
            length: Length of tonearm in pixels
        """
        self.pivot_x = x
        self.pivot_y = y
        self.length = length

        # Angle positions (in degrees)
        self.park_angle = -90      # Parked position
        self.play_angle = -45      # Playing start position
        self.end_angle = -20       # End of record position
        self.current_angle = -90   # Current angle
        self.target_angle = -90    # Target angle for smooth movement

        # State management
        self.state = ToneArmState.PARKED

        # Animation parameters
        self.swing_speed = 45      # degrees per second (swing out/return)
        self.lower_speed = 2.0     # seconds to lower/lift
        self.lower_timer = 0.0
        self.current_height = 0    # Vertical offset (0 = down, positive = up)
        self.lift_height = 30      # How high to lift when moving

        # Visual effects
        self.play_wobble = 0       # Small wobble during playback
        self.wobble_timer = 0

        # Colors (can be overridden by subclasses)
        self.needle_color = (200, 50, 50)

    def play_record(self):
        """Start playing - swing out to record."""
        if self.state == ToneArmState.PARKED:
            self.state = ToneArmState.SWINGING_OUT
            self.target_angle = self.play_angle
            self.current_height = self.lift_height

    def return_to_park(self):
        """Return to parked position."""
        if self.state == ToneArmState.PLAYING:
            self.state = ToneArmState.LIFTING
            self.lower_timer = 0.0

    def is_playing(self):
        """Check if currently playing."""
        return self.state == ToneArmState.PLAYING

    def is_parked(self):
        """Check if parked."""
        return self.state == ToneArmState.PARKED

    def get_state(self):
        """Get current state."""
        return self.state

    def update(self, dt):
        """
        Update tonearm animation.

        Args:
            dt: Delta time in seconds
        """
        # Update wobble effect during playback
        if self.state == ToneArmState.PLAYING:
            self.wobble_timer += dt * 3
            self.play_wobble = math.sin(self.wobble_timer) * 0.5
        else:
            self.play_wobble = 0

        # State machine for tonearm movement
        if self.state == ToneArmState.SWINGING_OUT:
            # Swing from park to play position
            angle_diff = self.target_angle - self.current_angle
            if abs(angle_diff) > 0.5:
                move = self.swing_speed * dt
                if angle_diff > 0:
                    self.current_angle += min(move, angle_diff)
                else:
                    self.current_angle += max(-move, angle_diff)
            else:
                self.current_angle = self.target_angle
                self.state = ToneArmState.LOWERING
                self.lower_timer = 0.0

        elif self.state == ToneArmState.LOWERING:
            # Lower onto record
            self.lower_timer += dt
            progress = min(self.lower_timer / self.lower_speed, 1.0)
            self.current_height = self.lift_height * (1.0 - progress)

            if progress >= 1.0:
                self.current_height = 0
                self.state = ToneArmState.PLAYING

        elif self.state == ToneArmState.LIFTING:
            # Lift from record
            self.lower_timer += dt
            progress = min(self.lower_timer / self.lower_speed, 1.0)
            self.current_height = self.lift_height * progress

            if progress >= 1.0:
                self.current_height = self.lift_height
                self.state = ToneArmState.RETURNING
                self.target_angle = self.park_angle

        elif self.state == ToneArmState.RETURNING:
            # Return to park position
            angle_diff = self.target_angle - self.current_angle
            if abs(angle_diff) > 0.5:
                move = self.swing_speed * dt
                if angle_diff > 0:
                    self.current_angle += min(move, angle_diff)
                else:
                    self.current_angle += max(-move, angle_diff)
            else:
                self.current_angle = self.target_angle
                self.current_height = 0
                self.state = ToneArmState.PARKED

    def draw(self, surface):
        """
        Draw the tonearm. Override in subclasses for specific designs.

        Args:
            surface: Pygame surface to draw on
        """
        pass


class WurlitzerPaddleToneArm(ToneArm):
    """
    Authentic Wurlitzer jukebox tonearm with paddle design.
    Scaled for 420x420 popup window.
    """

    def __init__(self, x, y, length=180):
        super().__init__(x, y, length)

        # Tonearm dimensions (scaled for smaller popup)
        self.arm_length = length * 0.85       # Main paddle arm
        self.head_radius = length * 0.15      # Large circular head at top
        self.base_width = 70                  # Flared base width (pixels)
        self.top_width = 70                   # Top width of paddle (pixels)

        # Angle positions (override parent class defaults)
        self.park_angle = -80        # Parked position (more backward)
        self.play_angle = -44        # Playing position (start)
        self.end_angle = -20         # End position
        self.current_angle = -80     # Start at park position
        self.target_angle = -80      # Initial target

        # Visual parameters
        self.arm_color = (140, 140, 145)          # Gray metal
        self.arm_shadow = (100, 100, 105)         # Darker edge
        self.arm_highlight = (170, 170, 175)      # Light edge
        self.head_color = (130, 130, 135)         # Cartridge head
        self.base_color = (120, 120, 125)         # Base/pivot area
        self.pivot_brass = (180, 150, 100)        # Brass pivot hardware

    def update(self, dt):
        """Override parent update to handle tracking movement during playback."""
        # Call parent update first
        super().update(dt)

        # Additional tracking movement during PLAYING state
        if self.is_playing():
            # Smoothly move toward target angle during playback
            angle_diff = self.target_angle - self.current_angle
            if abs(angle_diff) > 0.1:
                # Slow, continuous tracking movement
                move_speed = 5  # degrees per second
                if angle_diff > 0:
                    self.current_angle += min(move_speed * dt, angle_diff)
                else:
                    self.current_angle += max(-move_speed * dt, angle_diff)

    def draw(self, surface):
        """
        Draw the Wurlitzer paddle-style tonearm.

        Args:
            surface: Pygame surface to draw on
        """
        # Calculate the actual pivot position with height offset
        pivot_x = self.pivot_x
        pivot_y = self.pivot_y + self.current_height

        # Base angle (for bottom pivot - arm extends upward)
        angle_rad = math.radians(self.current_angle + self.play_wobble)

        # Calculate head center position (top of arm)
        head_x = pivot_x + self.arm_length * math.sin(angle_rad)
        head_y = pivot_y - self.arm_length * math.cos(angle_rad)

        # Calculate the four corners of the tapered paddle
        # Bottom corners (wider)
        base_half = self.base_width / 2
        perp_angle = angle_rad + math.pi / 2

        base_left_x = pivot_x + base_half * math.cos(perp_angle)
        base_left_y = pivot_y + base_half * math.sin(perp_angle)
        base_right_x = pivot_x - base_half * math.cos(perp_angle)
        base_right_y = pivot_y - base_half * math.sin(perp_angle)

        # Top corners (narrower, at base of head)
        top_half = self.top_width / 2
        top_offset = self.arm_length * 0.85  # Leave room for head

        top_center_x = pivot_x + top_offset * math.sin(angle_rad)
        top_center_y = pivot_y - top_offset * math.cos(angle_rad)

        top_left_x = top_center_x + top_half * math.cos(perp_angle)
        top_left_y = top_center_y + top_half * math.sin(perp_angle)
        top_right_x = top_center_x - top_half * math.cos(perp_angle)
        top_right_y = top_center_y - top_half * math.sin(perp_angle)

        # Draw the flared base (bell shape)
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

        # Draw the main paddle arm (tapered trapezoid)
        paddle_points = [
            (int(base_left_x), int(base_left_y)),
            (int(base_right_x), int(base_right_y)),
            (int(top_right_x), int(top_right_y)),
            (int(top_left_x), int(top_left_y))
        ]

        # Main paddle body
        pygame.draw.polygon(surface, self.arm_color, paddle_points)

        # Left edge highlight (thicker for wide paddle)
        pygame.draw.line(surface, self.arm_highlight,
                        (int(base_left_x), int(base_left_y)),
                        (int(top_left_x), int(top_left_y)), 35)

        # Right edge shadow (thicker for wide paddle)
        pygame.draw.line(surface, self.arm_shadow,
                        (int(base_right_x), int(base_right_y)),
                        (int(top_right_x), int(top_right_y)), 35)

        # Draw the large circular head (cartridge assembly)
        pygame.draw.circle(surface, self.head_color,
                          (int(head_x), int(head_y)), int(self.head_radius))

        # Head outline
        pygame.draw.circle(surface, self.arm_shadow,
                          (int(head_x), int(head_y)), int(self.head_radius), 2)

        # Two parallel grooves on the head
        groove_length = self.head_radius * 0.6
        groove_spacing = self.head_radius * 0.25
        groove_angle = angle_rad

        for offset in [-groove_spacing, groove_spacing]:
            groove_start_x = head_x + offset * math.cos(perp_angle) - (groove_length/2) * math.sin(groove_angle)
            groove_start_y = head_y + offset * math.sin(perp_angle) + (groove_length/2) * math.cos(groove_angle)
            groove_end_x = head_x + offset * math.cos(perp_angle) + (groove_length/2) * math.sin(groove_angle)
            groove_end_y = head_y + offset * math.sin(perp_angle) - (groove_length/2) * math.cos(groove_angle)

            pygame.draw.line(surface, self.arm_shadow,
                           (int(groove_start_x), int(groove_start_y)),
                           (int(groove_end_x), int(groove_end_y)), 2)

        # Draw needle extending from bottom of head
        needle_length = self.head_radius * 0.4
        needle_x = head_x + (self.head_radius + needle_length) * math.sin(angle_rad)
        needle_y = head_y - (self.head_radius + needle_length) * math.cos(angle_rad)

        pygame.draw.line(surface, (80, 80, 85),
                        (head_x, head_y), (needle_x, needle_y), 3)

        # Needle tip
        pygame.draw.circle(surface, self.needle_color,
                          (int(needle_x), int(needle_y)), 3)

        # Draw brass pivot mechanism (visible on the arm)
        pivot_pos_y = pivot_y - self.arm_length * 0.3
        pivot_pos_x = pivot_x + self.arm_length * 0.3 * math.sin(angle_rad)

        pygame.draw.circle(surface, self.pivot_brass,
                          (int(pivot_pos_x), int(pivot_pos_y)), 6)
        pygame.draw.circle(surface, (150, 120, 80),
                          (int(pivot_pos_x), int(pivot_pos_y)), 6, 2)
        pygame.draw.circle(surface, (100, 80, 50),
                          (int(pivot_pos_x), int(pivot_pos_y)), 2)

        # Draw main pivot point at base
        pygame.draw.circle(surface, self.base_color, (pivot_x, pivot_y), 12)
        pygame.draw.circle(surface, self.arm_shadow, (pivot_x, pivot_y), 12, 2)
        pygame.draw.circle(surface, (80, 80, 85), (pivot_x, pivot_y), 5)
        pygame.draw.circle(surface, (60, 60, 65), (pivot_x, pivot_y), 2)


# ============================================================================
# TEXT WRAPPING AND FITTING FUNCTIONS
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
    Rotate a record image in real-time with authentic Wurlitzer tonearm animation.

    Displays the record image in a pygame window with smooth rotation animation
    at 30 FPS and an animated Wurlitzer paddle-style tonearm that swings out,
    lowers onto the record, tracks across during playback, and returns to park.

    The tonearm auto-starts 2 seconds after the popup opens and tracks across
    the record over 30 seconds. The popup continues until rotation_stop_flag
    is set by external logic (idle timeout, keypress, or song ending).

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

        # Convert to RGBA to preserve transparency
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')

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

        # Scale record to fill window completely (420x420 for 420x420 window)
        record_display_size = int(window_width * 1.00)  # ~420px for 420px window
        pil_image = pil_image.resize((record_display_size, record_display_size), Image.LANCZOS)

        # Convert PIL image to pygame surface using raw bytes
        # This preserves exact color values and transparency
        raw_bytes = pil_image.tobytes()
        original_surface = pygame.image.fromstring(raw_bytes, pil_image.size, 'RGBA')

        clock = pygame.time.Clock()

        # Record position - centered in window
        record_x = window_width // 2
        record_y = int(window_height * 0.50)  # ~210 for 420px window (centered)

        # Create Wurlitzer tonearm (scaled for popup window)
        tonearm_pivot_x = record_x
        tonearm_pivot_y = int(window_height * 0.95)  # ~475 for 500px window
        tonearm_length = int(window_width * 0.55)    # ~275 for 500px window
        tonearm = WurlitzerPaddleToneArm(tonearm_pivot_x, tonearm_pivot_y, tonearm_length)

        # Timing and animation settings
        auto_start_delay = 2.0      # Wait 2 seconds before auto-playing
        elapsed_time = 0            # Time since popup started
        auto_started = False        # Flag to track if auto-start happened

        play_time = 0               # Elapsed time while tonearm is playing
        track_duration = 30         # Default tracking duration

        angle = 0
        running = True

        print(f"Pygame record rotation with tonearm started at ({window_x}, {window_y}) with size {window_width}x{window_height}")
        print(f"Record: {record_display_size}x{record_display_size} at ({record_x}, {record_y})")
        print(f"Tonearm pivot: ({tonearm_pivot_x}, {tonearm_pivot_y}), length: {tonearm_length}")

        while running and not rotation_stop_flag.is_set():
            dt = clock.tick(RECORD_ROTATION_FPS) / 1000.0  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Close popup on any keypress
                elif event.type == pygame.KEYDOWN:
                    print(f"Pygame: Keypress detected - closing popup")
                    rotation_stop_flag.set()
                    running = False

            # Auto-start tonearm after delay
            if not auto_started:
                elapsed_time += dt
                if elapsed_time >= auto_start_delay:
                    auto_started = True
                    play_time = 0
                    tonearm.play_record()
                    print("Tonearm auto-started")

            # Update tonearm animation
            tonearm.update(dt)

            # Update record rotation - start as soon as tonearm starts moving
            if tonearm.get_state() in [ToneArmState.SWINGING_OUT, ToneArmState.LOWERING, ToneArmState.PLAYING]:
                # Rotate record at 45 RPM (240° per second)
                angle = (angle - RECORD_ROTATION_SPEED) % 360
            elif tonearm.is_parked():
                # Stop rotation when parked
                angle = 0
            else:
                # Slow down record rotation when returning
                if angle > 0:
                    angle = (angle - RECORD_ROTATION_SPEED * 0.3) % 360

            # Update tonearm tracking during playback
            if tonearm.is_playing():
                # Track play time and move tonearm across record
                play_time += dt

                # Calculate tonearm position based on elapsed time
                # Interpolate from play_angle to end_angle over track_duration
                progress = min(play_time / track_duration, 1.0)  # 0.0 to 1.0
                current_target = tonearm.play_angle + (tonearm.end_angle - tonearm.play_angle) * progress
                tonearm.target_angle = current_target

                # If we reach the end, stay at end position (popup will close externally)

            # ===== DRAWING =====

            # Fill background with dark grey
            screen.fill(PYGAME_BACKGROUND_COLOR)

            # Draw brown background circle behind record
            brown_background = (101, 67, 33)
            background_radius = int(record_display_size * 0.55)
            pygame.draw.circle(screen, brown_background, (record_x, record_y), background_radius)

            # Rotate the surface by the current angle
            rotated_surface = pygame.transform.rotate(original_surface, angle)

            # Get the rect of rotated surface and center it
            rotated_rect = rotated_surface.get_rect(center=(record_x, record_y))

            # Display rotated record image
            screen.blit(rotated_surface, rotated_rect)

            # Draw tonearm on top of record
            tonearm.draw(screen)

            # Update display
            pygame.display.flip()

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
            artist_name, FONT_PATH, 25, ARTIST_MAX_TEXT_WIDTH, 2, draw
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

        # Log popup opened event
        log_popup_event("popup window rotating opened")

        # Return rotation control flag and start time for lifecycle management
        return rotation_stop_flag, popup_start_time

    except Exception as e:
        print(f"Error displaying rotating record popup: {e}")
        import traceback
        traceback.print_exc()
        return None, None
