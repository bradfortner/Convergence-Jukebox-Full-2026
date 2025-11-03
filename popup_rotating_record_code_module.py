"""
Rotating Record Pop-up Code Module
Displays a rotating record during playback based on idle time and song progress

All popup parameters are defined here to keep popup logic self-contained.
"""
import threading
from pathlib import Path
import os
import time
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

# Default song duration in seconds (used if duration cannot be parsed from metadata)
POPUP_DEFAULT_SONG_DURATION = 600

# Popup window properties
POPUP_WINDOW_TITLE = ''  # Empty = no title bar
POPUP_WINDOW_LOCATION = (500, 100)  # (x, y) position on screen
POPUP_WINDOW_BACKGROUND = 'black'
POPUP_WINDOW_NO_TITLEBAR = True
POPUP_WINDOW_KEEP_ON_TOP = True

# Popup image filename
POPUP_IMAGE_FILENAME = 'rotating_record.png'

# ============================================================================


def display_rotating_record_popup():
    """
    Display a rotating record popup during song playback.

    This popup appears after specified idle time and playback duration,
    and closes on any keypress or when the song has specified seconds remaining.

    All timing parameters are configured at module level for easy customization.

    Returns:
        tuple: (popup_window, popup_start_time, popup_duration) for lifecycle management
               - popup_window: FreeSimpleGUI Window object
               - popup_start_time: time.time() when popup was created
               - popup_duration: duration to keep popup open (None = manual close only)
    """

    try:
        # Use the rotating record image
        record_filename = POPUP_IMAGE_FILENAME

        if not os.path.exists(record_filename):
            print(f"Warning: {record_filename} not found")
            return None, None, None

        layout = [
            [sg.Image(filename=record_filename, key='--ROTATING_RECORD_IMAGE--')]
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

        # Popup duration - None means manual close (controlled by main event loop)
        popup_duration = None

        print("Rotating record popup created and displayed")

        # Return the popup window to be processed by main event loop
        # popup_duration=None means the popup closes via keypress or time_remaining check
        return popup_window, popup_start_time, popup_duration

    except Exception as e:
        print(f"Error displaying rotating record popup: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
