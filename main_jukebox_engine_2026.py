import vlc
from datetime import datetime, timedelta
from tinytag import TinyTag
import psutil
import glob
import json
import os
import random
import time
import gc
import sys
from typing import List, Dict, Any, Optional, Tuple


# ANSI Color codes for cross-platform colored output
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
    STATISTICS_FILE: str = 'song_statistics.json'
    GC_THRESHOLD: int = 100

    def __init__(self) -> None:
        """Initialize Jukebox Engine with all required variables and file setup"""
        # Initialize data structures
        self.music_id3_metadata_list: List[tuple] = []
        self.music_master_song_list: List[Dict[str, str]] = []
        self.random_music_playlist: List[int] = []
        self.paid_music_playlist: List[int] = []
        self.final_genre_list: List[str] = []
        self.song_statistics: Dict[str, Dict[str, Any]] = {}  # Improvement #3: Statistics tracking

        # Memory optimization counters
        self.gc_counter: int = 0

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
        self.statistics_file: str = os.path.join(self.dir_path, self.STATISTICS_FILE)

        # Initialize log file and required data files
        self._setup_files()
        self._load_statistics()  # Improvement #3: Load song statistics
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
    # IMPROVEMENT #3: SONG STATISTICS METHODS
    # ============================================================================

    def _load_statistics(self) -> None:
        """Load song statistics from file."""
        success, data = self._read_json_file(self.statistics_file)
        if success and isinstance(data, dict):
            self.song_statistics = data
        else:
            self.song_statistics = {}
            self._print_success("Created new statistics file")

    def _save_statistics(self) -> bool:
        """Save song statistics to file.

        Returns:
            bool: True if successful, False otherwise
        """
        return self._write_json_file(self.statistics_file, self.song_statistics)

    def _record_song_play(self, song_index: int, play_type: str) -> None:
        """Record a song play in statistics.

        Args:
            song_index (int): Index of played song
            play_type (str): Type of play ('random' or 'paid')
        """
        if not self._validate_playlist_entry(song_index):
            return

        song_index_str = str(song_index)

        # Initialize song stats if not exists
        if song_index_str not in self.song_statistics:
            song = self.music_master_song_list[song_index]
            self.song_statistics[song_index_str] = {
                'title': song.get('title', 'Unknown'),
                'artist': song.get('artist', 'Unknown'),
                'play_count': 0,
                'last_played': None,
                'play_history': []
            }

        # Update statistics
        self.song_statistics[song_index_str]['play_count'] += 1
        self.song_statistics[song_index_str]['last_played'] = str(self._get_rounded_timestamp())
        self.song_statistics[song_index_str]['play_history'].append({
            'timestamp': str(self._get_rounded_timestamp()),
            'type': play_type
        })

        # Keep history to last 100 plays
        if len(self.song_statistics[song_index_str]['play_history']) > 100:
            self.song_statistics[song_index_str]['play_history'] = \
                self.song_statistics[song_index_str]['play_history'][-100:]

    def _get_top_songs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top played songs.

        Args:
            limit (int): Number of top songs to return

        Returns:
            List[Dict[str, Any]]: List of top songs with stats
        """
        sorted_stats = sorted(
            self.song_statistics.items(),
            key=lambda x: x[1].get('play_count', 0),
            reverse=True
        )

        top_songs = []
        for song_index_str, stats in sorted_stats[:limit]:
            top_songs.append({
                'index': int(song_index_str),
                'title': stats.get('title', 'Unknown'),
                'artist': stats.get('artist', 'Unknown'),
                'play_count': stats.get('play_count', 0),
                'last_played': stats.get('last_played', 'Never')
            })

        return top_songs

    def _display_statistics(self) -> None:
        """Display song statistics in console."""
        if not self.song_statistics:
            self._print_warning("No song statistics available yet")
            return

        self._print_header("Song Statistics")

        total_plays = sum(s.get('play_count', 0) for s in self.song_statistics.values())
        self._print_success(f"Total plays: {total_plays}")
        self._print_success(f"Unique songs played: {len(self.song_statistics)}")

        print("\nTop 10 Most Played Songs:")
        print("-" * 80)

        top_songs = self._get_top_songs(10)
        for i, song in enumerate(top_songs, 1):
            print(f"{i:2}. {song['title']:<40} | {song['artist']:<20} | Plays: {song['play_count']:>3}")

        print("-" * 80)

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
            print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
        else:
            print(f"✓ {message}")

    def _print_warning(self, message: str) -> None:
        """Print a warning message in yellow

        Args:
            message (str): The warning message
        """
        if self.config['console']['colors_enabled']:
            print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")
        else:
            print(f"⚠ {message}")

    def _print_error_msg(self, message: str) -> None:
        """Print an error message in red

        Args:
            message (str): The error message
        """
        if self.config['console']['colors_enabled']:
            print(f"{Colors.RED}✗ {message}{Colors.ENDC}")
        else:
            print(f"✗ {message}")

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

            for file_path in mp3_music_files:
                try:
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

            if not self.music_id3_metadata_list:
                self._log_error("No valid metadata was extracted from MP3 files")
                return False

            self._print_success(f"Extracted metadata from {counter} songs")
            return True
        except Exception as e:
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
                    try:
                        with open(self.paid_music_playlist_file, 'r') as paid_list_file:
                            self.paid_music_playlist = json.load(paid_list_file)
                    except (IOError, json.JSONDecodeError) as e:
                        self._log_error(f"Failed to load PaidMusicPlayList.txt: {e}")
                        break

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

                        # Delete song just played from paid playlist
                        try:
                            del self.paid_music_playlist[0]
                            with open(self.paid_music_playlist_file, 'w') as paid_list_file:
                                json.dump(self.paid_music_playlist, paid_list_file)
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
                            self.jukebox_engine()
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
                self.jukebox_engine()
            else:
                self._log_error("Failed to initialize jukebox engine")
        except Exception as e:
            self._log_error(f"Critical error in run method: {e}")


# Main execution
if __name__ == "__main__":
    try:
        jukebox: JukeboxEngine = JukeboxEngine()
        jukebox.run()
    except Exception as e:
        print(f"CRITICAL: Failed to start Jukebox Engine: {e}")
        sys.exit(1)
