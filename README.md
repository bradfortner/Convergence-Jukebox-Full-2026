# Convergence Jukebox (2026 Edition)

## Overview

Welcome to the Convergence Jukebox, a feature-rich, virtual jukebox application with a highly detailed, graphical interface built with **Pygame**. This software emulates the experience of a classic jukebox, allowing users to browse a vast music library, make selections, and see their choices play on a beautifully animated, rotating 45 RPM record.

The application is built on a robust Python foundation, using the powerful **VLC media player** for high-quality audio playback and dynamic audio processing. It is designed to be highly configurable and extensible, managing everything from ID3 tag extraction and playlist generation to dynamic record label creation and search functionality.

## Features

### Core Engine & Playback
-   **VLC Audio Engine:** Utilizes `python-vlc` for professional-grade audio playback.
-   **Advanced Audio Processing:** Features a built-in audio compressor and normalizer to provide a consistent listening experience across songs from different eras and mastering levels.
-   **Dual Playlist System:** Manages a priority "Paid Playlist" alongside a continuous "Random Playlist". Paid songs are always played first.
-   **Genre-Based Filtering:** The random playlist can be filtered to only include songs matching up to four specific genre tags (defined in `GenreFlagsList.txt`).
-   **Smart Playlist Generation:** Automatically generates and shuffles the random playlist, respecting genre filters and excluding any songs tagged with `norandom` in their ID3 comments.

### Music & Metadata Management
-   **Automatic Music Library Scanning:** On first launch, the application scans its `/music` directory to build a master song list (`MusicMasterSongList.txt`) from your MP3 files.
-   **ID3 Tag Extraction:** Uses `TinyTag` to read metadata (Title, Artist, Year, Album, Comment, Duration) from each MP3.
-   **Intelligent Rescanning:** Only regenerates the master song list if it detects a change in the number of MP3 files, ensuring fast startup times.
-   **Metadata Progress Bar:** Displays a graphical progress bar while scanning the music library for the first time.
-   **Artist Name Correction:** Includes a module (`the_bands_name_check_module.py`) to automatically apply the "The" prefix to band names like "Beatles" or "Rolling Stones" for correct display.

### Graphical User Interface (Pygame)
-   **High-Fidelity Jukebox Interface:** A fully custom GUI built with Pygame that emulates the look and feel of a classic jukebox.
-   **Dynamic Song Selection Grid:** Displays pages of songs with their titles and artists, which can be navigated with on-screen arrows.
-   **Interactive Song Selection:** Use keyboard commands to select songs.
-   **Animated Visualizations:**
    -   **Rotating Record (Idle Screensaver):** After a period of inactivity, a beautifully rendered 45 RPM record with an animated tonearm appears and rotates, displaying the currently playing song's information.
    -   **Paid Song Popup:** When a song is paid for, a popup appears showing the generated 45 RPM record for the selected song.
-   **Info Screen:** A dedicated panel shows the "Now Playing" song, a list of up to 10 "Upcoming Selections," and the number of credits.
-   **Operator Panel:** A hidden panel accessible via a specific key combination (code `7777`) for advanced controls.

### Keyboard Controls & Navigation
-   **Page Navigation:** Use the **Left** and **Right Arrow Keys** to move between pages of song selections.
-   **Song Selection:** This is a two-step process:
    1.  Press a **lowercase letter key (a, b, or c)** to select a column.
        *   **Visual Feedback (Song Selection Grid):** The song selection buttons in the selected column will remain fully visible, while those in the other two columns will dim.
        *   **Visual Feedback (Control Panel):** The letter button you pressed will **dim**, as will the other letter buttons. The number buttons (1-7) on the control panel will become **active** (fully visible), ready for your next input.
        *   **Interactive State:** The `SELECT` button will remain dimmed. The `CORRECT` button remains active.
    2.  Press a **Number Key (1-7)** to select a row within the chosen column.
    3.  Press **S** to confirm the selection.
        *   **Effect:** This adds the selected song to the paid playlist. Crucially, the code currently decrements credits when 'S' is pressed for selection.
