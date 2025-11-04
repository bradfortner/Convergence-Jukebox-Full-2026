# Convergence Jukebox Full 2026

An integrated jukebox application combining a VLC-based audio engine with a FreeSimpleGUI interface. The application runs the engine as a daemon thread while maintaining a responsive GUI on the main thread. Features comprehensive song management with 79-track collection, multiple playlist types, genre filtering, song statistics tracking, advanced search capabilities, and interactive 45 RPM record visualization.

**Evolution**: This project evolved from the original Convergence Jukebox created in 2015. Version 0.76 represents a complete modernization with a new interface featuring dynamically generated 45 RPM record images and smooth rotation animations that bring a nostalgic retro aesthetic to digital music playback.

## Features

- **Cross-platform** - Runs on Windows and Linux with full compatibility
- **Dual-threaded architecture** - Engine runs as daemon thread, GUI runs on main thread for responsiveness
- **VLC audio playback** - Professional-grade audio playback with VLC MediaPlayer
- **Responsive GUI** - FreeSimpleGUI with transparent background and overlay windows
- **79-track collection** - Curated music library with ID3 metadata support
- **Playlist management** - Random playlist and paid music playlist support
- **Song search** - Search by title or artist with keyboard entry
- **Genre filtering** - Multiple genre flags per song (up to 4) for advanced filtering
- **Song statistics** - Tracks play count, last played time, and other metrics
- **45 RPM record visualization** - Dynamically generated 45 RPM record image with smooth rotation animation, displaying song metadata and playback progress (new in modernized 2026 version)
- **Input validation** - Data integrity checks for all inputs
- **Console logging** - Colored console output with debug information
- **File-based IPC** - Communication between engine and GUI via text files
- **Configuration management** - JSON-based configuration system with sensible defaults

## Installation

### Platform Compatibility

This application is **fully compatible with Windows and Linux**. The codebase uses cross-platform libraries and path handling (via `os.path.join`) to ensure seamless operation across both operating systems.

### System Requirements
- **Python 3.7+**
- **VLC (VideoLAN)** - https://www.videolan.org/vlc/ (required for audio playback)

### Python Package Dependencies

Install the required packages using pip:

```bash
pip install PySimpleGUI python-vlc tinytag Pillow pygame psutil
```

**External (Third-party) Libraries:**
- **FreeSimpleGUI** - GUI framework for creating the application windows and interface
- **python-vlc** - Python bindings for VLC media player (handles audio playback)
- **tinytag** - Reads and parses ID3 metadata from MP3 files
- **Pillow (PIL)** - Image processing library for generating 45 RPM record images and rotations
- **pygame** - Game development library used for display and animation of rotating record visualization
- **psutil** - System and process utilities for monitoring

**Standard Library (Built-in):**
- `os` - Cross-platform file and path operations
- `sys` - System-specific parameters and functions
- `json` - Configuration file parsing and statistics storage
- `threading` - Background engine thread management
- `queue` - Thread-safe communication queue
- `datetime` - Timestamp and logging support
- `time` - Timing and delays
- `random` - Random playlist generation
- `glob` - File pattern matching
- `gc` - Garbage collection optimization
- `typing` - Type hints for code clarity
- `operator`, `calendar`, `token`, `textwrap` - Utility functions

### Project-Specific Modules

The application requires the following project module files:
- `control_button_screen_layout_module.py` - Control button UI layout
- `jukebox_selection_screen_layout_module.py` - Song selection screen layout
- `info_screen_layout_module.py` - Information display screen layout
- `search_window_button_layout_module.py` - Search window interface
- `popup_45rpm_song_selection_code_module.py` - 45 RPM popup for song selection
- `popup_rotating_record_code_module.py` - Rotating record animation and display
- `font_size_window_updates_module.py` - Dynamic font sizing for buttons
- `disable_a_selection_buttons_module.py` - Button management (A selections)
- `disable_b_selection_buttons_module.py` - Button management (B selections)
- `disable_c_selection_buttons_module.py` - Button management (C selections)
- `enable_all_buttons_module.py` - Button enabling functionality
- `the_bands_name_check_module.py` - Band name formatting and exemptions

## Usage

```bash
python "0.76 - Convergence-Jukebox-Full-2026.py"
```

