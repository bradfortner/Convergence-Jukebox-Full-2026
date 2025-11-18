"""
CONVERGENCE JUKEBOX - FULL INTEGRATED VERSION
Version 0.81 - Combined Engine + GUI with Targeted VLC Output Suppression

This is an integrated version combining:
- main_jukebox_engine_2026.py (Engine: Music playback management)
- 0.67 - main_jukebox_GUI_2026.py (GUI: User interface)

Architecture:
- Engine runs in daemon thread for non-blocking playback
- GUI runs in main thread for interactive events
- Thread-safe separation of concerns
- Maintains memory efficiency and responsiveness

Key Features:
- VLC integration for audio playback
- FreeSimpleGUI for user interface
- Background threading for engine
- Event-driven GUI with queue communication
- Pygame progress bar for MP3 metadata generation
"""

# ============================================================================
# SECTION 1: CONSOLIDATED IMPORTS
# ============================================================================

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from background_image_module import background_image
from calendar import c
from control_button_screen_layout_module import create_control_button_screen_layout
from datetime import datetime, timedelta
from datetime import datetime, timedelta # required for logging timestamp
from disable_a_selection_buttons_module import disable_a_selection_buttons as disable_a_buttons_module
from disable_b_selection_buttons_module import disable_b_selection_buttons as disable_b_buttons_module
from disable_c_selection_buttons_module import disable_c_selection_buttons as disable_c_buttons_module
from enable_all_buttons_module import enable_all_buttons as enable_all_buttons_module
from font_size_window_updates_module import reset_button_fonts, update_selection_button_text, adjust_button_fonts_by_length, create_font_size_window_updates
from gc import disable
from info_screen_layout_module import create_info_screen_layout
from jukebox_selection_screen_layout_module import create_jukebox_selection_screen_layout
from operator import itemgetter
from popup_45rpm_now_playing_code_module import display_45rpm_now_playing_popup
from metadata_progress_bar_module import MetadataProgressBar
from popup_45rpm_song_selection_code_module import display_45rpm_popup
from popup_rotating_record_code_module import display_rotating_record_popup, log_popup_event
from song_label_cache_module import clear_cache as clear_song_label_cache
import artist_label_mapping_module  # Load artist-to-label mappings at startup
import year_range_label_mapping_module  # Load year-range-to-label mappings at startup
from queue import Queue, Empty
from search_window_button_layout_module import create_search_window_button_layout
from the_bands_name_check_module import the_bands_name_check as check_bands_module
from tinytag import TinyTag
from token import NUMBER
from typing import List, Dict, Any, Optional, Tuple
# from upcoming_selections_update_module import update_upcoming_selections

def format_time_remaining(seconds):
    """
    Format seconds as MM:SS for display.

    Args:
        seconds (float): Number of seconds remaining

    Returns:
        str: Formatted time string like "03:45" or "00:12"
    """
    # Convert to integer first to eliminate floating point precision issues
    seconds = int(seconds)
    if seconds < 0:
        seconds = 0
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

# INLINE: Fixed function to update upcoming selections display using correct element keys
def update_upcoming_selections(window, upcoming_list):
    """Update upcoming selections display in the info screen window using individual element keys"""
    try:
        if not window:
            return

        # Element keys for the upcoming songs display (from info_screen_layout_module.py)
        upcoming_keys = [
            '--upcoming_one--',
            '--upcoming_two--',
            '--upcoming_three--',
            '--upcoming_four--',
            '--upcoming_five--',
            '--upcoming_six--',
            '--upcoming_seven--',
            '--upcoming_eight--',
            '--upcoming_nine--',
            '--upcoming_ten--'
        ]

        # Clear all upcoming selection displays first
        for key in upcoming_keys:
            try:
                if key in window.AllKeysDict:
                    window[key].update('')
            except Exception as e:
                continue

        # Update with actual upcoming songs
        if upcoming_list and len(upcoming_list) > 0:
            for i, song in enumerate(upcoming_list):
                if i >= len(upcoming_keys):
                    break  # Don't exceed available elements
                try:
                    if upcoming_keys[i] in window.AllKeysDict:
                        window[upcoming_keys[i]].update(f"{i+1}. {song}")
                except Exception as e:
                    continue

    except Exception as e:
        import traceback
        traceback.print_exc()
import FreeSimpleGUI as sg
import gc
import glob
import json
import os
import psutil
import pygame
import random
import sys
import textwrap
import threading
import time

# Suppress VLC stderr ONLY during import to prevent plugin cache messages
import sys as _sys_for_vlc_suppress
_vlc_stderr_backup = _sys_for_vlc_suppress.stderr
_vlc_devnull = open(__import__('os').devnull, 'w')
_sys_for_vlc_suppress.stderr = _vlc_devnull
try:
    import vlc
finally:
    _sys_for_vlc_suppress.stderr = _vlc_stderr_backup
    _vlc_devnull.close()


# ============================================================================
# SECTION 2: UTILITY CLASSES
# ============================================================================


class Colors:
    """ANSI color codes for terminal output"""
    HEADER: str = '\033[95m'
    BLUE: str = '\033[94m'
    CYAN: str = '\033[96m'
    GREEN: str = '\033[32m'
    YELLOW: str = '\033[93m'
    RED: str = '\033[91m'
    ENDC: str = '\033[0m'
    BOLD: str = '\033[1m'
    UNDERLINE: str = '\033[4m'

    @staticmethod
    def disable_on_windows() -> None:
        """Disable colors on Windows if not supported"""
        if sys.platform.startswith('win'):
            # Windows 10+ supports ANSI codes, but older versions don't
            # We'll keep colors enabled by default
            pass


class JukeboxEngineException(Exception):
    """Custom exception for Jukebox Engine errors"""
    pass


# ============================================================================
# SECTION 3: JUKEBOX ENGINE CLASS
# ============================================================================