-   **Add Credit:** Press **x** to add credits to the Jukebox before making any selections.
-   **Title Search:** Press the **letter 'T'** to open the Title Search window.
-   **Artist Search:** Press the **letter 'A'** to open the Artist Search window.
-   **Correction:** Press **C** to clear the current a/b/c or 1-7 selection.
-   **Exit:** Press **ESC** to quit the application.

### Dynamic Record Label Generation
-   **On-the-Fly Label Creation:** Generates unique 45 RPM record labels for each song using the `Pillow` library, rendering the song title and artist directly onto a blank label template.
-   **ID3 Album Art Priority:** If a song's ID3 comment tag contains the word `image`, the system will extract the embedded album art and use it as the record label, overriding all other rules.
-   **Christmas Label Priority:** If a song's ID3 comment tag contains `christmas`, a random label from the `/record_labels/blank_record_labels_christmas/` directory is used.
-   **Artist & Year-Based Logic:** Assigns specific record labels to artists (from `RecordLabelAssignList.txt`) or selects an era-appropriate label based on the song's year (from `YearRangeLabelList.txt`).
-   **Shared Caching:** Caches the assigned label for each song to ensure consistency across different popups and reduce redundant processing.

### Search Functionality
-   **Integrated Title & Artist Search:** Press 'T' for title search or 'A' for artist search to open dedicated search windows.
-   **Optimized Performance:** Uses a binary search algorithm for near-instant results, even with libraries containing over 16,000 songs.
-   **Full Keyboard Navigation:** The search interface is fully navigable using the keyboard, fitting the classic jukebox theme.

## Project History

This project has a long and storied history, evolving from a simpler application in 2015 to the current, highly advanced Pygame version. The `depreciated_code` directory contains over 150 previous iterations, showcasing a development journey focused on bug fixing, feature enhancement, and a complete migration from `PySimpleGUI` to `Pygame` for greater graphical control.

Version **0.90.68** represents the latest stable build, featuring numerous fixes for cross-platform compatibility, audio processing, UI layout, and race conditions in the playlist system.

## Getting Started

Follow these steps to get the Convergence Jukebox up and running.

### 1. Prerequisites
-   **Python 3.7+**
-   **VLC (VideoLAN Media Player):** The full VLC application must be installed on your system, as this project's audio engine depends on its libraries. Download it from [videolan.org](https://www.videolan.org/vlc/).

### 2. Required Files & Directories

For the application to run correctly, ensure the following files and directories are in place:

-   `0.90.68-Convergence-Jukebox-Full-2026.py` (The main script)
-   `jukebox_config.json` (Configuration file)
-   **`/music/`**: A directory containing its MP3 music files. The jukebox will scan this on first run.
-   **`/images/`**: Contains all the required background and button images for the GUI.
-   **`/fonts/`**: Contains the font files used for rendering text on record labels and the UI.
-   **`/jukebox_required_audio_files/`**: Contains UI sound effects (`buzz.mp3`, `success.mp3`).
-   **All Python Modules (`.py` files):** The application relies on a set of custom modules that must be in the same directory as the main script. The full list of required modules is:
    *   `artist_label_mapping_module.py`
    *   `metadata_progress_bar_module.py`
    *   `search_pygame_module.py`
    *   `song_label_cache_module.py`
    *   `the_bands_name_check_module.py`
    *   `year_range_label_mapping_module.py`

### 3. Installation

Install the required Python packages using pip:

```bash
pip install pygame python-vlc Pillow tinytag
```

-   **`pygame`**: The core framework for the graphical user interface, animations, and user input.
-   **`python-vlc`**: Python bindings for the VLC media player, used for the audio engine.
-   **`Pillow (PIL)`**: An image processing library used for dynamically generating record labels.
-   **`tinytag`**: A library for reading music metadata (ID3 tags) from your MP3 files.

### 4. Running the Jukebox

Once all prerequisites and files are in place, run the application from your terminal:

```bash
python 0.90.68-Convergence-Jukebox-Full-2026.py
```

On the first launch, the application will scan its `music/` directory and create the `MusicMasterSongList.txt` file. This may take a few moments, and a progress bar will be displayed. Subsequent launches will be much faster.

## Operating Systems

The application has been designed for cross-platform compatibility and is known to run on:

-   **Windows**
-   **Linux**

The code includes specific logic to handle filesystem differences, ensuring a consistent experience across operating systems.

---