The application will:
1. Initialize the jukebox engine with input validation
2. Load configuration from `jukebox_config.json`
3. Load the 79-track music collection with ID3 metadata
4. Load genre flags and song statistics
5. Initialize VLC player and logging
6. Launch the GUI windows (selection screen, control buttons, info screen)
7. Start the engine in a background daemon thread
8. Display the interactive jukebox selection interface with 45 RPM record popup

## Project Structure

```
Convergence-Jukebox-Full-2026/
├── 0.76 - Convergence-Jukebox-Full-2026.py    # Main integrated application
├── jukebox_config.json                        # Configuration file
├── song_statistics.json                       # Song statistics tracking
├── GenreFlagsList.txt                         # Genre flags data
├── MusicMasterSongList.txt                    # Song database
├── MusicMasterSongListCheck.txt               # Song list verification
├── PaidMusicPlayList.txt                      # Paid playlist storage
├── CurrentSongPlaying.txt                     # Current playing song info
├── log.txt                                    # Application log file
├── music/                                     # Music directory (79 MP3 files)
├── images/                                    # Image assets (UI graphics)
├── jukebox_required_audio_files/              # UI sounds (buzz.mp3)
└── Module files/                              # External GUI modules
    ├── control_button_screen_layout_module.py
    ├── jukebox_selection_screen_layout_module.py
    ├── info_screen_layout_module.py
    ├── search_window_button_layout_module.py
    ├── popup_45rpm_song_selection_code_module.py
    ├── popup_rotating_record_code_module.py
    ├── font_size_window_updates_module.py
    ├── disable_a/b/c_selection_buttons_module.py
    ├── enable_all_buttons_module.py
    └── (and other UI/utility modules)
```

## Architecture

### Engine (Daemon Thread)
The `JukeboxEngine` class (Version 0.9 STABLE + FEATURES HYBRID) manages:
- **VLC playback** - Professional audio control with MediaPlayer instance
- **Playlist management** - Random playlist and paid music playlist handling
- **Song metadata** - Loads and manages 79 songs with ID3 tags (artist, title, album, year, duration, genre)
- **Genre filtering** - Multi-flag genre system (up to 4 genres per song)
- **Statistics tracking** - Records play count, last played time, and other metrics
- **Input validation** - Data integrity checks for all operations
- **File-based IPC** - Reads playlist files and updates current song status
- **Memory optimization** - Garbage collection triggers and efficient data structures

Key design: NO THREADING within the engine itself to avoid memory leaks introduced in earlier versions.

### GUI (Main Thread)
FreeSimpleGUI windows managed by the `main()` function:
- **Selection screen** - Grid-based interface for browsing and selecting songs (20 songs per page)
- **Control buttons** - Play, pause, stop, forward, and playlist controls
- **Info screen** - Displays current song, upcoming songs queue, and playback info
- **Search window** - Keyboard-based search by title or artist
- **45 RPM popup** - Rotating record visualization showing playback progress
- **Button management** - Contextual button enabling/disabling (A/B/C selections + numbered buttons)

### IPC Communication (File-based)
- **PaidMusicPlayList.txt** - Paid playlist requests from GUI to engine
- **CurrentSongPlaying.txt** - Engine updates with current song metadata
- **MusicMasterSongListCheck.txt** - Song list verification and caching

## Configuration

Edit `jukebox_config.json` to customize:
- **Logging** - Enable/disable logging and set log level (INFO, DEBUG, etc.)
- **Logging format** - Customize log message format with timestamp, level, and message
- **File paths** - Set custom paths for music directory, config files, and data files
- **Console output** - Toggle colored output, system info display, and verbose mode

## Setup Notes

For full functionality, you will need:
1. A `music/` directory with 79 MP3 files (requires ID3 metadata tags)
2. An `images/` directory with required UI graphics
3. A `jukebox_required_audio_files/` directory with `buzz.mp3` sound effect
4. VLC installed on your system
5. All external module files in the project directory
6. Valid `jukebox_config.json` configuration file

## Version History

**2015 (Original)** - Convergence Jukebox
- Initial jukebox application with basic music playback

**0.76 - Convergence Jukebox Full 2026 (Current)**
- Complete modernization and unified integration of engine and GUI
- New retro interface with 45 RPM record image generation and smooth rotation animation
- Stable base (Version 0.8) with enhanced features
- Input validation for data integrity
- Refactored I/O methods for testability
- Song statistics tracking and reporting
- No internal threading (avoids memory leaks from earlier versions)
- Enhanced from 11 years of development and refinement

## License

[Add your license here]
