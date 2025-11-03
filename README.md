# Convergence Jukebox 2026

A threaded music player that combines a VLC-based audio engine with a FreeSimpleGUI interface, running the engine as a non-blocking daemon thread while maintaining a responsive GUI for song selection, search, and playlist management. Features a 79-track collection with support for random and paid playlists, genre filtering, and file-based inter-process communication between components.

## Features

- **Dual-threaded architecture** - Engine runs as daemon thread, GUI runs on main thread
- **VLC audio playback** - Professional-grade audio playback with VLC MediaPlayer
- **Responsive GUI** - FreeSimpleGUI with transparent background and overlay windows
- **79-track collection** - Curated music library with metadata support
- **Playlist management** - Random playlist and paid music playlist support
- **Song search** - Search by title or artist
- **Genre filtering** - Filter songs by genre
- **File-based IPC** - Communication between engine and GUI via text files

## Installation

### Requirements
- Python 3.7+
- VLC (VideoLAN)
- Python packages:
  - PySimpleGUI
  - python-vlc
  - tinytag

### Setup

```bash
pip install PySimpleGUI python-vlc tinytag
```

Ensure VLC is installed on your system: https://www.videolan.org/vlc/

## Usage

```bash
python main.py
```

The application will:
1. Initialize the jukebox engine
2. Load the 79-track music collection
3. Launch the GUI with background image
4. Start the engine in a background daemon thread
5. Display the interactive jukebox interface

## Project Structure

```
Convergence-Jukebox-Full-2026/
├── main.py                       # Main application (engine + GUI combined)
├── jukebox_config.json           # Configuration file
├── GenreFlagsList.txt            # Genre flags data
├── MusicMasterSongList.txt       # Song database
├── music/                        # Music directory (requires 79 MP3 files)
└── images/                       # Image assets (requires UI graphics)
```

## Architecture

### Engine (Daemon Thread)
- Manages VLC playback
- Reads playlist files (file-based IPC)
- Tracks current playing song
- Handles genre and playlist filtering

### GUI (Main Thread)
- FreeSimpleGUI application window
- Song selection interface
- Search functionality
- Playlist management
- Real-time updates via file I/O

### IPC Communication
- **PaidMusicPlayList.txt** - Paid playlist requests
- **CurrentSongPlaying.txt** - Current song metadata
- **UpcomingSongPlayList.txt** - Upcoming songs queue

## Configuration

Edit `jukebox_config.json` to customize:
- Logging settings
- File paths
- Console output options

## Setup Notes

For full functionality, you will need:
1. A `music/` directory with 79 MP3 files
2. An `images/` directory with required UI graphics
3. VLC installed on your system

## Version

2026 (Unified Integration) - Combined engine and GUI into single executable

## License

[Add your license here]
