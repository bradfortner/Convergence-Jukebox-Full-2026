# Convergence Jukebox Full 2026

An integrated jukebox application combining a VLC-based audio engine with a FreeSimpleGUI interface. The application runs the engine as a daemon thread while maintaining a responsive GUI on the main thread. Features comprehensive song management with a music collection, multiple playlist types (paid and random), advanced search capabilities, and interactive 45 RPM record visualization.

**Evolution**: This project evolved from the original Convergence Jukebox created in 2015. Version 0.82.97 represents the latest stable implementation with a modernized interface featuring dynamically generated 45 RPM record images and smooth rotation animations. Recent improvements include fixing a race condition bug in the paid music playlist system, optimizing popup module text rendering, and enhancing the info screen display with dynamic title character limiting and layout refinements.

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
- `search_module.py` - Search functionality for title and artist search
- `popup_45rpm_song_selection_code_module.py` - 45 RPM popup for song selection
- `popup_rotating_record_code_module.py` - Rotating record animation and display
- `font_size_window_updates_module.py` - Dynamic font sizing for buttons
- `disable_a_selection_buttons_module.py` - Button management (A selections)
- `disable_b_selection_buttons_module.py` - Button management (B selections)
- `disable_c_selection_buttons_module.py` - Button management (C selections)
- `enable_all_buttons_module.py` - Button enabling functionality
- `the_bands_name_check_module.py` - Band name formatting and exemptions
- `background_image_module.py` - Base64-encoded PNG background image data (imported by main application)

## Usage

```bash
python "0.83.42 - Convergence-Jukebox-Full-2026.py"
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
├── 0.83.42 - Convergence-Jukebox-Full-2026.py # Main integrated application (CURRENT)
├── depreciated_code/                          # Previous versions (0.81-0.83.41 archived versions)
├── .claude/                                   # Claude Code configuration
│   └── claude.md                              # Debugging notes and fixes
├── jukebox_config.json                        # Configuration file
├── song_statistics.json                       # Song statistics tracking
├── GenreFlagsList.txt                         # Genre flags data
├── MusicMasterSongList.txt                    # Song database
├── MusicMasterSongListCheck.txt               # Song list verification
├── PaidMusicPlayList.txt                      # Paid playlist storage
├── CurrentSongPlaying.txt                     # Current playing song info
├── log.txt                                    # Application log file
├── music/                                     # Music directory (MP3 files)
├── images/                                    # Image assets (UI graphics)
├── record_labels/                             # 45 RPM record label templates
├── fonts/                                     # Font files for record labels
├── jukebox_required_audio_files/              # UI sounds (buzz.mp3, success.mp3)
└── Module files (in project root)
    ├── control_button_screen_layout_module.py
    ├── jukebox_selection_screen_layout_module.py
    ├── info_screen_layout_module.py
    ├── search_window_button_layout_module.py
    ├── search_module.py
    ├── popup_45rpm_song_selection_code_module.py
    ├── popup_rotating_record_code_module.py
    ├── popup_45rpm_now_playing_code_module.py
    ├── font_size_window_updates_module.py
    ├── disable_a_selection_buttons_module.py
    ├── disable_b_selection_buttons_module.py
    ├── disable_c_selection_buttons_module.py
    ├── enable_all_buttons_module.py
    ├── the_bands_name_check_module.py
    ├── metadata_progress_bar_module.py
    ├── upcoming_selections_update_module.py
    ├── background_image_module.py
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

**0.76** - Convergence Jukebox Full 2026
- Complete modernization and unified integration of engine and GUI
- New retro interface with 45 RPM record image generation and smooth rotation animation
- Stable base with enhanced features
- Input validation for data integrity
- Song statistics tracking and reporting

**0.80 - 0.81** - Debugging and Enhancement
- Added logging and diagnostic features
- Improved module organization

**0.82.0 - 0.82.7** - Paid Song Bug Investigation and Fixes
- Identified race condition between GUI and Engine accessing PaidMusicPlayList.txt
- Attempted solutions with background thread removal, file locking, and atomic writes
- All debug versions moved to depreciated_code folder

**0.82.8 - Convergence Jukebox Full 2026**
- Fixed paid music playlist bug by re-reading file after playing
- Resolves issue where second and subsequent paid songs were lost
- Cleaned up debug logging from popup modules and main code
- Stable, fully functional implementation with proper playlist synchronization

**0.82.90 - 0.82.97 - Popup and Info Screen Enhancements**
- **0.82.90**: Updated popup modules with separate artist text width (250px vs 300px song title)
- **0.82.91**: Implemented dynamic song title alignment using dual elements (centered/left)
- **0.82.92**: Fixed blank line between title and artist by optimizing element layout
- **0.82.93**: Reverted to separate rows to resolve window width overflow issues
- **0.82.94**: Implemented manual padding approach for dynamic alignment
- **0.82.95**: Simplified to left-justified display for all title/artist elements
- **0.82.96**: Reverted back to center-justified display for better visual appearance
- **0.82.97**: Added 22-character limit to song title display to prevent layout overflow
- Archived versions 0.81-0.82.8 to depreciated_code folder for cleaner project structure

**0.83.12 - Code Organization and Module Refactoring**
- **0.83.12**: Extracted background image data to separate module file
  - Created `background_image_module.py` to store Base64-encoded PNG image separately
  - Updated main application to import background_image from the new module
  - Improves code organization and maintainability by separating large image data from main file
  - Reduces main application file size while maintaining full functionality

**0.83.42 - Search Functionality Refactoring (CURRENT)**
- **0.83.42**: Refactored search functionality into separate module
  - Created `search_module.py` with extracted search logic (~530 lines)
  - Moved title and artist search code from main file to dedicated module
  - Implemented clean interface with `run_search()` function accepting window and callback parameters
  - Reduced main application file by ~485 lines while maintaining full search functionality
  - Both title search (T key) and artist search (A key) now use modular approach
  - Improves code organization and maintainability for search features

## Paid Music Playlist System

The jukebox features a paid music playlist system that prioritizes paid song selections over random playback:

- **Selection**: Users can select paid songs by inserting credits (quarters)
- **Priority**: Paid songs play immediately after the current song finishes, before returning to random playlist
- **Queue Management**: Multiple paid songs can be selected and will play in the order they were selected
- **File-based Storage**: Song selections are stored in `PaidMusicPlayList.txt` and synchronized between GUI and Engine

### Bug Fix (v0.82.8)
A race condition bug was identified and fixed where the second and subsequent paid songs would be lost during playback:
- **Root Cause**: The Engine's in-memory copy of the paid playlist became out of sync with the file when songs were selected during playback
- **Solution**: The Engine now re-reads the playlist file from disk after playing each song, ensuring all newly added selections are captured
- This simple fix ensures all paid song selections are played in the correct order without loss of data

## License

[Add your license here]
