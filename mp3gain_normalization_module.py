"""
MP3 Volume Normalization Module
Uses mp3gain to normalize audio levels to 89 dB (radio mode)
"""

import subprocess
import os
import logging

def normalize_mp3(filename):
    """
    Normalize a single MP3 file using mp3gain

    Args:
        filename: The filename (without path) in the 'music' directory

    Returns:
        bool: True if normalization succeeded, False otherwise
    """
    try:
        # Construct full path to music file
        music_path = os.path.join('music', filename)

        # Check if file exists
        if not os.path.exists(music_path):
            logging.error(f"File not found: {music_path}")
            print(f"ERROR: File not found: {music_path}")
            return False

        # Run mp3gain with radio mode (-r) and prevent clipping (-k)
        print(f"Normalizing {filename}...")
        logging.info(f"Starting mp3gain normalization for {filename}")

        result = subprocess.run(
            ["mp3gain-win-1_3_4.exe", "-r", "-k", music_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Log output
        if result.stdout:
            logging.info(f"mp3gain output: {result.stdout}")
            print(f"mp3gain: {result.stdout.strip()}")

        logging.info(f"Successfully normalized {filename}")
        print(f"Successfully normalized {filename}")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"mp3gain failed for {filename}: {e.stderr}")
        print(f"ERROR: mp3gain failed for {filename}")
        print(f"Error output: {e.stderr}")
        return False

    except FileNotFoundError:
        logging.error("mp3gain not found - is it installed and in PATH?")
        print("ERROR: mp3gain not found. Please install mp3gain and add it to your PATH.")
        return False

    except Exception as e:
        logging.error(f"Unexpected error normalizing {filename}: {e}")
        print(f"ERROR: Unexpected error normalizing {filename}: {e}")
        return False