class JukeboxEngine:
    """Main Convergence Jukebox Engine - Manages music playback and playlist management

    Version 0.9: STABLE + FEATURES HYBRID
    - Base: Version 0.8 (proven stable, no memory leaks)
    - Enhanced with: Validation, I/O refactoring, and Statistics from 0.91

    Improvements in this version:
    - #1: Input Validation for data integrity
    - #2: Refactored I/O Methods for testability
    - #3: Song Statistics tracking and reporting
    - Plus: Console colors, logging, config file support (from 0.8)

    Key Feature: NO THREADING - Avoids the memory leak introduced in 0.9+
    """

    # Configuration constants
    SLEEP_TIME: float = 0.5
    TIMESTAMP_ROUNDING: float = 0.5
    CONFIG_FILE: str = 'jukebox_config.json'
    GC_THRESHOLD: int = 100

    def __init__(self) -> None:
        """Initialize Jukebox Engine with all required variables and file setup"""
        # Initialize data structures
        self.music_id3_metadata_list: List[tuple] = []
        self.music_master_song_list: List[Dict[str, str]] = []
        self.random_music_playlist: List[int] = []
        self.paid_music_playlist: List[int] = []
        self.final_genre_list: List[str] = []

        # Memory optimization counters
        self.gc_counter: int = 0

        # VLC Media Player instance for accessing playback state
        self.vlc_media_player = None

        # Current song metadata
        self.artist_name: str = ""
        self.song_name: str = ""
        self.album_name: str = ""
        self.song_duration: str = ""
        self.song_year: str = ""
        self.song_genre: str = ""

        # Genre flags
        self.genre0: str = "null"
        self.genre1: str = "null"
        self.genre2: str = "null"
        self.genre3: str = "null"

        # Get directory path for cross-platform compatibility
        self.dir_path: str = os.path.dirname(os.path.realpath(__file__))

        # Load configuration
        self.config: Dict[str, Any] = self._load_config()

        # Define standard file and directory paths using os.path.join for cross-platform compatibility
        self.music_dir: str = os.path.join(self.dir_path, self.config['paths']['music_dir'])
        self.log_file: str = os.path.join(self.dir_path, self.config['paths']['log_file'])
        self.genre_flags_file: str = os.path.join(self.dir_path, self.config['paths']['genre_flags_file'])
        self.music_master_song_list_file: str = os.path.join(self.dir_path, self.config['paths']['music_master_song_list_file'])
        self.music_master_song_list_check_file: str = os.path.join(self.dir_path, self.config['paths']['music_master_song_list_check_file'])
        self.paid_music_playlist_file: str = os.path.join(self.dir_path, self.config['paths']['paid_music_playlist_file'])
        self.current_song_playing_file: str = os.path.join(self.dir_path, self.config['paths']['current_song_playing_file'])

        # Initialize log file and required data files
        self._setup_files()
        self._print_header("Jukebox Engine Initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config file or create default config

        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        config_path: str = os.path.join(self.dir_path, self.CONFIG_FILE)

        # Default configuration
        default_config: Dict[str, Any] = {
            "logging": {
                "enabled": True,
                "level": "INFO",
                "format": "{timestamp} {level}: {message}"
            },
            "paths": {
                "music_dir": "music",
                "log_file": "log.txt",
                "genre_flags_file": "GenreFlagsList.txt",
                "music_master_song_list_file": "MusicMasterSongList.txt",
                "music_master_song_list_check_file": "MusicMasterSongListCheck.txt",
                "paid_music_playlist_file": "PaidMusicPlayList.txt",
                "current_song_playing_file": "CurrentSongPlaying.txt"
            },
            "console": {
                "colors_enabled": True,
                "show_system_info": True,
                "verbose": False
            }
        }

        # Try to load existing config
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as config_file:
                    loaded_config: Dict[str, Any] = json.load(config_file)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(default_config, loaded_config)
            except (IOError, json.JSONDecodeError) as e:
                print(f"{Colors.YELLOW}Warning: Failed to load config file: {e}{Colors.ENDC}")
                print(f"{Colors.YELLOW}Using default configuration{Colors.ENDC}")
                return default_config
        else:
            # Create default config file
            try:
                with open(config_path, 'w') as config_file:
                    json.dump(default_config, config_file, indent=2)
                print(f"{Colors.GREEN}Created default config file: {config_path}{Colors.ENDC}")
            except IOError as e:
                print(f"{Colors.YELLOW}Warning: Failed to create config file: {e}{Colors.ENDC}")

            return default_config

    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with default config, preserving defaults for missing keys

        Args:
            default (Dict[str, Any]): Default configuration
            loaded (Dict[str, Any]): Loaded configuration

        Returns:
            Dict[str, Any]: Merged configuration
        """
        merged: Dict[str, Any] = default.copy()
        for key, value in loaded.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        return merged

    # ============================================================================
    # IMPROVEMENT #1: INPUT VALIDATION METHODS
    # ============================================================================

    def _validate_song_index(self, index: int, playlist_type: str = 'random') -> Tuple[bool, str]:
        """Validate song index is within bounds.

        Args:
            index (int): The song index to validate
            playlist_type (str): Type of playlist ('random' or 'paid')

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(index, int):
            return False, f"Song index must be integer, got {type(index).__name__}"

        if index < 0:
            return False, f"Song index cannot be negative: {index}"

        if index >= len(self.music_master_song_list):
            return False, f"Song index {index} out of range (max: {len(self.music_master_song_list) - 1})"

        return True, ""

    def _validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """Validate file path exists and is accessible.

        Args:
            file_path (str): The file path to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(file_path, str):
            return False, f"File path must be string, got {type(file_path).__name__}"

        if not file_path:
            return False, "File path cannot be empty"

        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"

        return True, ""

    def _validate_json_data(self, data: Any, data_type: str) -> Tuple[bool, str]:
        """Validate JSON data structure integrity.

        Args:
            data (Any): The data to validate
            data_type (str): Type of data ('playlist', 'genres', 'statistics')

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if data is None:
            return False, f"{data_type} data is None"

        if data_type == 'playlist':
            if not isinstance(data, list):
                return False, f"Playlist must be list, got {type(data).__name__}"
            for item in data:
                if not isinstance(item, int):
                    return False, f"Playlist items must be integers, got {type(item).__name__}"

        elif data_type == 'genres':
            if not isinstance(data, list):
                return False, f"Genres must be list, got {type(data).__name__}"
            if len(data) != 4:
                return False, f"Genres list must have 4 items, got {len(data)}"
            for item in data:
                if not isinstance(item, str):
                    return False, f"Genre items must be strings, got {type(item).__name__}"

        elif data_type == 'statistics':
            if not isinstance(data, dict):
                return False, f"Statistics must be dict, got {type(data).__name__}"

        return True, ""

    def _validate_playlist_entry(self, song_index: int) -> bool:
        """Validate a song index before adding to playlist.

        Args:
            song_index (int): The song index to validate

        Returns:
            bool: True if valid, False otherwise
        """
        is_valid, error_msg = self._validate_song_index(song_index)
        if not is_valid:
            self._log_error(f"Invalid playlist entry: {error_msg}")
            return False
        return True

    # ============================================================================
    # IMPROVEMENT #2: REFACTORED I/O METHODS FOR TESTABILITY
    # ============================================================================

    def _read_json_file(self, file_path: str) -> Tuple[bool, Any]:
        """Read JSON file with validation.

        Args:
            file_path (str): Path to JSON file

        Returns:
            Tuple[bool, Any]: (success, data)
        """
        try:
            is_valid, error_msg = self._validate_file_path(file_path)
            if not is_valid:
                self._log_error(f"Cannot read file: {error_msg}")
                return False, None

            with open(file_path, 'r') as f:
                data = json.load(f)
            return True, data
        except (IOError, json.JSONDecodeError) as e:
            self._log_error(f"Failed to read JSON file {file_path}: {e}")
            return False, None

    def _write_json_file(self, file_path: str, data: Any) -> bool:
        """Write JSON file with validation.

        Args:
            file_path (str): Path to JSON file
            data (Any): Data to write

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not file_path:
                self._log_error("Cannot write file: path is empty")
                return False

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except (IOError, json.JSONDecodeError) as e:
            self._log_error(f"Failed to write JSON file {file_path}: {e}")
            return False

    def _read_paid_playlist(self) -> Tuple[bool, List[int]]:
        """Read paid playlist file with validation.

        Returns:
            Tuple[bool, List[int]]: (success, playlist)
        """
        success, data = self._read_json_file(self.paid_music_playlist_file)
        if not success:
            return False, []

        is_valid, error_msg = self._validate_json_data(data, 'playlist')
        if not is_valid:
            self._log_error(f"Invalid paid playlist data: {error_msg}")
            return False, []

        return True, data

    def _write_paid_playlist(self, playlist: List[int]) -> bool:
        """Write paid playlist file with validation.

        Args:
            playlist (List[int]): Paid playlist to write

        Returns:
            bool: True if successful, False otherwise
        """
        is_valid, error_msg = self._validate_json_data(playlist, 'playlist')
        if not is_valid:
            self._log_error(f"Cannot write playlist: {error_msg}")
            return False

        return self._write_json_file(self.paid_music_playlist_file, playlist)

    def _read_genres(self) -> Tuple[bool, List[str]]:
        """Read genre flags file with validation.

        Returns:
            Tuple[bool, List[str]]: (success, genres)
        """
        success, data = self._read_json_file(self.genre_flags_file)
        if not success:
            return False, ['null', 'null', 'null', 'null']

        is_valid, error_msg = self._validate_json_data(data, 'genres')
        if not is_valid:
            self._log_error(f"Invalid genre data: {error_msg}")
            return False, ['null', 'null', 'null', 'null']

        return True, data

    def _read_master_song_list(self) -> Tuple[bool, List[Dict[str, str]]]:
        """Read master song list file with validation.

        Returns:
            Tuple[bool, List[Dict]]: (success, song_list)
        """
        success, data = self._read_json_file(self.music_master_song_list_file)
        if not success:
            return False, []

        if not isinstance(data, list):
            self._log_error(f"Master song list must be list, got {type(data).__name__}")
            return False, []

        return True, data

    # ============================================================================
    # LOGGING AND OUTPUT METHODS
    # ============================================================================

    def _print_header(self, message: str) -> None:
        """Print a formatted header message to console

        Args:
            message (str): The message to display
        """
        if self.config['console']['colors_enabled']:
            print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
            print(f"{message.center(60)}")
            print(f"{'='*60}{Colors.ENDC}\n")
        else:
            print(f"\n{'='*60}")
            print(f"{message.center(60)}")
            print(f"{'='*60}\n")

    def _print_section(self, message: str) -> None:
        """Print a formatted section header

        Args:
            message (str): The section message
        """
        if self.config['console']['colors_enabled']:
            print(f"{Colors.CYAN}{Colors.BOLD}{message}{Colors.ENDC}")
        else:
            print(message)

    def _print_success(self, message: str) -> None:
        """Print a success message in green

        Args:
            message (str): The success message
        """
        if self.config['console']['colors_enabled']:
            print(f"{Colors.GREEN}[+] {message}{Colors.ENDC}")
        else:
            print(f"[+] {message}")

    def _print_warning(self, message: str) -> None:
        """Print a warning message in yellow

        Args:
            message (str): The warning message
        """
        if self.config['console']['colors_enabled']:
            print(f"{Colors.YELLOW}[!] {message}{Colors.ENDC}")
        else:
            print(f"[!] {message}")

    def _print_error_msg(self, message: str) -> None:
        """Print an error message in red

        Args:
            message (str): The error message
        """
        if self.config['console']['colors_enabled']:
            print(f"{Colors.RED}[-] {message}{Colors.ENDC}")
        else:
            print(f"[-] {message}")

    def _get_rounded_timestamp(self) -> datetime:
        """Helper method to get current timestamp rounded to nearest second

        Returns:
            datetime: Current timestamp rounded to nearest second
        """
        try:
            now: datetime = datetime.now()
            rounded_now: datetime = now + timedelta(seconds=self.TIMESTAMP_ROUNDING)
            return rounded_now.replace(microsecond=0)
        except Exception as e:
            self._print_error_msg(f"Failed to get timestamp: {e}")
            return datetime.now()

    def _log_error(self, error_message: str) -> None:
        """Log error message to both console and log file

        Args:
            error_message (str): The error message to log
        """
        timestamp: datetime = self._get_rounded_timestamp()
        error_log: str = f"\n{timestamp} ERROR: {error_message}"

        # Only log to file if logging is enabled
        if self.config['logging']['enabled']:
            try:
                with open(self.log_file, 'a') as log:
                    log.write(error_log)
            except Exception as e:
                self._print_error_msg(f"Could not write to log file: {e}")

        self._print_error_msg(error_message)

    def _setup_files(self) -> None:
        """Check for files on disk. If they don't exist, create them"""
        # Create date and time stamp for log file
        now: datetime = self._get_rounded_timestamp()

        # Setup log file
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w') as log:
                    log.write(str(now) + ' Jukebox Engine Started - New Log File Created,')
                self._print_success(f"Created log file: {os.path.basename(self.log_file)}")
            else:
                with open(self.log_file, 'a') as log:
                    log.write('\n' + str(now) + ' Jukebox Engine Restarted,')
        except IOError as e:
            self._log_error(f"Failed to setup log.txt: {e}")

        # Setup genre flags file
        try:
            if not os.path.exists(self.genre_flags_file):
                with open(self.genre_flags_file, 'w') as genre_flags_file:
                    genre_flags_list: List[str] = ['null', 'null', 'null', 'null']
                    json.dump(genre_flags_list, genre_flags_file)
                self._print_success(f"Created genre flags file: {os.path.basename(self.genre_flags_file)}")
        except (IOError, json.JSONDecodeError) as e:
            self._log_error(f"Failed to setup GenreFlagsList.txt: {e}")

        # Setup music master song list check file
        try:
            if not os.path.exists(self.music_master_song_list_check_file):
                with open(self.music_master_song_list_check_file, 'w') as check_file:
                    json.dump([], check_file)
                self._print_success(f"Created song list check file: {os.path.basename(self.music_master_song_list_check_file)}")
        except (IOError, json.JSONDecodeError) as e:
            self._log_error(f"Failed to setup MusicMasterSongListCheck.txt: {e}")

        # Setup paid music playlist file
        try:
            if not os.path.exists(self.paid_music_playlist_file):
                with open(self.paid_music_playlist_file, 'w') as paid_list_file:
                    json.dump([], paid_list_file)
                self._print_success(f"Created paid playlist file: {os.path.basename(self.paid_music_playlist_file)}")
        except (IOError, json.JSONDecodeError) as e:
            self._log_error(f"Failed to setup PaidMusicPlayList.txt: {e}")

    def assign_song_data(self, playlist_type: str = 'random') -> bool:
        """
        Assign song metadata from specified playlist to instance variables

        Args:
            playlist_type (str): Either 'random' or 'paid' to specify which playlist to use

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Determine which playlist to use and validate
            if playlist_type == 'random':
                if not self.random_music_playlist:
                    self._log_error("Random playlist is empty")
                    return False
                song_index: int = self.random_music_playlist[0]
            elif playlist_type == 'paid':
                if not self.paid_music_playlist:
                    self._log_error("Paid playlist is empty")
                    return False
                song_index: int = int(self.paid_music_playlist[0])
            else:
                self._log_error(f"Invalid playlist type: {playlist_type}")
                return False

            # Validate song index
            if song_index >= len(self.music_master_song_list):
                self._log_error(f"Song index {song_index} out of range")
                return False

            # Assign song metadata to instance variables
            self.artist_name = self.music_master_song_list[song_index]['artist']
            self.song_name = self.music_master_song_list[song_index]['title']
            self.album_name = self.music_master_song_list[song_index]['album']
            self.song_duration = self.music_master_song_list[song_index]['duration']
            self.song_year = self.music_master_song_list[song_index]['year']
            self.song_genre = self.music_master_song_list[song_index]['comment']
            return True
        except (KeyError, IndexError, TypeError, ValueError) as e:
            self._log_error(f"Failed to assign {playlist_type} song data: {e}")
            return False

    def generate_mp3_metadata(self) -> bool:
        """Generate MP3 metadata from music directory

        Returns:
            bool: True if successful, False otherwise
        """
        progress_bar = None
        try:
            self._print_header("Generating MP3 Metadata")
            print("Please Be Patient - Regenerating Your Songlist From Scratch")
            print("Music Will Start When Finished\n")

            counter: int = 0

            # Get music files using cross-platform path
            try:
                mp3_music_files: List[str] = glob.glob(os.path.join(self.music_dir, '*.mp3'))
            except Exception as e:
                self._log_error(f"Failed to search for MP3 files: {e}")
                return False

            if not mp3_music_files:
                self._log_error("No MP3 files found in music directory")
                return False

            print(f"Found {len(mp3_music_files)} MP3 files. Processing...\n")

            # Initialize and start progress bar in separate thread
            progress_bar = MetadataProgressBar(len(mp3_music_files))
            progress_bar.start()

            for file_path in mp3_music_files:
                try:
                    # Update progress bar with current file
                    file_name = os.path.basename(file_path)
                    progress_bar.update(counter, file_name)

                    id3tag: Optional[Any] = TinyTag.get(file_path)

                    if id3tag is None:
                        self._log_error(f"Could not read metadata from {file_path}")
                        continue

                    get_song_duration_seconds: str = "%f" % id3tag.duration
                    remove_song_duration_decimals: float = float(get_song_duration_seconds)
                    song_duration_decimals_removed: int = int(remove_song_duration_decimals)
                    song_duration_minutes_seconds: int = int(song_duration_decimals_removed)
                    song_duration: str = time.strftime("%M:%S", time.gmtime(song_duration_minutes_seconds))

                    song_metadata: List[Any] = list((
                        counter,
                        file_path,
                        "%s" % id3tag.title,
                        "%s" % id3tag.artist,
                        "%s" % id3tag.album,
                        "%s" % id3tag.year,
                        "%s" % id3tag.comment,
                        song_duration
                    ))
                    self.music_id3_metadata_list.append(song_metadata)
                    counter += 1
                except Exception as e:
                    self._log_error(f"Failed to extract metadata from {file_path}: {e}")
                    continue

            # Stop progress bar and pause for 1 second
            if progress_bar:
                progress_bar.stop()
                time.sleep(1)  # Pause after progress bar closes

            if not self.music_id3_metadata_list:
                self._log_error("No valid metadata was extracted from MP3 files")
                return False

            self._print_success(f"Extracted metadata from {counter} songs")
            return True
        except Exception as e:
            # Ensure progress bar is stopped on error
            if progress_bar:
                progress_bar.stop()
                time.sleep(1)  # Pause after progress bar closes
            self._log_error(f"Unexpected error in generate_mp3_metadata: {e}")
            return False

    def generate_music_master_song_list_dictionary(self) -> bool:
        """Generate master song list dictionary and save to file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._print_section("Generating Master Song List Dictionary...")

            # Assign keys for MusicMasterSongList Dictionary
            keys: List[str] = ['number', 'location', 'title', 'artist', 'album', 'year', 'comment', 'duration']

            # Build MusicMasterSongList Dictionary
            self.music_master_song_list = [dict(zip(keys, sublst)) for sublst in self.music_id3_metadata_list]

            # Save MusicMasterSongList Dictionary
            try:
                with open(self.music_master_song_list_file, 'w') as master_list_file:
                    json.dump(self.music_master_song_list, master_list_file)
                self._print_success(f"Saved master song list to {os.path.basename(self.music_master_song_list_file)}")
            except (IOError, json.JSONDecodeError) as e:
                self._log_error(f"Failed to save MusicMasterSongList.txt: {e}")
                return False

            # Create and save a file list size value to check if MusicMasterSongList has changed after a reboot
            list_size: int = len(self.music_master_song_list)
            try:
                with open(self.music_master_song_list_check_file, 'w') as check_file:
                    json.dump(list_size, check_file)
                self._print_success(f"Saved song list check file ({list_size} songs)")
            except (IOError, json.JSONDecodeError) as e:
                self._log_error(f"Failed to save MusicMasterSongListCheck.txt: {e}")
                return False

            return True
        except Exception as e:
            self._log_error(f"Unexpected error in generate_music_master_song_list_dictionary: {e}")
            return False

    def play_song(self, song_file_name: str) -> bool:
        """Play a song using VLC media player

        Args:
            song_file_name (str): The full path to the song file to play

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(song_file_name):
                self._log_error(f"Song file not found: {song_file_name}")
                return False

            if self.config['console']['show_system_info']:
                print("\nSystem Info:")
                print(psutil.virtual_memory())
                print("Garbage collection thresholds:", gc.get_threshold())

            # Perform garbage collection
            collected: int = gc.collect()
            if self.config['console']['verbose']:
                print(f"Garbage collector: collected {collected} objects.")

            # VLC Song Playback Code Begin
            try:
                p: vlc.MediaPlayer = vlc.MediaPlayer(song_file_name)
                # Store player as instance variable for popup access
                self.vlc_media_player = p
                p.play()
                if self.config['console']['verbose']:
                    print('is_playing:', p.is_playing())  # 0 = False
                time.sleep(self.SLEEP_TIME)  # sleep because it needs time to start playing
                if self.config['console']['verbose']:
                    print('is_playing:', p.is_playing())  # 1 = True

                while p.is_playing():
                    time.sleep(self.SLEEP_TIME)  # sleep to use less CPU
                # VLC Song Playback Code End
                return True
            except Exception as vlc_error:
                self._log_error(f"VLC playback error for {song_file_name}: {vlc_error}")
                return False
        except Exception as e:
            self._log_error(f"Unexpected error in play_song: {e}")
            return False

    def assign_genres_to_random_play(self) -> bool:
        """Load and assign genres from GenreFlagsList file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._print_section("Loading Genre Configuration...")

            extract_original_assigned_genres: List[str] = []
            unfiltered_final_genre_list: List[str] = []

            try:
                with open(self.genre_flags_file, 'r') as genre_flags_file:
                    genre_flags_list: List[str] = json.load(genre_flags_file)
            except (IOError, json.JSONDecodeError) as e:
                self._log_error(f"Failed to load GenreFlagsList.txt: {e}")
                genre_flags_list: List[str] = ['null', 'null', 'null', 'null']

            self.genre0 = genre_flags_list[0] if len(genre_flags_list) > 0 else 'null'
            self.genre1 = genre_flags_list[1] if len(genre_flags_list) > 1 else 'null'
            self.genre2 = genre_flags_list[2] if len(genre_flags_list) > 2 else 'null'
            self.genre3 = genre_flags_list[3] if len(genre_flags_list) > 3 else 'null'

            # Extract genres from all songs
            for song in self.music_master_song_list:
                try:
                    extract_original_assigned_genres.append(song['comment'])
                except KeyError:
                    self._log_error(f"Missing 'comment' field in song: {song}")
                    continue

            # Split multi-genre selections
            for genre_string in extract_original_assigned_genres:
                if ' ' in genre_string:
                    split_genres: List[str] = genre_string.split()
                    extract_original_assigned_genres.extend(split_genres)

            # Filter and create final genre list
            for genre in extract_original_assigned_genres:
                if ' ' not in genre:
                    unfiltered_final_genre_list.append(genre)

            self.final_genre_list = list(set(unfiltered_final_genre_list))  # removes duplicates
            self.final_genre_list.sort()

            # Print genre information
            print('\nGenres for Random Play:')
            genres: List[str] = [self.genre0, self.genre1, self.genre2, self.genre3]
            for idx, genre in enumerate(genres):
                if genre == 'null':
                    print(f'  Genre {idx}: Not Set')
                else:
                    self._print_success(f"Genre {idx}: {genre}")

            return True
        except Exception as e:
            self._log_error(f"Unexpected error in assign_genres_to_random_play: {e}")
            return False

    def generate_random_song_list(self) -> bool:
        """Generate random song playlist based on genre filters

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._print_section("Generating Random Song Playlist...")

            counter: int = 0
            for song in self.music_master_song_list:
                try:
                    # Skip songs marked with 'norandom'
                    if 'norandom' in song['comment']:
                        counter += 1
                        continue

                    # Add all songs if no genre filters are set
                    if (self.genre0 == "null" and self.genre1 == "null" and
                        self.genre2 == "null" and self.genre3 == "null"):
                        self.random_music_playlist.append(counter)
                    else:
                        # Add songs matching any of the genre filters
                        if self.genre0 != "null" and self.genre0 in song['comment']:
                            self.random_music_playlist.append(counter)
                        elif self.genre1 != "null" and self.genre1 in song['comment']:
                            self.random_music_playlist.append(counter)
                        elif self.genre2 != "null" and self.genre2 in song['comment']:
                            self.random_music_playlist.append(counter)
                        elif self.genre3 != "null" and self.genre3 in song['comment']:
                            self.random_music_playlist.append(counter)

                    counter += 1
                except KeyError as e:
                    self._log_error(f"Missing key in song data: {e}")
                    counter += 1
                    continue

            random.shuffle(self.random_music_playlist)
            self._print_success(f"Generated random playlist with {len(self.random_music_playlist)} songs")
            return True
        except Exception as e:
            self._log_error(f"Unexpected error in generate_random_song_list: {e}")
            return False

    def _log_song_play(self, artist: str, title: str, play_type: str) -> None:
        """Log a song play event to log file

        Args:
            artist (str): The artist name
            title (str): The song title
            play_type (str): Either 'Paid' or 'Random'
        """
        try:
            if self.config['logging']['enabled']:
                with open(self.log_file, 'a') as log:
                    now: datetime = self._get_rounded_timestamp()
                    log.write('\n' + str(now) + ', ' + str(artist) + ' - ' + str(title) + ', Played ' + play_type + ',')
        except IOError as e:
            self._log_error(f"Failed to log song play: {e}")

    def _write_current_song_playing(self, song_location: str) -> None:
        """Write current playing song location to file

        Args:
            song_location (str): The full path to the currently playing song
        """
        try:
            with open(self.current_song_playing_file, "w") as outfile:
                outfile.write(song_location)
        except IOError as e:
            self._log_error(f"Failed to write CurrentSongPlaying.txt: {e}")

    def jukebox_engine(self) -> bool:
        """
        Main jukebox engine - plays paid songs first, then alternates with random songs

        IMPORTANT: This method uses while loops instead of recursion to prevent
        stack overflow. The paid playlist file is checked after each random song,
        enabling real-time additions of paid songs during playback.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._print_header("Jukebox Engine Starting")

            # Main loop: continuously check for paid songs, play them, then play one random song
            while True:
                # Play all paid songs - reload file at each iteration to pick up new requests
                while True:
                    # Reload paid music playlist from file at each iteration to enable real-time additions
                    self.paid_music_playlist = read_paid_playlist(self.paid_music_playlist_file)

                    # If no more paid songs, exit the inner loop
                    if not self.paid_music_playlist:
                        break
                    try:
                        song_index: int = self.paid_music_playlist[0]

                        if song_index >= len(self.music_master_song_list):
                            self._log_error(f"Invalid song index in paid playlist: {song_index}")
                            del self.paid_music_playlist[0]
                            continue

                        song: Dict[str, str] = self.music_master_song_list[song_index]

                        if self.config['console']['colors_enabled']:
                            print(f"\n{Colors.BLUE}Now Playing (PAID): {Colors.BOLD}{song['title']}{Colors.ENDC}")
                            print(f"{Colors.BLUE}Artist: {song['artist']}{Colors.ENDC}")
                            print(f"{Colors.BLUE}Album: {song['album']} ({song['year']}){Colors.ENDC}")
                            print(f"{Colors.BLUE}Duration: {song['duration']} | Genre: {song['comment']}{Colors.ENDC}\n")
                        else:
                            print(f"\nNow Playing (PAID): {song['title']}")
                            print(f"Artist: {song['artist']}")
                            print(f"Album: {song['album']} ({song['year']})")
                            print(f"Duration: {song['duration']} | Genre: {song['comment']}\n")

                        # Save current playing song to disk
                        self._write_current_song_playing(song['location'])

                        # Log paid song play
                        self._log_song_play(song['artist'], song['title'], 'Paid')

                        if not self.play_song(song['location']):
                            self._log_error(f"Failed to play paid song: {song['title']}")

                        # Re-read paid playlist from file before deleting to capture any new selections made while playing
                        # This prevents losing songs that were added during the song playback
                        self.paid_music_playlist = read_paid_playlist(self.paid_music_playlist_file)

                        # Delete song just played from paid playlist
                        try:
                            if self.paid_music_playlist:  # Only delete if there are songs in the list
                                del self.paid_music_playlist[0]
                            write_paid_playlist(self.paid_music_playlist_file, self.paid_music_playlist)
                        except (IOError, json.JSONDecodeError) as e:
                            self._log_error(f"Failed to update PaidMusicPlayList.txt: {e}")
                            break
                    except (KeyError, IndexError, TypeError) as e:
                        self._log_error(f"Error processing paid song: {e}")
                        break

                # Play one random song, then loop back to check for paid songs again
                if self.random_music_playlist:
                    try:
                        if not self.assign_song_data('random'):
                            self._log_error("Failed to assign random song data, skipping")
                            break

                        if self.config['console']['colors_enabled']:
                            print(f"\n{Colors.GREEN}Now Playing (RANDOM): {Colors.BOLD}{self.song_name}{Colors.ENDC}")
                            print(f"{Colors.GREEN}Artist: {self.artist_name}{Colors.ENDC}")
                            print(f"{Colors.GREEN}Album: {self.album_name} ({self.song_year}){Colors.ENDC}")
                            print(f"{Colors.GREEN}Duration: {self.song_duration} | Genre: {self.song_genre}{Colors.ENDC}\n")
                        else:
                            print(f"\nNow Playing (RANDOM): {self.song_name}")
                            print(f"Artist: {self.artist_name}")
                            print(f"Album: {self.album_name} ({self.song_year})")
                            print(f"Duration: {self.song_duration} | Genre: {self.song_genre}\n")

                        # Save current playing song to disk
                        song_index: int = self.random_music_playlist[0]
                        self._write_current_song_playing(self.music_master_song_list[song_index]['location'])

                        # Log random song play
                        self._log_song_play(self.artist_name, self.song_name, 'Random')

                        if not self.play_song(self.music_master_song_list[song_index]['location']):
                            self._log_error(f"Failed to play random song: {self.song_name}")

                        # Move song to end of RandomMusicPlaylist
                        move_first_list_element: int = self.random_music_playlist.pop(0)
                        self.random_music_playlist.append(move_first_list_element)
                        # Loop continues, goes back to check for paid songs again
                    except (KeyError, IndexError, TypeError) as e:
                        self._log_error(f"Error processing random song: {e}")
                        break
                else:
                    # If no random songs in playlist, exit the main loop
                    break

            self._print_section("Jukebox Engine Stopped")
            return True
        except Exception as e:
            self._log_error(f"Unexpected error in jukebox_engine: {e}")
            return False

    def run(self) -> None:
        """Main execution method"""
        try:
            # Check to see if MusicMasterSongList exists on disk
            if os.path.exists(self.music_master_song_list_file):
                self._print_section("Found existing music database")

                # Count number of files in music directory
                try:
                    current_file_count: int = len(glob.glob(os.path.join(self.music_dir, '*.mp3')))
                    print(f"Current MP3 files in directory: {current_file_count}")
                except Exception as e:
                    self._log_error(f"Failed to count MP3 files: {e}")
                    current_file_count: int = -1

                # Open MusicMasterSongListCheck generated from previous run
                try:
                    with open(self.music_master_song_list_check_file, 'r') as check_file:
                        stored_file_count: int = json.load(check_file)
                        print(f"Stored MP3 file count: {stored_file_count}")
                except (IOError, json.JSONDecodeError) as e:
                    self._log_error(f"Failed to load MusicMasterSongListCheck.txt: {e}")
                    stored_file_count: int = -1

                # Check for match
                if current_file_count == stored_file_count and current_file_count != -1:
                    self._print_success("Music database matches current files")
                    # Open MusicMasterSongList dictionary
                    try:
                        with open(self.music_master_song_list_file, 'r') as master_list_file:
                            self.music_master_song_list = json.load(master_list_file)

                        # MusicMasterSongList matches, run required functions
                        if (self.assign_genres_to_random_play() and
                            self.generate_random_song_list()):
                            self._print_success("Engine initialization complete - ready for playback")
                            return
                    except (IOError, json.JSONDecodeError) as e:
                        self._log_error(f"Failed to load MusicMasterSongList.txt: {e}")
                else:
                    self._print_warning("Music database count mismatch - regenerating")

            # If no match or file doesn't exist, regenerate everything
            if (self.generate_mp3_metadata() and
                self.generate_music_master_song_list_dictionary() and
                self.assign_genres_to_random_play() and
                self.generate_random_song_list()):
                self._print_success("Engine initialization complete - ready for playback")
            else:
                self._log_error("Failed to initialize jukebox engine")
        except Exception as e:
            self._log_error(f"Critical error in run method: {e}")


# Main execution

# ============================================================================
# SECTION 3B: FILE LOCKING HELPER FUNCTIONS FOR PAIDMUSICPLAYLIST.TXT
# ============================================================================

def read_paid_playlist(filepath):
    """Read PaidMusicPlayList.txt with retry logic to prevent race conditions"""
    max_retries = 5
    retry_delay = 0.01  # 10ms delay between retries

    for attempt in range(max_retries):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return []
        except (IOError, json.JSONDecodeError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return []
    return []

def write_paid_playlist(filepath, data):
    """Write PaidMusicPlayList.txt with atomic operations and retry logic to prevent race conditions"""
    max_retries = 5
    retry_delay = 0.01  # 10ms delay between retries

    for attempt in range(max_retries):
        try:
            # Write to temp file first, then rename (atomic operation)
            temp_filepath = filepath + '.tmp'
            with open(temp_filepath, 'w') as f:
                json.dump(data, f)
            # Atomic rename on Windows
            os.replace(temp_filepath, filepath)
            return True
        except (IOError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print(f"Error writing PaidMusicPlayList.txt after {max_retries} attempts: {e}")
                # Clean up temp file if it exists
                try:
                    if os.path.exists(temp_filepath):
                        os.remove(temp_filepath)
                except:
                    pass
                return False
    return False

# ============================================================================
# SECTION 4: GUI HELPER FUNCTIONS & SETUP
# ============================================================================

def create_vlc_player_silent(file_path):
    """Create VLC MediaPlayer while suppressing VLC's C-level error/warning messages.

    VLC prints errors at the C library level (not Python level), so we need to redirect
    file descriptors 2 (stderr) and 1 (stdout) at the OS level to suppress the messages.
    """
    # Save original file descriptors
    old_stdout = os.dup(1)  # stdout file descriptor
    old_stderr = os.dup(2)  # stderr file descriptor

    try:
        # Redirect stdout and stderr to /dev/null using file descriptors
        with open(os.devnull, 'w') as devnull:
            os.dup2(devnull.fileno(), 1)  # Redirect stdout
            os.dup2(devnull.fileno(), 2)  # Redirect stderr
            # Create VLC player (this will now produce no output)
            player = vlc.MediaPlayer(file_path)
    finally:
        # Always restore original file descriptors
        os.dup2(old_stdout, 1)
        os.dup2(old_stderr, 2)
        os.close(old_stdout)
        os.close(old_stderr)

    return player

global selection_window_number
global jukebox_selection_window
global last_song_check
global master_songlist_number
last_song_check = ""
global credit_amount
credit_amount = 0
# Popup window tracking
global active_popup_window
global popup_start_time
global popup_duration
active_popup_window = None
popup_start_time = None
popup_duration = None
# Rotating record popup tracking
global rotating_record_rotation_stop_flag
global rotating_record_start_time
global last_keypress_time
global song_start_time
global last_displayed_time
rotating_record_rotation_stop_flag = None
rotating_record_start_time = None
last_keypress_time = time.time()
last_displayed_time = ""
song_start_time = time.time()
UpcomingSongPlayList = []
all_songs_list = []
all_artists_list = []
find_list = []
MusicMasterSongList = []
MusicMasterSongDict = []
master_songlist_number = 0
dir_path = os.path.dirname(os.path.realpath(__file__))
#  Check for files on disk. If they dont exist, create them
#  Create date and time stamp for log file
now = datetime.now()
rounded_now = now + timedelta(seconds=0.5)
rounded_now = rounded_now.replace(microsecond=0)
now = rounded_now
if not os.path.exists('log.txt'):
    with open('log.txt', 'w') as log:
        log.write(str(now) + ' Jukebox GUI Started - New Log File Created,')
else:
    with open('log.txt', 'a') as log:
        log.write('\n' + str(now) + ', Jukebox GUI Restarted,')
if not os.path.exists('the_bands.txt'):
    with open('the_bands.txt', 'w') as TheBandsTextOpen:
        # Band names to have the added to them, in lower case separated by commas in thebands.txt file
        TheBandsText = "beatles,rolling stones,who,doors,byrds,beachboys"
        json.dump(TheBandsText, TheBandsTextOpen)
#  open MusicMasterSongList dictionary
if not os.path.exists('the_exempted_bands.txt'):
    with open('the_exempted_bands.txt', 'w') as TheExemptedBandsTextOpen:
        # Band names be exempted from having the added to them, in proper case separated by line return in the_exempted_bands.txt file
        TheExemptedBandsText = "Place Band Names Here In Proper Case With Each Band Placed On Separate Line With No Quotes"
        json.dump(TheExemptedBandsText, TheExemptedBandsTextOpen)
if not os.path.exists('RecordLabelAssignList.txt'):
    with open('RecordLabelAssignList.txt', 'w') as RecordLabelAssignListOpen:
        # Artist-to-label mappings as list of lists: [["Artist Name", "label_filename.png"], ...]
        RecordLabelAssignList = []
        RecordLabelAssignListOpen.write(str(RecordLabelAssignList))
if not os.path.exists('YearRangeLabelList.txt'):
    with open('YearRangeLabelList.txt', 'w') as YearRangeLabelListOpen:
        # Year-range-to-label mappings as list of lists: [[start_year, end_year, ["label1.png", "label2.png"]], ...]
        YearRangeLabelList = []
        YearRangeLabelListOpen.write(str(YearRangeLabelList))
#  open MusicMasterSongList dictionary - WILL BE POPULATED AFTER jukebox.run() IN MAIN
# This code is deferred until after the jukebox engine generates the MusicMasterSongList.txt file
def _load_master_song_list():
    """Load and process master song list after it has been generated"""
    global all_songs_list, all_artists_list, find_list, MusicMasterSongList, MusicMasterSongDict, master_songlist_number

    with open('MusicMasterSongList.txt', 'r') as MusicMasterSongListOpen:
        MusicMasterSongList = json.load(MusicMasterSongListOpen)
    #  sort MusicMasterSongList dictionary by artist
    MusicMasterSongList = sorted(MusicMasterSongList, key=itemgetter('artist'))
    with open('MusicMasterSongList.txt', 'r') as MusicMasterSongListOpen:
        MusicMasterSongList = json.load(MusicMasterSongListOpen)
    #  sort MusicMasterSongList dictionary by artist
    MusicMasterSongDict = sorted(MusicMasterSongList, key=itemgetter('artist'))
    # MusicMasterSongList*=0
    master_songlist_number = len(MusicMasterSongDict)
    counter = 0
    for counter in range(master_songlist_number):
        all_songs_list.append(list(MusicMasterSongDict[counter].values()))
    MusicMasterSongDict*=0
    artist_songlist_number = len(all_songs_list)
    counter = 0
    for counter in range(artist_songlist_number):
        all_artists_list.append(all_songs_list[counter][3])
    all_songs_list*=0
    # Important Delete duplicates from all_artists_list
    all_artists_list = list(set(all_artists_list)) # https://bit.ly/4cZ7A6R
    # Sort all_artists_list
    all_artists_list = sorted(all_artists_list)
    find_list = all_artists_list

# Queue and thread for handling file I/O operations to prevent event loop freezing
file_io_queue = Queue()

def file_io_worker_thread():
    """Background thread to handle non-blocking file I/O operations"""
    while True:
        try:
            task = file_io_queue.get(timeout=1)
            if task is None:  # Signal to exit thread
                break

            operation = task.get('operation')


            if operation == 'save_song_selection':
                paid_music_file_path = task.get('paid_music_file_path')
                PaidMusicPlayList = task.get('PaidMusicPlayList')
                song_info = task.get('song_info')  # tuple of (artist, title)

                try:
                    # Write updated PaidMusicPlayList to disk
                    # NOTE: This assumes the GUI has properly prepared the list
                    with open(paid_music_file_path, 'w') as f:
                        json.dump(PaidMusicPlayList, f)
                except IOError as e:
                    print(f'Background thread error writing files: {e}')

        except Empty:
            # Queue timeout is normal - just continue waiting for tasks
            continue
        except Exception as e:
            print(f'File I/O worker thread error: {e}')

# Start the background file I/O worker thread
file_io_worker = threading.Thread(target=file_io_worker_thread, daemon=True)
file_io_worker.start()

def file_lookup_thread(song_playing_lookup_window):
    try:
        while True:
            time.sleep(1)
            song_playing_lookup_window.write_event_value('--SONG_PLAYING_LOOKUP--', f'counter = {1}')
    except KeyboardInterrupt:
        pass
#  Thread to look for file changes. Code developed from Python GUIs - "The Official
#  PySimpleGUI Course" https://www.udemy.com/course/pysimplegui/learn/lecture/30070620
#  Background image code modified from https://www.pysimplegui.org/en/latest/Demos/#demo_window_background_imagepy
def title_bar(title, text_color, background_color):
    return [sg.Col([]),
                sg.Col([[sg.T(),sg.Text()]],element_justification='r', key='--BG--')]


# ============================================================================
# SECTION 5: MAIN GUI FUNCTION
# ============================================================================

def main():
    global active_popup_window, popup_start_time, popup_duration, credit_amount
    selection_window_number = 0  # Used to frame initial selection buttons
    selection_entry = ""  # Used for selection entry
    def disable_a_selection_buttons():
        # Call the compacted disable_a_selection_buttons function from external module
        disable_a_buttons_module(jukebox_selection_window, control_button_window)
    def disable_b_selection_buttons():
        # Call the compacted disable_b_selection_buttons function from external module
        disable_b_buttons_module(jukebox_selection_window, control_button_window)
    def disable_c_selection_buttons():
        # Call the compacted disable_c_selection_buttons function from external module
        disable_c_buttons_module(jukebox_selection_window, control_button_window)
    def disable_numbered_selection_buttons():
        #  Identify all buttons to be disabled in the numbered selection window
        control_buttons_to_disable = ['--1--', '--2--', '--3--', '--4--', '--5--', '--6--', '--7--']
        #  Loop through all buttons to disable them in the C selection window
        for control_buttons in control_buttons_to_disable:
            control_button_window[control_buttons].update(disabled=True)
    def selection_buttons_update(selection_window_number):
        #  stop screen progression at end of list
        if selection_window_number + 20 >= len(MusicMasterSongList):
            selection_window_number = len(MusicMasterSongList)-21
            right_arrow_selection_window['--selection_right--'].update(disabled=True)
            #VLC Song Playback Code Begin
            p = create_vlc_player_silent('jukebox_required_audio_files/buzz.mp3')
            p.play()
        else:
            right_arrow_selection_window['--selection_right--'].update(disabled=False)
        #  Stop screen progression at beginning of list
        if selection_window_number + 20 < 0:
            selection_window_number = 0
            left_arrow_selection_window['--selection_left--'].update(disabled=True)
            #VLC Song Playback Code Begin
            p = create_vlc_player_silent('jukebox_required_audio_files/buzz.mp3')
            p.play()
        else:
            left_arrow_selection_window['--selection_left--'].update(disabled=False)
        #  update window buttons        
        font_size_window_updates = create_font_size_window_updates()        
        #  Update and restore selection window buttons to standard font size, then update with song data
        reset_button_fonts(jukebox_selection_window, font_size_window_updates)
        update_selection_button_text(jukebox_selection_window, MusicMasterSongList, selection_window_number)
        adjust_button_fonts_by_length(jukebox_selection_window, font_size_window_updates)
        the_bands_name_check()
    def band_names_exemptions(the_band_to_update, exempted_bands, band_to_check):
        """Check if band needs exemption from 'The' prefix"""
        if the_band_to_update in exempted_bands:
            return band_to_check
        return the_band_to_update

    def the_bands_name_check():
        # Call the compacted the_bands_name_check function from external module
        check_bands_module(jukebox_selection_window, dir_path, band_names_exemptions)

    def enable_numbered_selection_buttons():
        buttons_to_disable = ['--1--', '--2--', '--3--', '--4--', '--5--', '--6--', '--7--']
        for buttons in buttons_to_disable:
            control_button_window[buttons].update(disabled=False)
    def enable_all_buttons():
        # Call the compacted enable_all_buttons function from external module
        enable_all_buttons_module(jukebox_selection_window, control_button_window) 
    def selection_entry_complete(selection_entry_letter, selection_entry_number):
        if selection_entry_number:
            selection_entry = selection_entry_letter + selection_entry_number
        disable_a_selection_buttons()
        disable_b_selection_buttons()
        disable_c_selection_buttons()
        disable_numbered_selection_buttons()
        if selection_entry == "A1":
            jukebox_selection_window['--A1--'].update(disabled=False)
            jukebox_selection_window['--button0_top--'].update(disabled=False)
            jukebox_selection_window['--button0_bottom--'].update(disabled=False)
        if selection_entry == "A2":
            jukebox_selection_window['--A2--'].update(disabled=False)
            jukebox_selection_window['--button1_top--'].update(disabled=False)
            jukebox_selection_window['--button1_bottom--'].update(disabled=False)
        if selection_entry == "A3":
            jukebox_selection_window['--A3--'].update(disabled=False)
            jukebox_selection_window['--button2_top--'].update(disabled=False)
            jukebox_selection_window['--button2_bottom--'].update(disabled=False)
        if selection_entry == "A4":
            jukebox_selection_window['--A4--'].update(disabled=False)
            jukebox_selection_window['--button3_top--'].update(disabled=False)
            jukebox_selection_window['--button3_bottom--'].update(disabled=False)
        if selection_entry == "A5":
            jukebox_selection_window['--A5--'].update(disabled=False)
            jukebox_selection_window['--button4_top--'].update(disabled=False)
            jukebox_selection_window['--button4_bottom--'].update(disabled=False)
        if selection_entry == "A6":
            jukebox_selection_window['--A6--'].update(disabled=False)
            jukebox_selection_window['--button5_top--'].update(disabled=False)
            jukebox_selection_window['--button5_bottom--'].update(disabled=False)
        if selection_entry == "A7":
            jukebox_selection_window['--A7--'].update(disabled=False)
            jukebox_selection_window['--button6_top--'].update(disabled=False)
            jukebox_selection_window['--button6_bottom--'].update(disabled=False)
        if selection_entry == "B1":
            jukebox_selection_window['--B1--'].update(disabled=False)
            jukebox_selection_window['--button7_top--'].update(disabled=False)
            jukebox_selection_window['--button7_bottom--'].update(disabled=False)
        if selection_entry == "B2":
            jukebox_selection_window['--B2--'].update(disabled=False)
            jukebox_selection_window['--button8_top--'].update(disabled=False)
            jukebox_selection_window['--button8_bottom--'].update(disabled=False)
        if selection_entry == "B3":
            jukebox_selection_window['--B3--'].update(disabled=False)
            jukebox_selection_window['--button9_top--'].update(disabled=False)
            jukebox_selection_window['--button9_bottom--'].update(disabled=False)
        if selection_entry == "B4":
            jukebox_selection_window['--B4--'].update(disabled=False)
            jukebox_selection_window['--button10_top--'].update(disabled=False)
            jukebox_selection_window['--button10_bottom--'].update(disabled=False)
        if selection_entry == "B5":
            jukebox_selection_window['--B5--'].update(disabled=False)
            jukebox_selection_window['--button11_top--'].update(disabled=False)
            jukebox_selection_window['--button11_bottom--'].update(disabled=False)
        if selection_entry == "B6":
            jukebox_selection_window['--B6--'].update(disabled=False)
            jukebox_selection_window['--button12_top--'].update(disabled=False)
            jukebox_selection_window['--button12_bottom--'].update(disabled=False)
        if selection_entry == "B7":
            jukebox_selection_window['--B7--'].update(disabled=False)
            jukebox_selection_window['--button13_top--'].update(disabled=False)
            jukebox_selection_window['--button13_bottom--'].update(disabled=False)
        if selection_entry == "C1":
            jukebox_selection_window['--C1--'].update(disabled=False)
            jukebox_selection_window['--button14_top--'].update(disabled=False)
            jukebox_selection_window['--button14_bottom--'].update(disabled=False)
        if selection_entry == "C2":
            jukebox_selection_window['--C2--'].update(disabled=False)
            jukebox_selection_window['--button15_top--'].update(disabled=False)
            jukebox_selection_window['--button15_bottom--'].update(disabled=False)
        if selection_entry == "C3":
            jukebox_selection_window['--C3--'].update(disabled=False)
            jukebox_selection_window['--button16_top--'].update(disabled=False)
            jukebox_selection_window['--button16_bottom--'].update(disabled=False)
        if selection_entry == "C4":
            jukebox_selection_window['--C4--'].update(disabled=False)
            jukebox_selection_window['--button17_top--'].update(disabled=False)
            jukebox_selection_window['--button17_bottom--'].update(disabled=False)
        if selection_entry == "C5":
            jukebox_selection_window['--C5--'].update(disabled=False)
            jukebox_selection_window['--button18_top--'].update(disabled=False)
            jukebox_selection_window['--button18_bottom--'].update(disabled=False)
        if selection_entry == "C6":
            jukebox_selection_window['--C6--'].update(disabled=False)
            jukebox_selection_window['--button19_top--'].update(disabled=False)
            jukebox_selection_window['--button19_bottom--'].update(disabled=False)
        if selection_entry == "C7":
            jukebox_selection_window['--C7--'].update(disabled=False)
            jukebox_selection_window['--button20_top--'].update(disabled=False)
            jukebox_selection_window['--button20_bottom--'].update(disabled=False)
        control_button_window['--select--'].update(disabled=False)
        return selection_entry
    # Call the compacted upcoming selections update function
    def upcoming_selections_update():
        update_upcoming_selections(info_screen_window, UpcomingSongPlayList)
    #  essential code for background image placement and transparent windows placed overtop from https://www.pysimplegui.org/en/latest/Demos/#demo_window_background_imagepy
    background_layout = [[sg.Image(data=background_image)]]
    window_background = sg.Window('Background', background_layout, return_keyboard_events=True, use_default_focus=False, no_titlebar=True, finalize=True, margins=(0, 0),
                                  element_padding=(0, 0), size=(1280, 720), right_click_menu=[[''], ['Exit', ]], transparent_color=sg.theme_background_color())
    song_playing_lookup_layout = [[sg.Text()]]
    info_screen_layout = create_info_screen_layout(master_songlist_number)
    jukebox_selection_screen_layout = create_jukebox_selection_screen_layout(MusicMasterSongList, selection_window_number, dir_path)
    right_arrow_screen_layout = [
        [sg.Button(button_text="", key='--selection_right--', size=(100, 47), image_size=(100, 47),
                   image_filename=dir_path + '/images/lg_arrow_right.png', border_width=0, pad=(0, 0),
                   font='Helvetica 16 bold')]]
    left_arrow_screen_layout = [
        [sg.Button(button_text="", key='--selection_left--', size=(100, 47), image_size=(100, 47),
                   image_filename=dir_path + '/images/lg_arrow_left.png', border_width=0, pad=(0, 0),
                   font='Helvetica 16 bold')]]
    control_button_screen_layout = create_control_button_screen_layout(dir_path)
    title_search_screen_layout = [[sg.Button('Welcome To Title Search', key = "--TITLE_SEARCH--")]]
    artist_search_screen_layout = [[sg.Button('Welcome To Artist Search', key = "--ARTIST_SEARCH--")]]    
    right_arrow_selection_window = sg.Window('Right Arrow', right_arrow_screen_layout, finalize=True,
        keep_on_top=True, transparent_color=sg.theme_background_color(), no_titlebar=True,
        relative_location=(425, -180),return_keyboard_events=True, use_default_focus=False)
    left_arrow_selection_window = sg.Window('Left Arrow', left_arrow_screen_layout, finalize=True,
        keep_on_top=True, transparent_color=sg.theme_background_color(), no_titlebar=True,
        relative_location=(-85, -180),return_keyboard_events=True, use_default_focus=False)
    jukebox_selection_window = sg.Window('Jukebox Selection Screen', jukebox_selection_screen_layout,
                finalize=True, keep_on_top=True, transparent_color=sg.theme_background_color(),
                no_titlebar=True, relative_location=(162,56),return_keyboard_events=True,
                use_default_focus=False)
    info_screen_window = sg.Window('Info Screen', info_screen_layout, finalize=True, keep_on_top=True,
                transparent_color=sg.theme_background_color(), no_titlebar=True,
                element_padding=((0, 0), (0, 0)), relative_location=(-448, 0),return_keyboard_events=True, use_default_focus=False)
    control_button_window = sg.Window('Control Screen', control_button_screen_layout, finalize=True,
                keep_on_top=True, transparent_color=sg.theme_background_color(), no_titlebar=True,return_keyboard_events=True, use_default_focus=False, element_padding=((0, 0), (0, 0)), relative_location=(150, 306))
    song_playing_lookup_window = sg.Window('Song Playing Lookup Thread', song_playing_lookup_layout, no_titlebar=True, finalize=True,return_keyboard_events=True, use_default_focus=False)
    title_search_window = sg.Window('Title Search Window', title_search_screen_layout, finalize=True,
                keep_on_top=True, transparent_color=sg.theme_background_color(),
                no_titlebar=True, relative_location=(415,280),return_keyboard_events=True, use_default_focus=False)
    artist_search_window = sg.Window('Artist Search Window', artist_search_screen_layout, finalize=True,
                keep_on_top=True, transparent_color=sg.theme_background_color(),
                no_titlebar=True, relative_location=(-60,280),return_keyboard_events=True, use_default_focus=False)

    # Bind ESC key to all main windows for exit functionality
    window_background.bind('<Escape>', '--ESC--')
    right_arrow_selection_window.bind('<Escape>', '--ESC--')
    left_arrow_selection_window.bind('<Escape>', '--ESC--')
    jukebox_selection_window.bind('<Escape>', '--ESC--')
    info_screen_window.bind('<Escape>', '--ESC--')
    control_button_window.bind('<Escape>', '--ESC--')
    song_playing_lookup_window.bind('<Escape>', '--ESC--')
    title_search_window.bind('<Escape>', '--ESC--')
    artist_search_window.bind('<Escape>', '--ESC--')

    the_bands_name_check()
    threading.Thread(target=file_lookup_thread, args=(song_playing_lookup_window,), daemon=True).start()
    # Main Jukebox GUI
    while True:
        global last_keypress_time, rotating_record_rotation_stop_flag, rotating_record_start_time
        window, event, values = sg.read_all_windows(timeout=100)  # 100ms timeout for smooth countdown updates
        print(event, values)
        print(event)  # prints buttons key name

        # KEYPRESS HANDLING FOR ROTATING RECORD POPUP
        # Reset idle timer on any keypress (except timeout events)
        if event and event not in [None, sg.TIMEOUT_KEY, '--SONG_PLAYING_LOOKUP--']:
            # Check if it's a keypress event (starts with special prefixes)
            if event.startswith('--') and ('KEY' in event or 'PRESSED' in event or event == '--ESC--'):
                last_keypress_time = time.time()

                # Close rotating record popup on any keypress
                if rotating_record_rotation_stop_flag is not None:
                    try:
                        rotating_record_rotation_stop_flag.set()
                        log_popup_event("popup window rotating closed")
                        # Wait for pygame thread to finish closing
                        time.sleep(0.2)  # Give popup thread time to clean up
                        rotating_record_rotation_stop_flag = None
                        rotating_record_start_time = None
                        # Restore selector windows after keypress close (background, info_screen, and arrow windows stay visible)
                        jukebox_selection_window.UnHide()
                        control_button_window.UnHide()
                        song_playing_lookup_window.UnHide()
                    except Exception as e:
                        pass

        # Check if pygame closed the popup via keypress (rotation_stop_flag was set)
        if rotating_record_rotation_stop_flag is not None and rotating_record_rotation_stop_flag.is_set():
            try:
                log_popup_event("popup window rotating closed")
                rotating_record_rotation_stop_flag = None
                rotating_record_start_time = None
                # Reset idle timer so popup won't reappear for 20 seconds
                last_keypress_time = time.time()
                # Restore selector windows (background, info_screen, and arrow windows stay visible)
                jukebox_selection_window.UnHide()
                control_button_window.UnHide()
                song_playing_lookup_window.UnHide()
            except Exception as e:
                pass

        # Handle ESC key to exit program
        if event == '--ESC--':
            break

        # Handle popup window events
        if active_popup_window is not None:
            # Check if popup has exceeded 3 second duration
            if popup_start_time is not None and time.time() - popup_start_time >= popup_duration:
                try:
                    active_popup_window.close()
                    active_popup_window = None
                    popup_start_time = None
                    popup_duration = None
                except:
                    pass

            # Handle 'x' key press on popup - add one credit
            if event == '--POPUP_X_PRESSED--':
                # Reset idle timer when credit key is pressed in popup (for rotating record popup)
                last_keypress_time = time.time()
                credit_amount += 1
                info_screen_window['--credits--'].Update('CREDITS ' + str(credit_amount))
                print(f"Credit added via popup! Total credits: {credit_amount}")

            # Handle ESC on popup - close it
            if event == '--POPUP_ESC--':
                try:
                    active_popup_window.close()
                    active_popup_window = None
                    popup_start_time = None
                    popup_duration = None
                except:
                    pass

        if (event) == "--selection_right--" or (event) == 'Right:39':
            # Reset idle timer when arrow key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_window_number = selection_window_number + 21
            selection_buttons_update(selection_window_number)
        if (event) == "--selection_left--" or (event) == 'Left:37':
            # Reset idle timer when arrow key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_window_number = selection_window_number - 21
            selection_buttons_update(selection_window_number)
        # Code to initiate search for title or artist
        if (event) == "--TITLE_SEARCH--" or (event) == "T" or (event) == "--ARTIST_SEARCH--" or (event) == "A":
            # Reset idle timer when search keys are pressed (for rotating record popup)
            last_keypress_time = time.time()
            if (event) == "--TITLE_SEARCH--" or (event) == "T":
                search_flag = "title"
            if (event) == "--ARTIST_SEARCH--" or (event) == "A":
                search_flag = "artist"
            # Hide jukebox interface and bring up title search interface
            right_arrow_selection_window.Hide()
            left_arrow_selection_window.Hide()
            jukebox_selection_window.Hide()
            info_screen_window.Hide()
            control_button_window.Hide()
            song_playing_lookup_window.Hide()
            window_background.Hide()
            # Search Windows Button Layout
            search_window_button_layout = create_search_window_button_layout()           
            search_window = sg.Window('', search_window_button_layout, modal=True, no_titlebar = True, size = (1280,720),
                default_button_element_size=(5, 2), auto_size_buttons=False, background_color='black',
                button_color=["firebrick4", "goldenrod1"], font="Helvetica 16 bold", finalize=True)
            # Apply special formatting to A button (highlighted color scheme)
            search_window['--A--'].update(button_color=["firebrick4", "goldenrod1"])
            search_window['--A--'].set_focus()
            search_window.bind('<Right>', '-NEXT-')
            search_window.bind('<Left>', '-PREV-')
            search_window.bind('<S>', '--SELECTED_LETTER--')
            search_window.bind('<C>', '--DELETE--')
            search_window.bind('<Escape>', '--ESC--')
            keys_entered = ''
            search_results = []
            # Set search window to artist if Artist search selected
            if search_flag == "artist":
                search_window["--search_type--"].update("Search For Artist")
            # Keyboard event loop for title search window
            while True:
                event, values = search_window.read()  # read the title_search_window
                print(event, values)
                # Handle ESC key in search window
                if event == '--ESC--':
                    search_window.close()
                    break
                if event == "-NEXT-" or event == "-PREV-" or event == "--CLEAR--" or event == '--EXIT--':
                    if event == "-NEXT-":
                        next_element = search_window.find_element_with_focus().get_next_focus()
                        next_element.set_focus()
                    if event == "-PREV-":
                        prev_element = search_window.find_element_with_focus().get_previous_focus()
                        prev_element.set_focus()
                    if event == "--CLEAR--":  # clear keys if clear button
                        keys_entered = ""
                        search_results = []
                        search_window["--letter_entry--"].Update(keys_entered)
                        search_window["--result_one--"].update("", visible=False, disabled=False)
                        search_window["--result_two--"].update("", visible=False)
                        search_window["--result_three--"].update("", visible=False)
                        search_window["--result_four--"].update("", visible=False)
                        search_window["--result_five--"].update("", visible=False)
                    if event == "--EXIT--":
                        #  Code to restore main jukebox windows
                        right_arrow_selection_window.UnHide()
                        left_arrow_selection_window.UnHide()
                        jukebox_selection_window.UnHide()
                        info_screen_window.UnHide()
                        control_button_window.UnHide()
                        window_background.UnHide()
                        # Clear search results
                        keys_entered = ""
                        # close title search window                              
                        search_window.close()
                        break
                else:
                    # Code specific to title search
                    if search_flag == "title":
                        if event == "--result_one--" or event == "--result_two--" or event == "--result_three--" or event == "--result_four--" or event == "--result_five--":
                            button_text = search_window[event].get_text()
                            song_search = f'{button_text}'
                            # Code to search for song number
                            for i in range(len(MusicMasterSongList)):                            
                                if song_search == str(MusicMasterSongList[i]['artist'] + ' - ' + str(MusicMasterSongList[i]['title'])):
                                    #Song number found
                                    # Song number assigned to song_selected_number variable
                                    song_selected_number = MusicMasterSongList[i]['number']
                                    # Code to set main jukeox selection window screen for selected song
                                    selection_window_number = song_selected_number
                                    selection_buttons_update(selection_window_number)
                                    # Code to update the main jukebox selection window position A1 to the selected song
                                    jukebox_selection_window['--button0_top--'].update(text = MusicMasterSongList[i]['title'])
                                    jukebox_selection_window['--button0_bottom--'].update(text = MusicMasterSongList[i]['artist'])
                                    # Code to set main main jukebox selection window to selected song
                                    disable_a_selection_buttons()
                                    control_button_window['--A--'].update(disabled=True)
                                    jukebox_selection_window['--button0_top--'].update(disabled = False)
                                    jukebox_selection_window['--button0_bottom--'].update(disabled = False)
                                    control_button_window['--select--'].update(disabled = False)
                                    disable_b_selection_buttons()
                                    disable_c_selection_buttons()
                                    # Requied by the main jukebox selection window
                                    song_selected = "A1" 
                                    # Code to restore main jukebox windows
                                    window_background.UnHide()
                                    right_arrow_selection_window.UnHide()
                                    left_arrow_selection_window.UnHide()
                                    jukebox_selection_window.UnHide()
                                    info_screen_window.UnHide()
                                    control_button_window.UnHide()                                
                                    # Clear search results
                                    keys_entered = ""
                                    # close title search window                              
                                    search_window.close()
                                    break
                            #Skip code that updates main Jukebox windows
                            break                    
                    if search_flag == "artist":
                        if event == "--result_one--" or event == "--result_two--" or event == "--result_three--" or event == "--result_four--" or event == "--result_five--":
                            button_text = search_window[event].get_text()                       
                            song_search = f'{button_text}'
                            #  Locate song number
                            counter = 0   
                            for i in MusicMasterSongList:
                                if song_search in MusicMasterSongList[counter]['artist']:
                                    print('artist looking for is: ' + str(song_search))
                                    print('artist match found')
                                    # Song Number Start Found                                
                                    if len(song_search) == len(MusicMasterSongList[counter]['artist']):
                                        print(MusicMasterSongList[counter]['number'])
                                        # Song number found
                                        #print(find_list[counter])
                                        print("Title Selected is number: " + str(MusicMasterSongList[counter]['number']))
                                        print("Artist Selected is: " + str(MusicMasterSongList[counter]['artist']))
                                        # Song number assigned ot song_selected_number variable
                                        song_selected_number = MusicMasterSongList[counter]['number']
                                        # Code to set main jukeox selection window screen for selected song
                                        selection_window_number = song_selected_number
                                        selection_buttons_update(selection_window_number) 
                                        # Code to restore main jukebox windows
                                        right_arrow_selection_window.UnHide()
                                        left_arrow_selection_window.UnHide()
                                        jukebox_selection_window.UnHide()
                                        info_screen_window.UnHide()
                                        control_button_window.UnHide()
                                        window_background.UnHide()
                                        # Clear search results
                                        keys_entered = ""
                                        # close artist search window                              
                                        search_window.close()
                                        break
                                    else:
                                        pass
                                counter += 1                            
                            #Skip code that updates main Jukebox windows                           
                            break  
                    if event == sg.WIN_CLOSED:  # if the X button clicked, just exit
                        break
                    # Code to update the search results based on the keys entered via the keypad                                         
                    if (event) == "--SELECTED_LETTER--":
                        selected_letter_entry = search_window.find_element_with_focus()
                        selected_letter_entry.Click()
                        # key_entry(keys_entered)
                        if event == "A":
                            keys_entered = keys_entered + "A"
                        if event == "B":
                            keys_entered = keys_entered + "B"
                        if event == "C":
                            keys_entered = keys_entered + "C"
                        if event == "D":
                            keys_entered = keys_entered + "D"
                        if event == "E":
                            keys_entered = keys_entered + "E"
                        if event == "F":
                            keys_entered = keys_entered + "F"
                        if event == "G":
                            keys_entered = keys_entered + "G"
                        if event == "H":
                            keys_entered = keys_entered + "H"
                        if event == "I":
                            keys_entered = keys_entered + "I"
                        if event == "J":
                            keys_entered = keys_entered + "J"
                        if event == "K":
                            keys_entered = keys_entered + "K"
                        if event == "L":
                            keys_entered = keys_entered + "L"
                        if event == "M":
                            keys_entered = keys_entered + "M"
                        if event == "N":
                            keys_entered = keys_entered + "N"
                        if event == "O":
                            keys_entered = keys_entered + "O"
                        if event == "P":
                            keys_entered = keys_entered + "P"
                        if event == "Q":
                            keys_entered = keys_entered + "Q"
                        if event == "R":
                            keys_entered = keys_entered + "R"
                        if event == "S":
                            keys_entered = keys_entered + "S"
                        if event == "T":
                            keys_entered = keys_entered + "T"
                        if event == "U":
                            keys_entered = keys_entered + "U"
                        if event == "V":
                            keys_entered = keys_entered + "V"
                        if event == "W":
                            keys_entered = keys_entered + "W"
                        if event == "X":
                            keys_entered = keys_entered + "X"
                        if event == "Y":
                            keys_entered = keys_entered + "Y"
                        if event == "Z":
                            keys_entered = keys_entered + "Z"
                        if event == "1":
                            keys_entered = keys_entered + "1"
                        if event == "2":
                            keys_entered = keys_entered + "2"
                        if event == "3":
                            keys_entered = keys_entered + "3"
                        if event == "4":
                            keys_entered = keys_entered + "4"
                        if event == "5":
                            keys_entered = keys_entered + "5"
                        if event == "6":
                            keys_entered = keys_entered + "6"
                        if event == "7":
                            keys_entered = keys_entered + "7"
                        if event == "8":
                            keys_entered = keys_entered + "8"
                        if event == "9":
                            keys_entered = keys_entered + "9"
                        if event == "0":
                            keys_entered = keys_entered + "0"
                    if event == "--DELETE--":
                        keys_entered = keys_entered[:-1]
                    if event == "--space--":
                        keys_entered += " "
                    elif event == "-":
                        keys_entered += "-"
                    elif event == "'":
                        keys_entered += "'"
                    # Code to update the search results based on the keys entered via a computer keyboard or mouse
                    elif event in "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        print(event, values)
                        if event == "B":
                            keys_entered = keys_entered + "B"
                        if event == "C":
                            keys_entered = keys_entered + "C"
                        if event == "D":
                            keys_entered = keys_entered + "D"
                        if event == "E":
                            keys_entered = keys_entered + "E"
                        if event == "F":
                            keys_entered = keys_entered + "F"
                        if event == "G":
                            keys_entered = keys_entered + "G"
                        if event == "H":
                            keys_entered = keys_entered + "H"
                        if event == "I":
                            keys_entered = keys_entered + "I"
                        if event == "J":
                            keys_entered = keys_entered + "J"
                        if event == "K":
                            keys_entered = keys_entered + "K"
                        if event == "L":
                            keys_entered = keys_entered + "L"
                        if event == "M":
                            keys_entered = keys_entered + "M"
                        if event == "N":
                            keys_entered = keys_entered + "N"
                        if event == "O":
                            keys_entered = keys_entered + "O"
                        if event == "P":
                            keys_entered = keys_entered + "P"
                        if event == "Q":
                            keys_entered = keys_entered + "Q"
                        if event == "R":
                            keys_entered = keys_entered + "R"
                        if event == "S":
                            keys_entered = keys_entered + "S"
                        if event == "T":
                            keys_entered = keys_entered + "T"
                        if event == "U":
                            keys_entered = keys_entered + "U"
                        if event == "V":
                            keys_entered = keys_entered + "V"
                        if event == "W":
                            keys_entered = keys_entered + "W"
                        if event == "X":
                            keys_entered = keys_entered + "X"
                        if event == "Y":
                            keys_entered = keys_entered + "Y"
                        if event == "Z":
                            keys_entered = keys_entered + "Z"
                        if event == "1":
                            keys_entered = keys_entered + "1"
                        if event == "2":
                            keys_entered = keys_entered + "2"
                        if event == "3":
                            keys_entered = keys_entered + "3"
                        if event == "4":
                            keys_entered = keys_entered + "4"
                        if event == "5":
                            keys_entered = keys_entered + "5"
                        if event == "6":
                            keys_entered = keys_entered + "6"
                        if event == "7":
                            keys_entered = keys_entered + "7"
                        if event == "8":
                            keys_entered = keys_entered + "8"
                        if event == "9":
                            keys_entered = keys_entered + "9"
                        if event == "0":
                            keys_entered = keys_entered + "0"
                        print(keys_entered)
                    elif event == "Submit":
                        keys_entered = values["input"]
                        search_window["out"].update(keys_entered)  # output the final stringsd
                    if event == "--A--":
                        keys_entered = keys_entered + "A"
                    print(keys_entered)
                    # Code to bring up search results based on keys entered
                    # Code to search for song title based on keys entered
                    if search_flag == "title":                    
                        for i, item in enumerate(MusicMasterSongList):                   
                            find_list_search = MusicMasterSongList[i]['title']
                            match = find_list_search.lower().find(keys_entered.lower())
                            if match == 0:  # ensures match is from left of string
                                search_results.append(str(MusicMasterSongList[i]['artist']) + " - " + str(MusicMasterSongList[i]['title']))
                    # Code to search for artist based on keys entered
                    if search_flag == "artist":                        
                        find_list = all_artists_list
                        print(keys_entered)
                        for i, item in enumerate(find_list):
                            find_list_search = find_list[i]
                            match = find_list_search.lower().find(keys_entered.lower())
                            if match == 0:  # ensures match is from left of string
                                search_results.append(str(find_list[i]))
                    # Code to update search results on search window
                    if len(search_results) <= 5:
                        search_window["--result_one--"].update(visible=True, disabled=False)
                        search_window["--result_two--"].update(visible=True)
                        search_window["--result_three--"].update(visible=True)
                        search_window["--result_four--"].update(visible=True)
                        search_window["--result_five--"].update(visible=True)
                    if len(search_results) <= 4:
                        search_window["--result_one--"].update(visible=True, disabled=False)
                        search_window["--result_two--"].update(visible=True)
                        search_window["--result_three--"].update(visible=True)
                        search_window["--result_four--"].update(visible=True)
                        search_window["--result_five--"].update(visible=False)
                    if len(search_results) <= 3:
                        search_window["--result_one--"].update(visible=True, disabled=False)
                        search_window["--result_two--"].update(visible=True)
                        search_window["--result_three--"].update(visible=True)
                        search_window["--result_four--"].update(visible=False)
                        search_window["--result_five--"].update(visible=False)
                    if len(search_results) <= 2:
                        search_window["--result_one--"].update(visible=True, disabled=False)
                        search_window["--result_two--"].update(visible=True)
                        search_window["--result_three--"].update(visible=False)
                        search_window["--result_four--"].update(visible=False)
                        search_window["--result_five--"].update(visible=False)
                    if len(search_results) <= 1:
                        search_window["--result_one--"].update(visible=True, disabled=False)
                        search_window["--result_two--"].update(visible=False)
                        search_window["--result_three--"].update(visible=False)
                        search_window["--result_four--"].update(visible=False)
                        search_window["--result_five--"].update(visible=False)
                    if len(search_results) == 0:
                        search_window["--result_one--"].update("Song Title Not On Jukebox", disabled=True)
                        search_window["--result_two--"].update(visible=False)
                        search_window["--result_three--"].update(visible=False)
                        search_window["--result_four--"].update(visible=False)
                        search_window["--result_five--"].update(visible=False)
                    for x in range(len(search_results)):
                        if len(search_results) == 0:
                            search_window["--result_one--"].update("", disabled=False)
                            search_window["--result_two--"].update("")
                            search_window["--result_three--"].update("")
                            search_window["--result_four--"].update("")
                            search_window["--result_five--"].update("")
                        if len(search_results) == 1:
                            search_window["--result_one--"].update(search_results[0], disabled=False)
                            search_window["--result_two--"].update("")
                            search_window["--result_three--"].update("")
                            search_window["--result_four--"].update("")
                            search_window["--result_five--"].update("")
                        if len(search_results) == 2:
                            search_window["--result_one--"].update(search_results[0], disabled=False)
                            search_window["--result_two--"].update(search_results[1])
                            search_window["--result_three--"].update("")
                            search_window["--result_four--"].update("")
                            search_window["--result_five--"].update("")
                        if len(search_results) == 3:
                            search_window["--result_one--"].update(search_results[0], disabled=False)
                            search_window["--result_two--"].update(search_results[1])
                            search_window["--result_three--"].update(search_results[2])
                            search_window["--result_four--"].update("")
                            search_window["--result_five--"].update("")
                        if len(search_results) == 4:
                            search_window["--result_one--"].update(search_results[0], disabled=False)
                            search_window["--result_two--"].update(search_results[1])
                            search_window["--result_three--"].update(search_results[2])
                            search_window["--result_four--"].update(search_results[3])
                            search_window["--result_five--"].update("")
                        if len(search_results) == 5:
                            search_window["--result_one--"].update(search_results[0], disabled=False)
                            search_window["--result_two--"].update(search_results[1])
                            search_window["--result_three--"].update(search_results[2])
                            search_window["--result_four--"].update(search_results[3])
                            search_window["--result_five--"].update(search_results[4])
                        if len(search_results) > 5:
                            search_window["--result_one--"].update(keys_entered, disabled=False)
                            search_window["--result_two--"].update(keys_entered)
                            search_window["--result_three--"].update(keys_entered)
                            search_window["--result_four--"].update(keys_entered)
                            search_window["--result_five--"].update(keys_entered)
                search_results = []
                search_window["--letter_entry--"].Update(keys_entered)
                # End of search window event loop code
            # Reset idle timer after exiting search window
            last_keypress_time = time.time()

            # Close rotating record popup if it's showing
            if rotating_record_rotation_stop_flag is not None:
                try:
                    rotating_record_rotation_stop_flag.set()
                    # Wait for pygame thread to finish closing
                    time.sleep(0.2)  # Give popup thread time to clean up
                    rotating_record_rotation_stop_flag = None
                    rotating_record_start_time = None
                except Exception as e:
                    pass

        #  keyboard entry PySimpleGUI
        if event == "--A--" or (event) == "a":
            # Reset idle timer when category key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_letter = "A"
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            enable_numbered_selection_buttons()
        if event == "--B--" or (event) == "b":
            # Reset idle timer when category key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_letter = "B"
            disable_a_selection_buttons()
            disable_c_selection_buttons()
            enable_numbered_selection_buttons()
        if event == "--C--" or (event) == "c":
            # Reset idle timer when category key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_letter = "C"
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            enable_numbered_selection_buttons()
        #if event == "--X--" or (event) == "x":
        if (event) == "x":
            # Reset idle timer when credit key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            credit_amount += 1
            info_screen_window['--credits--'].Update('CREDITS ' + str(credit_amount))
            # Add credit to log file
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            with open('log.txt', 'a') as log:
                log.write('\n' + str(current_time) + ' Quarter Added,')    
        if event == "--1--" or (event) == "1":
            # Reset idle timer when number key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_number = "1"
            disable_numbered_selection_buttons()
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            jukebox_selection_window['--A1--'].update(disabled=False)
            jukebox_selection_window['--button0_top--'].update(disabled=False)
            jukebox_selection_window['--button0_bottom--'].update(disabled=False)
            jukebox_selection_window['--B1--'].update(disabled=False)
            jukebox_selection_window['--button7_top--'].update(disabled=False)
            jukebox_selection_window['--button7_bottom--'].update(disabled=False)
            jukebox_selection_window['--C1--'].update(disabled=False)
            jukebox_selection_window['--button14_top--'].update(disabled=False)
            jukebox_selection_window['--button14_bottom--'].update(disabled=False)
            control_button_window['--A--'].update(disabled=False)
            control_button_window['--B--'].update(disabled=False)
            control_button_window['--C--'].update(disabled=False)
            if selection_entry_letter:
                selection_entry_complete(selection_entry_letter, selection_entry_number)
        if event == "--2--" or (event) == "2":
            # Reset idle timer when number key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_number = "2"
            disable_numbered_selection_buttons()
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            jukebox_selection_window['--A2--'].update(disabled=False)
            jukebox_selection_window['--button1_top--'].update(disabled=False)
            jukebox_selection_window['--button1_bottom--'].update(disabled=False)
            jukebox_selection_window['--B2--'].update(disabled=False)
            jukebox_selection_window['--button8_top--'].update(disabled=False)
            jukebox_selection_window['--button8_bottom--'].update(disabled=False)
            jukebox_selection_window['--C2--'].update(disabled=False)
            jukebox_selection_window['--button15_top--'].update(disabled=False)
            jukebox_selection_window['--button15_bottom--'].update(disabled=False)
            control_button_window['--A--'].update(disabled=False)
            control_button_window['--B--'].update(disabled=False)
            control_button_window['--C--'].update(disabled=False)
            if selection_entry_letter:
                selection_entry_complete(selection_entry_letter, selection_entry_number)
        if event == "--3--" or (event) == "3":
            # Reset idle timer when number key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_number = "3"
            disable_numbered_selection_buttons()
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            jukebox_selection_window['--A3--'].update(disabled=False)
            jukebox_selection_window['--button2_top--'].update(disabled=False)
            jukebox_selection_window['--button2_bottom--'].update(disabled=False)
            jukebox_selection_window['--B3--'].update(disabled=False)
            jukebox_selection_window['--button9_top--'].update(disabled=False)
            jukebox_selection_window['--button9_bottom--'].update(disabled=False)
            jukebox_selection_window['--C3--'].update(disabled=False)
            jukebox_selection_window['--button16_top--'].update(disabled=False)
            jukebox_selection_window['--button16_bottom--'].update(disabled=False)
            control_button_window['--A--'].update(disabled=False)
            control_button_window['--B--'].update(disabled=False)
            control_button_window['--C--'].update(disabled=False)
            if selection_entry_letter:
                selection_entry_complete(selection_entry_letter, selection_entry_number)
        if event == "--4--" or (event) == "4":
            # Reset idle timer when number key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_number = "4"
            disable_numbered_selection_buttons()
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            jukebox_selection_window['--A4--'].update(disabled=False)
            jukebox_selection_window['--button3_top--'].update(disabled=False)
            jukebox_selection_window['--button3_bottom--'].update(disabled=False)
            jukebox_selection_window['--B4--'].update(disabled=False)
            jukebox_selection_window['--button10_top--'].update(disabled=False)
            jukebox_selection_window['--button10_bottom--'].update(disabled=False)
            jukebox_selection_window['--C4--'].update(disabled=False)
            jukebox_selection_window['--button17_top--'].update(disabled=False)
            jukebox_selection_window['--button17_bottom--'].update(disabled=False)
            control_button_window['--A--'].update(disabled=False)
            control_button_window['--B--'].update(disabled=False)
            control_button_window['--C--'].update(disabled=False)
            if selection_entry_letter:
                selection_entry_complete(selection_entry_letter, selection_entry_number)
        if event == "--5--" or (event) == "5":
            # Reset idle timer when number key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_number = "5"
            disable_numbered_selection_buttons()
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            jukebox_selection_window['--A5--'].update(disabled=False)
            jukebox_selection_window['--button4_top--'].update(disabled=False)
            jukebox_selection_window['--button4_bottom--'].update(disabled=False)
            jukebox_selection_window['--B5--'].update(disabled=False)
            jukebox_selection_window['--button11_top--'].update(disabled=False)
            jukebox_selection_window['--button11_bottom--'].update(disabled=False)
            jukebox_selection_window['--C5--'].update(disabled=False)
            jukebox_selection_window['--button18_top--'].update(disabled=False)
            jukebox_selection_window['--button18_bottom--'].update(disabled=False)
            control_button_window['--A--'].update(disabled=False)
            control_button_window['--B--'].update(disabled=False)
            control_button_window['--C--'].update(disabled=False)
            if selection_entry_letter:
                selection_entry_complete(selection_entry_letter, selection_entry_number)
        if event == "--6--" or (event) == "6":
            # Reset idle timer when number key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_number = "6"
            disable_numbered_selection_buttons()
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            jukebox_selection_window['--A6--'].update(disabled=False)
            jukebox_selection_window['--button5_top--'].update(disabled=False)
            jukebox_selection_window['--button5_bottom--'].update(disabled=False)
            jukebox_selection_window['--B6--'].update(disabled=False)
            jukebox_selection_window['--button12_top--'].update(disabled=False)
            jukebox_selection_window['--button12_bottom--'].update(disabled=False)
            jukebox_selection_window['--C6--'].update(disabled=False)
            jukebox_selection_window['--button19_top--'].update(disabled=False)
            jukebox_selection_window['--button19_bottom--'].update(disabled=False)
            control_button_window['--A--'].update(disabled=False)
            control_button_window['--B--'].update(disabled=False)
            control_button_window['--C--'].update(disabled=False)
            if selection_entry_letter:
                selection_entry_complete(selection_entry_letter, selection_entry_number)
        if event == "--7--" or (event) == "7":
            # Reset idle timer when number key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            selection_entry_number = "7"
            disable_numbered_selection_buttons()
            disable_a_selection_buttons()
            disable_b_selection_buttons()
            disable_c_selection_buttons()
            jukebox_selection_window['--A7--'].update(disabled=False)
            jukebox_selection_window['--button6_top--'].update(disabled=False)
            jukebox_selection_window['--button6_bottom--'].update(disabled=False)
            jukebox_selection_window['--B7--'].update(disabled=False)
            jukebox_selection_window['--button13_top--'].update(disabled=False)
            jukebox_selection_window['--button13_bottom--'].update(disabled=False)
            jukebox_selection_window['--C7--'].update(disabled=False)
            jukebox_selection_window['--button20_top--'].update(disabled=False)
            jukebox_selection_window['--button20_bottom--'].update(disabled=False)
            control_button_window['--A--'].update(disabled=False)
            control_button_window['--B--'].update(disabled=False)
            control_button_window['--C--'].update(disabled=False)
            if selection_entry_letter:
                selection_entry_complete(selection_entry_letter, selection_entry_number)
        if event == "--correct--" or (event) == "C":
            enable_all_buttons()
            selection_entry_letter = ""  # Used for selection entry
            selection_entry_number = ""  # Used for selection entry
            selection_entry = ""  # Used for selection entry
            control_button_window['--select--'].update(disabled=True)
        if event == "--select--" or (event) == 'S':
            # Reset idle timer when select key is pressed (for rotating record popup)
            last_keypress_time = time.time()
            print("Entering Song Selected")
            if credit_amount == 0:
                #VLC Song Playback Code Begin
                p = create_vlc_player_silent('jukebox_required_audio_files/buzz.mp3')
                p.play()
                enable_all_buttons()
                selection_entry_letter = ""  # Used for selection entry
                selection_entry_number = ""  # Used for selection entry
                control_button_window['--select--'].update(disabled=True)
            else:                
                try:
                    if song_selected == "":
                        song_selected = selection_entry_letter + selection_entry_number
                except UnboundLocalError:
                        song_selected = selection_entry_letter + selection_entry_number
                # Clear variables no longer needed
                selection_entry_letter = ""
                selection_entry_number = ""
                if song_selected == "A1":
                    paid_song_selected_title = (jukebox_selection_window['--button0_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button0_bottom--'].get_text())
                if song_selected == "A2":
                    paid_song_selected_title = (jukebox_selection_window['--button1_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button1_bottom--'].get_text())
                if song_selected == "A3":
                    paid_song_selected_title = (jukebox_selection_window['--button2_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button2_bottom--'].get_text())
                if song_selected == "A4":
                    paid_song_selected_title = (jukebox_selection_window['--button3_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button3_bottom--'].get_text())
                if song_selected == "A5":
                    paid_song_selected_title = (jukebox_selection_window['--button4_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button4_bottom--'].get_text())
                if song_selected == "A6":
                    paid_song_selected_title = (jukebox_selection_window['--button5_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button5_bottom--'].get_text())
                if song_selected == "A7":
                    paid_song_selected_title = (jukebox_selection_window['--button6_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button6_bottom--'].get_text())
                if song_selected == "B1":
                    paid_song_selected_title = (jukebox_selection_window['--button7_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button7_bottom--'].get_text())
                if song_selected == "B2":
                    paid_song_selected_title = (jukebox_selection_window['--button8_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button8_bottom--'].get_text())
                if song_selected == "B3":
                    paid_song_selected_title = (jukebox_selection_window['--button9_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button9_bottom--'].get_text())
                if song_selected == "B4":
                    paid_song_selected_title = (jukebox_selection_window['--button10_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button10_bottom--'].get_text())
                if song_selected == "B5":
                    paid_song_selected_title = (jukebox_selection_window['--button11_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button11_bottom--'].get_text())
                if song_selected == "B6":
                    paid_song_selected_title = (jukebox_selection_window['--button12_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button12_bottom--'].get_text())
                if song_selected == "B7":
                    paid_song_selected_title = (jukebox_selection_window['--button13_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button13_bottom--'].get_text())
                if song_selected == "C1":
                    paid_song_selected_title = (jukebox_selection_window['--button14_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button14_bottom--'].get_text())
                if song_selected == "C2":
                    paid_song_selected_title = (jukebox_selection_window['--button15_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button15_bottom--'].get_text())
                if song_selected == "C3":
                    paid_song_selected_title = (jukebox_selection_window['--button16_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button16_bottom--'].get_text())
                if song_selected == "C4":
                    paid_song_selected_title = (jukebox_selection_window['--button17_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button17_bottom--'].get_text())
                if song_selected == "C5":
                    paid_song_selected_title = (jukebox_selection_window['--button18_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button18_bottom--'].get_text())
                if song_selected == "C6":
                    paid_song_selected_title = (jukebox_selection_window['--button19_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button19_bottom--'].get_text())
                if song_selected == "C7":
                    paid_song_selected_title = (jukebox_selection_window['--button20_top--'].get_text())
                    paid_song_selected_artist = (jukebox_selection_window['--button20_bottom--'].get_text())
                song_selected = ""
                control_button_window['--select--'].update(disabled=True)
                disable_numbered_selection_buttons()
                # Check and remove The from artist name
                try:
                    if str(paid_song_selected_artist).startswith('The '):
                        paid_song_selected_artist_no_the = paid_song_selected_artist.replace('The ', '')
                        paid_song_selected_artist = paid_song_selected_artist_no_the

                    # add selection to paid song list
                    counter = 0
                    song_found = False
                    #  find library number of selected song
                    for i in MusicMasterSongList:
                        # search for match of song in MusicMasterSongList
                        # Truncate both sides to 22 characters for consistent matching
                        button_title_truncated = str(paid_song_selected_title)[:22]
                        button_artist_truncated = str(paid_song_selected_artist)[:22]
                        library_title_truncated = str(MusicMasterSongList[counter]['title'][:22])
                        library_artist_truncated = str(MusicMasterSongList[counter]['artist'][:22])

                        if button_title_truncated == library_title_truncated and button_artist_truncated == library_artist_truncated:
                            song_found = True
                            # add song to upcoming list file
                            # UpcomingSongPlayList
                            UpcomingSongPlayList.append(str(MusicMasterSongList[counter]['title'][:22]) + ' - ' + str(MusicMasterSongList[counter]['artist'][:22]))
                            #  add matched song number to variable
                            song_to_add = (MusicMasterSongList[counter]['number'])
                            #  open PaidMusicPlaylist text file and append song number to list
                            paid_music_file_path = os.path.join(dir_path, 'PaidMusicPlayList.txt')

                            # Initialize PaidMusicPlayList with existing data or empty list
                            PaidMusicPlayList = read_paid_playlist(paid_music_file_path)

                            PaidMusicPlayList.append(int(song_to_add))

                            # Check for duplicate song numbers in PaidMusicPlayList
                            # Remove duplicate song numbers from PaidMusicPlayList
                            test_set = set(PaidMusicPlayList)
                            if len(PaidMusicPlayList) != len(test_set):
                                PaidMusicPlayList = list(set(PaidMusicPlayList)) # https://bit.ly/4cZ7A6R
                                UpcomingSongPlayList.pop(-1)
                                print('Duplicate Song Found')
                                #VLC Song Playback Code Begin
                                p = create_vlc_player_silent('jukebox_required_audio_files/buzz.mp3')
                                p.play()
                                enable_all_buttons()
                                selection_entry_letter = ""  # Used for selection entry
                                selection_entry_number = ""  # Used for selection entry
                                selection_entry = ""  # Used for selection entry
                                control_button_window['--select--'].update(disabled=True)
                                enable_all_buttons()
                                break

                            # Write PaidMusicPlayList directly to file immediately with file locking
                            write_paid_playlist(paid_music_file_path, PaidMusicPlayList)
                            #  end search
                            enable_all_buttons()
                            credit_amount -= 1
                            info_screen_window['--credits--'].Update('CREDITS ' + str(credit_amount))
                            # Call 45rpm popup display function
                            active_popup_window, popup_start_time, popup_duration = display_45rpm_popup(MusicMasterSongList, counter, jukebox_selection_window)
                            # Update the upcoming selections display to show newly added paid song
                            update_upcoming_selections(info_screen_window, UpcomingSongPlayList)
                            break
                        counter += 1

                    if not song_found:
                        print(f"ERROR: Song '{paid_song_selected_title}' by '{paid_song_selected_artist}' not found in music library!")
                        enable_all_buttons()
                        control_button_window['--select--'].update(disabled=True)

                except Exception as e:
                    print(f"ERROR during song selection: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    enable_all_buttons()
                    control_button_window['--select--'].update(disabled=True)
        if event is None or event == 'Cancel' or event == 'Exit':
            print(f'closing window = {window.Title}')
            break
        if event == '--SONG_PLAYING_LOOKUP--':
            global last_song_check, song_start_time, last_displayed_time
            with open('CurrentSongPlaying.txt', 'r') as CurrentSongPlayingOpen:
                song_currently_playing = CurrentSongPlayingOpen.read()
                #  search MusicMasterSonglist for location string
                counter=0
                for x in MusicMasterSongList:
                    if MusicMasterSongList[counter]['location'] == song_currently_playing:
                        # Update Jukebox Info Screen
                        song_title = MusicMasterSongList[counter]['title']
                        display_title = song_title[:22]  # Limit to first 22 characters
                        info_screen_window['--song_title--'].Update(display_title)
                        info_screen_window['--song_artist--'].Update(
                            MusicMasterSongList[counter]['artist'][:29])
                        info_screen_window['--mini_song_title--'].Update(
                            '  Title: ' + MusicMasterSongList[counter]['title'])
                        info_screen_window['--mini_song_artist--'].Update(
                            '  Artist: ' + MusicMasterSongList[counter]['artist'])

                        # UPDATE COUNTDOWN from VLC
                        try:
                            current_time_ms = jukebox.vlc_media_player.get_time()
                            media = jukebox.vlc_media_player.get_media()
                            duration_ms = media.get_duration() if media else -1

                            if current_time_ms > 0 and duration_ms > 0:
                                elapsed_seconds = current_time_ms / 1000.0
                                total_seconds = duration_ms / 1000.0
                                time_remaining_seconds = total_seconds - elapsed_seconds
                                formatted_time = format_time_remaining(time_remaining_seconds)
                                display_string = '  Year: ' + MusicMasterSongList[counter]['year'] + '   Remaining: ' + formatted_time
                            else:
                                display_string = '  Year: ' + MusicMasterSongList[counter]['year'] + '   Remaining: ' + MusicMasterSongList[counter]['duration']

                            # Only update if changed
                            if display_string != last_displayed_time:
                                info_screen_window['--year--'].Update(display_string)
                                last_displayed_time = display_string
                        except:
                            info_screen_window['--year--'].Update(
                                '  Year: ' + MusicMasterSongList[counter]['year'] + '   Remaining: ' +
                                MusicMasterSongList[counter]['duration'])

                        info_screen_window['--album--'].Update(
                            '  Album: ' + MusicMasterSongList[counter]['album'])
                        #  Check to see if curent song playing has changed
                        with open('CurrentSongPlaying.txt', 'r') as CurrentSongPlayingOpen:
                            song_currently_playing = CurrentSongPlayingOpen.read()
                            # Set up first check
                            if last_song_check == "":
                                last_song_check = song_currently_playing
                            #  Check to see if current song has changed
                            if last_song_check != song_currently_playing:
                                last_song_check = song_currently_playing
                                # Clear the shared label cache when song changes to prevent memory buildup
                                clear_song_label_cache()
                                # FIX: Only remove from UpcomingSongPlayList if the currently playing song matches the first upcoming song
                                # This prevents paid songs from being removed when a random song plays instead
                                if UpcomingSongPlayList:  # Only if there are upcoming songs
                                    # Build the current song string in the same format as UpcomingSongPlayList entries
                                    current_song_str = str(MusicMasterSongList[counter]['title'][:22]) + ' - ' + str(MusicMasterSongList[counter]['artist'][:22])
                                    upcoming_song_str = UpcomingSongPlayList[0]

                                    # Only remove from upcoming list if the currently playing song matches the first upcoming song
                                    if current_song_str == upcoming_song_str:
                                        try:
                                            UpcomingSongPlayList.pop(0)
                                        except IndexError: # Executed if no first entry in list
                                            pass
                                        # Update the display after removing the song
                                        update_upcoming_selections(info_screen_window, UpcomingSongPlayList)
                                # Always update the now-playing popup
                                # active_popup_window, popup_start_time, popup_duration = display_45rpm_now_playing_popup(MusicMasterSongList, counter, jukebox_selection_window, upcoming_selections_update)
                                # Reset song start time when song changes
                                song_start_time = time.time()

                        # ROTATING RECORD POPUP LOGIC
                        # Get current playback time and duration from VLC
                        try:
                            current_time_ms = jukebox.vlc_media_player.get_time()
                            media = jukebox.vlc_media_player.get_media()
                            duration_ms = media.get_duration() if media else -1

                            if current_time_ms > 0 and duration_ms > 0:
                                # Convert to seconds
                                elapsed_seconds = current_time_ms / 1000.0
                                total_seconds = duration_ms / 1000.0
                                time_remaining_seconds = total_seconds - elapsed_seconds
                                time_since_keypress = time.time() - last_keypress_time

                                # Conditions to SHOW rotating record popup
                                should_show = (
                                    elapsed_seconds >= 20 and  # Song playing >= 20 seconds
                                    time_since_keypress >= 20 and  # Idle >= 20 seconds
                                    time_remaining_seconds >= 5 and  # Song has >= 5 seconds remaining
                                    rotating_record_rotation_stop_flag is None  # Popup not already shown
                                )

                                # Conditions to CLOSE rotating record popup
                                should_close = (
                                    rotating_record_rotation_stop_flag is not None and
                                    (time_remaining_seconds < 5)  # Close when 5 seconds remaining
                                )

                                # Show popup if conditions met
                                if should_show:
                                    # Hide selector windows (keep background, info_screen, and arrow windows visible)
                                    jukebox_selection_window.Hide()
                                    control_button_window.Hide()
                                    song_playing_lookup_window.Hide()
                                    rotating_record_rotation_stop_flag, rotating_record_start_time = display_rotating_record_popup(MusicMasterSongList, counter, total_seconds, elapsed_seconds)

                                # Close popup if song ending
                                if should_close:
                                    rotating_record_rotation_stop_flag.set()
                                    log_popup_event("popup window rotating closed")
                                    # Wait for pygame thread to finish closing
                                    time.sleep(0.2)  # Give popup thread time to clean up
                                    rotating_record_rotation_stop_flag = None
                                    rotating_record_start_time = None
                                    # Restore selector windows (background, info_screen, and arrow windows stay visible)
                                    jukebox_selection_window.UnHide()
                                    control_button_window.UnHide()
                                    song_playing_lookup_window.UnHide()
                        except Exception as e:
                            pass

                        if UpcomingSongPlayList != []:
                            # update upcoming selections on jukebox screens
                            update_upcoming_selections(info_screen_window, UpcomingSongPlayList)
                        break
                    counter +=1
    right_arrow_selection_window.close()
    left_arrow_selection_window.close()
    info_screen_window.close()


# ============================================================================
# SECTION 6: ENGINE INITIALIZATION & THREADING SETUP
# ============================================================================

def run_engine_thread(jukebox_instance):
    """Run the jukebox engine in a daemon thread

    This method runs continuously in the background, checking the paid playlist
    file for new song requests and alternating between paid and random songs.

    Args:
        jukebox_instance (JukeboxEngine): The initialized engine instance
    """
    try:
        jukebox_instance._print_header("Engine Thread Started")
        jukebox_instance.jukebox_engine()
    except Exception as e:
        jukebox_instance._log_error(f"Engine thread error: {e}")


# ============================================================================
# SECTION 7: MAIN EXECUTION BLOCK
# ============================================================================

if __name__ == '__main__':
    try:
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"{'CONVERGENCE JUKEBOX - FULL INTEGRATED VERSION 0.51'.center(60)}")
        print(f"{'='*60}{Colors.ENDC}\n")

        # Step 1: Initialize the Jukebox Engine
        print("[1/3] Initializing Jukebox Engine...")
        jukebox = JukeboxEngine()

        # Step 2: Run engine initialization (database, config, playlists)
        print("[2/3] Running engine startup sequence...")
        jukebox.run()

        # Step 2.5: Load master song list after it has been generated
        print("[2/5] Loading master song list...")
        _load_master_song_list()

        # Step 3: Launch engine in daemon thread for background playback
        print("[3/3] Launching engine thread and GUI...\n")
        engine_thread = threading.Thread(
            target=run_engine_thread,
            args=(jukebox,),
            name="JukeboxEngine-Thread",
            daemon=True
        )
        engine_thread.start()

        # Step 4: Start GUI in main thread (blocks until GUI exits)
        print(f"{Colors.GREEN}Engine running in background thread{Colors.ENDC}")
        print(f"{Colors.GREEN}Starting user interface...{Colors.ENDC}\n")

        main()

        # Step 5: Cleanup when GUI closes
        print(f"\n{Colors.CYAN}Jukebox GUI closed. Shutting down...{Colors.ENDC}")
        sys.exit(0)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Keyboard interrupt received. Shutting down...{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[CRITICAL ERROR] Failed to start Convergence Jukebox: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
b