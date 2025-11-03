"""
Rotating Record Pop-up Code Module
Displays a rotating record during playback based on idle time and song progress
"""
import threading
from pathlib import Path
import os
import time
import FreeSimpleGUI as sg


def display_rotating_record_popup():
    """
    Display a rotating record popup during song playback.

    This popup appears after 20 seconds of playback and 20 seconds of idle time,
    and closes on any keypress or when the song has 5 seconds remaining.

    Returns:
        tuple: (popup_window, popup_start_time) for lifecycle management
    """

    try:
        # Use the rotating record image
        record_filename = 'rotating_record.png'

        if not os.path.exists(record_filename):
            print(f"Warning: {record_filename} not found")
            return None, None

        layout = [
            [sg.Image(filename=record_filename, key='--ROTATING_RECORD_IMAGE--')]
        ]

        popup_window = sg.Window(
            '',  # No title
            layout,
            no_titlebar=True,
            keep_on_top=True,
            location=(500, 100),
            background_color='black',
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

        # Return the popup window to be processed by main event loop
        return popup_window, popup_start_time

    except Exception as e:
        print(f"Error displaying rotating record popup: {e}")
        import traceback
        traceback.print_exc()
        return None, None
