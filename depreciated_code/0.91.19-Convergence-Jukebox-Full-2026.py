"""
CONVERGENCE JUKEBOX - PYGAME MIGRATION VERSION
Version 0.91.19 - Nuitka Compilation Prep

This version prepares the codebase for Nuitka C compilation with type hints,
import cleanup, variable type consistency, and structural verification.

Version 0.91.19 Changes:
- ADDED type hints to all 63 functions/methods across main file and 7 modules
- ADDED from typing import Optional, Union to main file and modules that need it
- MOVED PIL and io imports from inline to top-level in song_label_cache_module.py
- REMOVED unused imports: json from operator_panel_module, Tuple/Any from search_pygame_module, Callable from metadata_progress_bar_module
- FIXED popup_play_time and selection_popup_start_time initialized as 0.0 instead of 0 (int-to-float type consistency)
- VERIFIED no eval/exec/dynamic imports/__file__ usage in any active file

Version 0.91.18 Changes:
- OPTIMIZED InfoScreen.draw() - text surfaces now cached, only re-rendered when data changes (~20 font.render/frame eliminated)
- OPTIMIZED random_playlist changed from list to collections.deque - pop(0) is now O(1) instead of O(n) for 16K+ songs
- OPTIMIZED os.listdir() for record labels cached once at startup instead of every song selection
- MOVED all 'from datetime import datetime' to top-level import (12 inline imports removed)
- RENAMED unused modules: jukebox_selection_screen_layout_module.py → xjukebox_selection_screen_layout_module.py
- RENAMED unused modules: label_pressing_module.py → xlabel_pressing_module.py

Version 0.91.17 Changes:
- FIXED (CRITICAL) VLC Error state unhandled - jukebox no longer goes permanently silent on corrupt/missing files
- FIXED recursive play_next_song() converted to loop - prevents stack overflow on consecutive invalid entries
- FIXED infinite loop when random playlist regenerates empty - now breaks after one retry
- FIXED VLC media object leak - old media is now released before loading new song
- FIXED selection popup image loaded from disk every frame - now cached once at activation
- FIXED dimmed button surfaces recreated every frame - now pre-created and cached at init
- REDUCED rotated frame count from 360 to 72 (5-degree steps) - cuts ~600 MB memory per song

Version 0.91.16 Changes:
- OPTIMIZED vinyl animation: pre-calculate 360 rotated frames when song starts playing (background prep)
- CHANGED popup activation to use pre-generated frames for zero startup delay
- ADDED fallback: if pre-gen missed, frames are generated on the spot at popup time
- CHANGED pygame.transform.rotate to pygame.transform.rotozoom for anti-aliased rotation
- ADDED hardware acceleration flags (HWSURFACE | DOUBLEBUF) to display mode
- FIXED RECORD_ROTATION_SPEED comment (actual speed is 300 deg/sec at 60fps, not 240 at 30fps)
- REMOVED unused RECORD_ROTATION_FPS constant
- CHANGED per-frame rotation to pre-calculated frame lookup for zero per-frame rotation cost

Version 0.91.15 Changes:
- ADDED "45 RPM Animation On/Off" option to More Selections submenu (slot 1)
- ADDED load_popup_animation_setting() function to read setting from user_config.txt
- ADDED save_popup_animation_setting() function to persist setting to user_config.txt
- ADDED "popup_animation_enabled" field to user_config.txt defaults (default: true)
- ADDED toggle_popup_animation() function in operator_panel_module.py
- UPDATED More Selections submenu to return action string for 45 RPM Animation item
- UPDATED popup should_show logic to check POPUP_ANIMATION_ENABLED flag

Version 0.91.14 Changes:
- FIXED mouse click SELECT button not playing success sound
- FIXED mouse click SELECT button not showing selection record label popup
- ADDED success_sound.play() to mouse click SELECT handler
- ADDED selection popup generation (record label image with title/artist/ID3 art) to mouse click SELECT handler
- Mouse click SELECT now matches keyboard S key behavior exactly

Version 0.91.13 Changes:
- FIXED rotating record popup not using ID3 album art during playback
- CHANGED song_file_path construction from manual to using song['location'] (line 3612)
- Rotating record popup now correctly extracts ID3 album art when "image" comment tag present
- Both selection popup AND rotating record popup now use correct file paths for ID3 extraction
- ID3 album art now works consistently across all popup types (selection and playback)

Version 0.91.12 Changes:
- FIXED paid song selection popup not using ID3 album art
- FIXED UnboundLocalError: artist_name referenced before assignment (line 3434)
- CHANGED song_file_path construction from manual to using song['location'] (line 3437)
- CHANGED artist_name to use song['artist'] instead of undefined variable (line 3434)
- Selection popup now correctly extracts ID3 album art when "image" comment tag present
- Paid selections and random playback now both use correct file paths for ID3 extraction
- Selection popup no longer crashes when attempting to apply "The" prefix to artist name

Version 0.91.11 Changes:
- FIXED random music toggle not starting playback when jukebox is silent
- When enabling random music: generates playlist and starts playback if idle
- ADDED check: if new_setting is True and current_setting was False
- ADDED automatic playlist generation when enabling random music
- ADDED automatic playback start if player.is_playing() returns False
- Users no longer need to wait for a song to end or manually select a song after enabling random music

Version 0.91.10 Changes:
- FIXED genre filter not applying until restart bug
- ADDED playback_engine.generate_random_playlist() call after saving genre filters
- Genre changes now take effect immediately (no restart required)
- Updated success message to indicate "regenerating random playlist"
- Genre filter behavior now matches year range filter behavior (both regenerate immediately)

Version 0.91.09 Changes:
- ADDED user_config.txt creation to setup_files() function
- user_config.txt now created with all default settings if it doesn't exist:
  - access_code: ['7', '7', '7', '7']
  - random_music_enabled: true
  - credits_enabled: true
  - year_range_enabled: false
  - year_range_start: 1967
  - year_range_end: 1967
  - genre_flags: ['null', 'null', 'null', 'null']
- Centralizes all file initialization in one location for better organization
- Updated setup_files() docstring to reflect 7 files created (including user_config.txt)

Version 0.91.08 Changes:
- ACTIVATED "More Selections" menu item (item 6) on Operator Control Panel
- ADDED MORE_SELECTIONS_MENU_ITEMS submenu definition in operator_panel_module.py
- IMPLEMENTED submenu navigation with 5 "For Future Use" placeholder items
- Items 1-5: "For Future Use" - return to main jukebox screen when selected
- Item 6: "More Selections" - returns to main jukebox screen (placeholder for future expansion)
- Item 7: "Return To Jukebox" - returns to main jukebox screen
- Updated display_operator_panel() to handle 'more_selections' panel state
- Added keyboard navigation for More Selections submenu (1-7 keys, up/down arrows, S key)

Version 0.91.07 Changes:
- MOVED genre filter flags from GenreFlagsList.txt to user_config.txt
- ADDED "genre_flags" field to user_config.txt (stores array of 4 genre filters)
- UPDATED load_genre_flags() to read from user_config.txt instead of GenreFlagsList.txt
- ADDED save_genre_flags() function to persist genre settings to user_config.txt
- UPDATED operator_panel_module.py to save genres via new save_genre_flags() function
- REMOVED GenreFlagsList.txt file creation from setup_files()
- DEPRECATED GENRE_FLAGS_FILE_PATH constant (kept for backward compatibility)
- All genre settings now centralized in user_config.txt alongside other jukebox settings
- user_config.txt now stores: {"access_code": [...], "random_music_enabled": true, "credits_enabled": true, "year_range_enabled": false, "year_range_start": 1967, "year_range_end": 1967, "genre_flags": ["null", "null", "null", "null"]}

Version 0.91.06 Changes:
- CHANGED all default year values from 1010/2017 to 1967/1967
- UPDATED menu item from "For Future Use" to "Select Year Range"
- UPDATED screen title to "Select Year Range" for consistency
- Both year wheels now start at 1967 by default (unless previously configured)
- Config file defaults now use 1967 as the starting year for both start and end

Version 0.91.05 Changes:
- FIXED dual year wheel functionality - both wheels now work independently
- CHANGED default year to 1967 for both start and end year
- IMPROVED interaction flow: S key selects year and moves to next wheel
- ADDED auto-matching: first change to left wheel auto-matches right wheel (for single year selection)
- ENHANCED user feedback: context-sensitive instructions based on which wheel is active
- RIGHT wheel now enforces minimum constraint (end year cannot be before start year)
- LEFT/RIGHT arrow keys now navigate between all interface elements
- UP/DOWN arrow keys change year values when on a wheel, navigate when on checkbox/button

Version 0.91.04 Changes:
- ADDED select_year_range() function in operator_panel_module.py
- IMPLEMENTED dual year spinner interface with "through" separator and checkbox
- ADDED load_year_range_settings() and save_year_range_settings() functions
- UPDATED user_config.txt to include "year_range_enabled", "year_range_start", "year_range_end" fields
- UPDATED all existing save functions to preserve year range settings
- MODIFIED generate_random_playlist() to filter songs by year range when enabled
- Year spinners automatically detect available year range from music collection ID3 tags
- When year range is enabled, only songs within the specified range appear in random playlist
- Year range filter works alongside genre filters (both can be active simultaneously)
- Log entries now include year range information when active
- user_config.txt now stores: {"access_code": ["7","7","7","7"], "random_music_enabled": true, "credits_enabled": true, "year_range_enabled": false, "year_range_start": 1967, "year_range_end": 1967}

Version 0.91.03 Changes:
- ADDED toggle_credits() function in operator_panel_module.py
- IMPLEMENTED checkbox interface for Credits Required setting with navigable Save button
- ADDED load_credits_enabled() and save_credits_enabled() functions
- UPDATED user_config.txt to include "credits_enabled" field (default: true)
- UPDATED save_access_code() and save_random_music_setting() to preserve credits_enabled
- MODIFIED song selection logic (keyboard and touchscreen) to bypass credit check when disabled
- When credits are OFF, users can select unlimited songs without inserting quarters
- Credits are only deducted when credits_enabled is true
- user_config.txt now stores: {"access_code": ["7","7","7","7"], "random_music_enabled": true, "credits_enabled": true}

Version 0.91.02 Changes:
- ADDED toggle_random_music() function in operator_panel_module.py
- IMPLEMENTED checkbox interface for Play Random Music setting with navigable Save button
- MODIFIED user_config.txt format from CSV to JSON to store both access code and random_music_enabled
- UPDATED load_access_code() and save_access_code() to use JSON format with backward compatibility
- ADDED load_random_music_setting() and save_random_music_setting() functions
- MODIFIED playback engine to respect random_music_enabled setting
- When random music is OFF, only paid songs play (jukebox silent when queue empty)
- user_config.txt now stores: {"access_code": ["7","7","7","7"], "random_music_enabled": true}
- Backward compatible: old CSV format auto-converts to JSON on first load

Version 0.91.01 Changes:
- ADDED change_access_code() function in operator_panel_module.py
- IMPLEMENTED three-step workflow: verify current code → enter new code → confirm new code
- ADDED load_access_code() function to read from user_config.txt at startup
- ADDED save_access_code() function to persist new code to user_config.txt
- MODIFIED display_operator_panel() to accept and return access code changes
- Access code now stored in user_config.txt as comma-separated list (e.g., 2,1,2,4)
- Operator panel now passes current code and receives new code on successful change
- Only accepts digits 1-7 for security code entries
- Displays visual feedback with asterisks during code entry
- Error handling for incorrect current code and mismatched confirmation

Version 0.90.68 - Operator Code Update

This version updates the operator control panel access code for enhanced security/preference.

Version 0.90.68 Changes:
- CHANGED Operator Control Panel access code from 2311 to 7777
- UPDATED version header information

Version 0.90.65 - Audio Normalization & Compression

This version includes enhanced audio processing to normalize volume levels and compress dynamic range for a consistent listening experience.

Version 0.90.65 Changes:
- ENABLED VLC Audio Compressor and Normalizer filters
- ADDED specific settings for 'Radio Style' compression (4:1 ratio, -20dB threshold)
- NORMALIZED volume between tracks to prevent loudness jumps
- REMOVED duplicate "The" band entries (Dolly Parton, Loretta Lynn, Bobby Vinton) from the_bands.txt

Version 0.90.64 Changes:
- FIXED pathing for Christmas labels. The get_or_assign_label function now returns a relative path
for Christmas labels so that the main program can correctly locate them.

Version 0.90.63 Changes:
- ADDED Priority #2 for Christmas-themed labels
- Logic checks ID3 comment tag for "christmas"
- If found, randomly selects a label from `record_labels/blank_record_labels_christmas/`
- This check occurs after ID3 album art check but before song cache lookup

Version 0.90.61 Changes:
- FIXED ID3 album art detection bug in song_label_cache_module.py
- Bug: Comment tag containing "noimage" was incorrectly treated as "image" due to substring match
- The check 'image' in comment.lower() would match both "image" and "noimage"
- Fix: Added explicit exclusion check - now requires 'image' AND excludes 'noimage'
- Impact: Songs marked with "noimage" will no longer incorrectly trigger ID3 album art extraction
- Module: song_label_cache_module.py line 48-51

Version 0.90.60 Changes:
- FIXED cross-platform song ordering inconsistency
- Added explicit alphabetical sorting by artist (case-insensitive) in generate_music_master_song_list_dictionary()
- Songs now sorted after dictionary creation and before saving to MusicMasterSongList.txt
- Song numbers renumbered sequentially (0, 1, 2...) after sorting to match new order
- Bug: glob.glob() returns files in filesystem-dependent order (alphabetical on NTFS/Windows, inode order on ext4/Linux)
- Fix ensures consistent alphabetical-by-artist display on all platforms (Windows, Linux, Raspberry Pi)

Version 0.90.59 Changes:
- FIXED song display formula from skip pattern to sequential display
- Changed song_offset from (col_idx * 14) + ((row - 1) * 2) to (col_idx * 7) + (row - 1)
- Changed letter_offset from {'A': 0, 'B': 14, 'C': 28} to {'A': 0, 'B': 7, 'C': 14}
- Changed row_offset from (row - 1) * 2 to (row - 1)
- Updated column/row detection logic in dimming calculations
- Grid now displays songs 0-20 sequentially: A1-A7 (0-6), B1-B7 (7-13), C1-C7 (14-20)
- All songs now visible in alphabetical order without skipping
- Bug: Previous version skipped odd-indexed songs, hiding 3 of 5 songs by some artists

Version 0.90.57 Changes:
- ADDED format_button_text() function to truncate song titles/artists at 22 characters
- MODIFIED SelectionButtons._create_button_layout() to use text truncation
- Song titles and artist names now consistently limited to 22-character display
- Prevents text overflow on selection buttons during page navigation
- Text is left-justified and cleanly truncated when length >= 22 characters

Version 0.90.51 Changes:
- FIXED duplicate genre tags caused by whitespace
- Strips whitespace from each genre tag
- Filters out empty strings
- Preserves original case (e.g., "boomr&b" and "boomR&B" remain separate)

Version 0.90.50 Changes:
- FIXED genre logging to extract individual genre tags (not combinations)
- Splits comment field by spaces to get individual genre words
- Each unique genre tag listed only once in log
- Example: "classicrock canadian" logs as two separate entries

Version 0.90.49 Changes:
- ADDED genre list extraction and logging at startup
- Extracts all unique comment values (genres) from MusicMasterSongList
- Logs available genres to log.txt with timestamp
- Prints genre list to console for visibility
- Helps identify all music categories available in collection

Version 0.90.45 Changes:
- Reverted codebase to commit e7e4a9a (Version 0.90.41)
- Restored comprehensive logging system functionality
- Rolled back versions 0.90.42, 0.90.43, and 0.90.44

Version 0.90.41 Changes:
- ADDED comprehensive logging to log.txt for all jukebox events
- Log program startup with date/time
- Log songlist generation (new) and usage (existing)
- Log random playlist generation with active genre filters
- Log every random song played with title, artist
- Log every paid song played with title, artist
- Log quarter insertions (credits added)
- Log record image generation with song info and label .png filename
- Log when rotating record image pulled from cache
- Fixed AttributeError in logging code (used LOG_FILE_PATH constant)

Version 0.90.40 Changes:
- FIXED pygame double initialization crash (exit code 3489660927)
- Moved song list check/generation to BEFORE pygame.init() in main()
- Progress bar now gets exclusive pygame access, completes, then main app initializes
- Execution order: setup_files() → check/generate song list → pygame.init() → create window
- Progress bar thread calls pygame.init(), runs, then pygame.quit() cleanly
- Main app then calls pygame.init() fresh without conflicts
- Added detailed comments explaining why this order is critical
- Matches proven working pattern from original convergence_jukebox.py
- User experience: Progress bar shows → closes → main jukebox window opens

Technical Details:
- Pygame/SDL cannot be initialized twice (main thread + child thread)
- Progress bar must complete and call pygame.quit() before main init
- Song list generation now happens before any main pygame initialization
- Fatal error exit now uses sys.exit(1) instead of pygame.quit() (pygame not init yet)

Version 0.90.39 Changes:
- ADDED threaded pygame progress bar during MP3 metadata generation
- Progress bar shows real-time file count, percentage, and current filename
- Runs in separate thread to avoid blocking metadata extraction
- Displays "Loading Your Music Collection..." with green progress bar
- Updates on every file processed (not just every 100)
- Auto-closes after generation completes with 1 second pause
- Added import: MetadataProgressBar from metadata_progress_bar_module
- Modified generate_mp3_metadata() to initialize, update, and stop progress bar
- Removes need for console progress messages (GUI replaces text output)
- Matches original implementation from convergence_jukebox.py

Version 0.90.38 Changes:
- FIXED console flooding with VLC error messages
- Added '--quiet' and '--no-video' flags to VLC instance initialization
- Suppresses thousands of "stale plugins cache" error messages at startup
- Console output now clean and readable

Version 0.90.37 Changes:
- RESTORED song list generation functionality from original version (convergence_jukebox.py)
- Automatically scans music/ directory for MP3 files on first run
- Extracts ID3 metadata (title, artist, album, year, comment, duration) using TinyTag
- Generates MusicMasterSongList.txt with all song data
- Smart regeneration: only re-scans when MP3 file count changes
- Uses MusicMasterSongListCheck.txt to track song count for change detection
- Handles missing/corrupt metadata gracefully (continues processing)
- Duration stored in MM:SS format matching original implementation
- Console progress messages (no progress bar in Part 1)
- Jukebox now works out-of-box for new users with MP3 collection
- Added imports: glob, TinyTag
- Added constants: MUSIC_DIRECTORY, MUSIC_MASTER_SONG_LIST_CHECK_PATH
- Added functions: generate_mp3_metadata(), generate_music_master_song_list_dictionary()
- Modified main() startup to check/regenerate song list when needed

Version 0.90.32 Changes:
- RESTORED GenreFlags functionality from original version (0.83.60)
- Random playlist now respects genre filter settings from GenreFlagsList.txt
- Added 4 genre filter attributes to PlaybackEngine: genre0, genre1, genre2, genre3
- Added load_genre_flags() method to read filters from GenreFlagsList.txt
- Modified generate_random_playlist() to filter songs based on genre settings
- If all genres are "null": plays ALL songs (except 'norandom')
- If any genre is set: plays ONLY songs matching that genre in comment field
- Genre filters support OR logic (song matches if ANY filter matches)
- Displays active genre filters on startup with [GENRE FILTERS] prefix
- Warns if no songs match the current genre filter settings
- Example: GenreFlagsList.txt = ["rock", "null", "null", "null"] → only plays rock songs

Version 0.90.31 Changes:
- Added 3 more files to automatic initialization on startup
- YearRangeLabelList.txt: Year range to record label mapping (default: [])
- RecordLabelAssignList.txt: Artist to record label assignments (default: [])
- FullYearRangeLabelList.txt: Complete year range label data (default: [])
- Total files now checked/created: 7 (was 4 in v0.90.30)
- Added file path constants for all 3 new files
- Updated setup_files() docstring to reflect 7 files

Version 0.90.30 Changes:
- Restored file initialization from original version (0.83.60)
- Added setup_files() function to check and create required data files on startup
- Creates 4 files if missing: log.txt, GenreFlagsList.txt, MusicMasterSongListCheck.txt, PaidMusicPlayList.txt
- log.txt: Logs startup/restart events and playback errors
- GenreFlagsList.txt: Stores genre filter flags (default: ['null', 'null', 'null', 'null'])
- MusicMasterSongListCheck.txt: Tracks song list changes (default: [])
- PaidMusicPlayList.txt: Queue of user-selected paid songs (default: [])
- Prevents crashes on first run when files don't exist
- Added file path constants: LOG_FILE_PATH, GENRE_FLAGS_FILE_PATH, MUSIC_MASTER_SONG_LIST_CHECK_PATH
- setup_files() called at start of main() before pygame initialization

Version 0.90.29 Changes:
- Fixed search window header layout to match original exactly
- "Search For Title/Artist" text, magnifying glass, and search box now on same line
- All three elements on single white background bar (not separate boxes)
- Magnifying glass positioned between header text and search entry area
- Search text appears inline after magnifying glass (no separate box)
- Layout: [Search For Title] [🔍] [user typed text...]

Version 0.90.28 Changes:
- Added magnifying glass icon before search text box (matching original UI)
- Search text box now starts empty (no placeholder text)
- Fixed "Not On Jukebox" message to only appear when search finds no matches
- Message no longer displays on empty search box (only after typing 3+ characters)
- Restored original search window appearance and behavior
- Changes made to search_pygame_module.py only

Version 0.90.27 Changes:
- CRITICAL FIX: Rotating record popup no longer appears immediately after search closes
- Search window now tracks keypresses and returns last_keypress_time to main event loop
- Main file updates idle timer when search window closes to reset 20-second countdown
- User can now use search window without triggering popup when returning to main screen
- Modified search_pygame_module.py to track and return last keypress timestamp
- Modified main file to extract last_keypress_time from search result dict

Version 0.90.26 Changes:
- CRITICAL FIX: S key now works correctly in artist search
- S key logic reordered to check focus state FIRST before handling
- When typing directly: S adds 'S' to search query
- When navigating with arrows: S selects the focused button
- Typing "STONES" now works properly in artist search
- Removed duplicate S key handling code

Version 0.90.25 Changes:
- Added pygame-based title and artist search functionality
- Implemented optimized binary search for 16,000+ song library (~840x faster)
- Pre-sorted song lists at startup for O(log n) search performance
- Search only triggers when query >= 3 characters (reduces unnecessary searches)
- Full keyboard grid navigation (arrow keys, letters, numbers)
- Returns up to 5 results per search
- Press T for title search, A for artist search
- Replaces deprecated FreeSimpleGUI search module

Version 0.90.24 Changes:
- Added 45rpm song selection popup (appears when user selects a paid song)
- Generates custom record label with song title and artist
- Uses shared song_label_cache for consistency with rotating popup
- Respects artist-specific label assignments (RecordLabelAssignList.txt)
- Applies year-range filtering for era-appropriate labels
- Plays success sound effect on selection
- 3-second auto-close or ESC to dismiss
- Positioned at (32, 300) with 320x320 image size
- Green background behind record label

Version 0.90.23 Changes:
- Modified popup overlay behavior to hide buttons instead of dimming everything
- When popup appears: song buttons disappear, background/arrows/info screen stay visible
- Removed full-screen dark overlay (no longer dims entire interface)
- Matches behavior of previous FreeSimpleGUI version

Version 0.90.22 Changes:
- Added rotating record popup (idle screensaver) as overlay on main window
- Integrated song_label_cache_module for consistent label assignments
- Added record image generation with PIL (title/artist text rendering)
- Added Wurlitzer paddle-style tonearm animation
- Added idle timer tracking (20 second timeout)
- Popup shows after 20 seconds idle + 20 seconds playback
- Popup closes on any keypress or when song has <5 seconds remaining

Next Steps:
- Fine-tune search interface appearance
- Add more search options (genre, year, etc.)

Original Code Reference:
- All original 0.83.60 code is preserved in 0.83.60 - Convergence-Jukebox-Full-2026.py
"""

# ============================================================================ 
# SECTION 1: IMPORTS
# ============================================================================ 

import pygame
import sys
import os
import json
import vlc
import time
import random
import math
import glob
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Optional, Union
from PIL import Image, ImageDraw, ImageFont
from tinytag import TinyTag
from song_label_cache_module import get_or_assign_label
from search_pygame_module import display_search_popup
from metadata_progress_bar_module import MetadataProgressBar
from the_bands_name_check_module import load_the_bands_data, apply_the_prefix
from operator_panel_module import display_operator_panel, select_random_music_genres, toggle_random_music, toggle_credits, select_year_range, toggle_popup_animation

# ============================================================================ 
# SECTION 2: CONSTANTS
# ============================================================================ 

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_IMAGE_PATH = "images/Full Jukebox Background Master 2026.png"
SONG_LIST_PATH = "MusicMasterSongList.txt"
MUSIC_DIRECTORY = "music"
MUSIC_MASTER_SONG_LIST_CHECK_PATH = "MusicMasterSongListCheck.txt"
BUZZ_SOUND_PATH = "jukebox_required_audio_files/buzz.mp3"
SUCCESS_SOUND_PATH = "jukebox_required_audio_files/success.mp3"
PAID_MUSIC_PLAYLIST_PATH = "PaidMusicPlayList.txt"
CURRENT_SONG_PLAYING_PATH = "CurrentSongPlaying.txt"
LOG_FILE_PATH = "log.txt"
GENRE_FLAGS_FILE_PATH = "GenreFlagsList.txt"  # DEPRECATED: Genre flags now in user_config.txt (v0.91.07)
MUSIC_MASTER_SONG_LIST_CHECK_PATH = "MusicMasterSongListCheck.txt"
YEAR_RANGE_LABEL_LIST_PATH = "YearRangeLabelList.txt"
RECORD_LABEL_ASSIGN_LIST_PATH = "RecordLabelAssignList.txt"
FULL_YEAR_RANGE_LABEL_LIST_PATH = "FullYearRangeLabelList.txt"

# Button grid layout constants
GRID_START_X = 465
GRID_START_Y = 218

# Arrow button constants
ARROW_RIGHT_X = 1015
ARROW_RIGHT_Y = 160
ARROW_LEFT_X = 520
ARROW_LEFT_Y = 160

# Control button constants
CONTROL_START_X = 455
CONTROL_START_Y = 586

# Info screen constants (relative_location=(-448, 0) → absolute position)
INFO_START_X = 32
INFO_START_Y = 100

# Color constants (RGB)
COLOR_SEAGREEN3 = (67, 205, 128)
COLOR_WHITE = (255, 255, 255)

# Button image paths
BUTTON_ID_BG = "images/button_id_bg.png"
BUTTON_ID_BLACK_BG = "images/button_id_black_bg.png"
SELECTION_TOP_BG = "images/new_selection_top_bg.png"
ARROW_LEFT_IMG = "images/lg_arrow_left.png"
ARROW_RIGHT_IMG = "images/lg_arrow_right.png"

# Control button image paths
A_BUTTON_IMG = "images/a_button.png"
B_BUTTON_IMG = "images/b_button.png"
C_BUTTON_IMG = "images/c_button.png"
NUM_BUTTON_IMG = "images/{}_button.png"  # Format with number 1-7
SELECT_BUTTON_IMG = "images/select_button.png"
CORRECT_BUTTON_IMG = "images/correct_button.png"
BLANK_BUTTON_IMG = "images/blank_button.png"

# Rotating record popup constants
POPUP_MIN_PLAYBACK_TIME = 20           # Song must play >= 20 seconds before popup
POPUP_MIN_IDLE_TIME = 20               # User idle >= 20 seconds before popup
POPUP_CLOSE_SECONDS_REMAINING = 5      # Close popup when song has <= 5 seconds left
BLANK_RECORDS_DIR = "record_labels/blank_record_labels"
FONT_PATH = "fonts/OpenSans-ExtraBold.ttf"
OUTPUT_FILENAME = 'final_record_pressing.png'
MAX_TEXT_WIDTH = 300                   # Maximum width for song title (pixels)
ARTIST_MAX_TEXT_WIDTH = 250            # Maximum width for artist name (pixels)
SONG_Y = 90                            # Y position offset for song title (from center)
ARTIST_Y = 120                         # Y position offset for artist name (from center)
SONG_LINE_HEIGHT = 25                  # Vertical spacing between song title lines
ARTIST_LINE_HEIGHT = 30                # Vertical spacing between artist name lines
PNG_OUTPUT_WIDTH = 750                 # PNG image generation width
PNG_OUTPUT_HEIGHT = 750                # PNG image generation height
RECORD_ROTATION_SPEED = 5              # Degrees per frame (300° per second at 60fps)
PYGAME_BACKGROUND_COLOR = (64, 64, 64) # Dark grey background

# ============================================================================ 
# SECTION 3: UTILITY FUNCTIONS
# ============================================================================ 

def format_time_remaining(seconds: float) -> str:
    """Format seconds as MM:SS for display.

    Args:
        seconds (float): Number of seconds remaining

    Returns:
        str: Formatted time string like "03:45" or "00:12"
    """
    seconds = int(seconds)
    if seconds < 0:
        seconds = 0
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Wrap text to fit within a specified pixel width.

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
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines

def fit_text_to_width(text: str, base_font_path: str, start_size: int, max_width: int, max_lines: int, draw: ImageDraw.ImageDraw) -> tuple[list[str], int, ImageFont.FreeTypeFont]:
    """Auto-fit text by reducing font size until it fits within constraints.

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
    min_font_size = 16

    while font_size >= min_font_size:
        font = ImageFont.truetype(base_font_path, font_size)
        lines = wrap_text(text, font, max_width, draw)

        if len(lines) == 1:
            return lines, font_size, font

        if len(lines) <= max_lines:
            test_font = ImageFont.truetype(base_font_path, font_size - 2)
            test_lines = wrap_text(text, test_font, max_width, draw)
            if len(test_lines) <= max_lines:
                font_size -= 2
                continue
            else:
                return lines, font_size, font

        font_size -= 2

    font = ImageFont.truetype(base_font_path, min_font_size)
    return wrap_text(text, font, max_width, draw), min_font_size, font

def generate_record_image(song_title: str, artist_name: str, year: Optional[Union[int, str]] = None, song_file_path: Optional[str] = None) -> Optional[str]:
    """Generate a record label image with song title and artist.

    Args:
        song_title (str): The song title
        artist_name (str): The artist name
        year (int/str, optional): The year the song was created
        song_file_path (str, optional): Full path to MP3 file for ID3 extraction

    Returns:
        str: Path to the generated record image file
    """
    try:
        # Get all .png files from blank_record_labels directory
        png_files = [f for f in os.listdir(BLANK_RECORDS_DIR) if f.endswith('.png')]

        if not png_files:
            print(f"No .png files found in {BLANK_RECORDS_DIR}")
            return None

        # Get or assign label using cache (with ID3 priority)
        selected_label = get_or_assign_label(song_title, artist_name, png_files, year, song_file_path)

        # Check if ID3 image should be used
        if selected_label == "USE_ID3_IMAGE" and os.path.exists('id3_image.png'):
            # ID3 COMPOSITE PATH - Use ID3 album art instead of blank labels
            print(f"[ID3 COMPOSITE] Creating record from ID3 album art")

            # Load blank record as base (750x750)
            base_img = Image.open('images/blank_record.png')
            base_img = base_img.resize((PNG_OUTPUT_WIDTH, PNG_OUTPUT_HEIGHT), Image.Resampling.LANCZOS)

            # Load ID3 image (300x300 from Music File Cleaner)
            id3_img = Image.open('id3_image.png')
            if id3_img.mode != 'RGBA':
                id3_img = id3_img.convert('RGBA')

            # Center the 300x300 ID3 image on the 750x750 blank record
            id3_x = (PNG_OUTPUT_WIDTH - id3_img.width) // 2
            id3_y = (PNG_OUTPUT_HEIGHT - id3_img.height) // 2

            # Create final composite
            if base_img.mode != 'RGBA':
                base_img = base_img.convert('RGBA')

            final_img = base_img.copy()
            final_img.paste(id3_img, (id3_x, id3_y), id3_img)

            # Save the record image
            final_img.save(OUTPUT_FILENAME, 'PNG')
            print(f"[ID3 COMPOSITE] Generated record image: {OUTPUT_FILENAME}")

            # Log record image creation

            now = datetime.now().replace(microsecond=0)
            log_date = now.strftime("%Y-%m-%d")
            log_time = now.strftime("%H:%M:%S")
            try:
                with open('log.txt', 'a') as log:
                    log.write(f'\n{log_date}, {log_time}, {song_title}, {artist_name}, New Record Image Pressed, ID3_ALBUM_ART')
            except IOError as log_error:
                print(f"[ERROR] Failed to write to log.txt: {log_error}")

            return OUTPUT_FILENAME

        # STANDARD PATH - Use blank label from record_labels directory
        label_path = os.path.join(BLANK_RECORDS_DIR, selected_label)

        # Determine font color based on filename
        font_color = (255, 255, 255, 255) if selected_label.startswith("w_") else (0, 0, 0, 255)

        # Load the selected record label image
        base_img = Image.open(label_path)
        base_img = base_img.resize((PNG_OUTPUT_WIDTH, PNG_OUTPUT_HEIGHT), Image.Resampling.LANCZOS)

        width, height = base_img.size
        song_y = (height // 2) + SONG_Y
        artist_y = (height // 2) + ARTIST_Y

        # Create working copy
        img = base_img.copy()
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        draw = ImageDraw.Draw(img)

        # Auto-fit song title text
        song_lines, song_font_size, song_font = fit_text_to_width(
            song_title, FONT_PATH, 28, MAX_TEXT_WIDTH, 2, draw
        )

        # Auto-fit artist name text
        artist_lines, artist_font_size, artist_font = fit_text_to_width(
            artist_name, FONT_PATH, 25, ARTIST_MAX_TEXT_WIDTH, 2, draw
        )

        # Draw song title lines, centered
        for i, line in enumerate(song_lines):
            song_bbox = draw.textbbox((0, 0), line, font=song_font)
            song_width = song_bbox[2] - song_bbox[0]
            song_x = (width - song_width) // 2
            draw.text((song_x, song_y + (i * SONG_LINE_HEIGHT)), line, font=song_font, fill=font_color)

        # Adjust artist Y position based on number of song lines
        artist_y_adjusted = artist_y + ((len(song_lines) - 1) * SONG_LINE_HEIGHT)

        # Draw artist name lines, centered
        for i, line in enumerate(artist_lines):
            artist_bbox = draw.textbbox((0, 0), line, font=artist_font)
            artist_width = artist_bbox[2] - artist_bbox[0]
            artist_x = (width - artist_width) // 2
            draw.text((artist_x, artist_y_adjusted + (i * ARTIST_LINE_HEIGHT)), line, font=artist_font, fill=font_color)

        # Save the record image
        img.save(OUTPUT_FILENAME, 'PNG')
        print(f"Generated record image: {OUTPUT_FILENAME}")

        # Log record image creation

        now = datetime.now().replace(microsecond=0)
        log_date = now.strftime("%Y-%m-%d")
        log_time = now.strftime("%H:%M:%S")
        try:
            with open('log.txt', 'a') as log:
                log.write(f'\n{log_date}, {log_time}, {song_title}, {artist_name}, New Record Image Pressed, {selected_label}')
        except IOError as log_error:
            print(f"[ERROR] Failed to write to log.txt: {log_error}")

        return OUTPUT_FILENAME

    except Exception as e:
        print(f"Error generating record image: {e}")
        return None

# ============================================================================ 
# SECTION 4: TONEARM ANIMATION CLASSES
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
    """Base class for turntable tonearm with animation states."""

    def __init__(self, x: int, y: int, length: int = 200) -> None:
        self.pivot_x = x
        self.pivot_y = y
        self.length = length

        self.play_angle = -22
        self.end_angle = 5
        self.current_angle = -22
        self.target_angle = -22

        self.state = ToneArmState.PLAYING
        self.current_height = 0

        self.play_wobble = 0
        self.wobble_timer = 0

        self.needle_color = (200, 50, 50)

    def is_playing(self) -> bool:
        return True

    def get_state(self) -> ToneArmState:
        return self.state

    def update(self, dt: float) -> None:
        self.wobble_timer += dt * 3
        self.play_wobble = math.sin(self.wobble_timer) * 0.5

        angle_diff = self.target_angle - self.current_angle
        if abs(angle_diff) > 0.1:
            move_speed = 5
            if angle_diff > 0:
                self.current_angle += min(move_speed * dt, angle_diff)
            else:
                self.current_angle += max(-move_speed * dt, angle_diff)

    def draw(self, surface: pygame.Surface) -> None:
        pass

class WurlitzerPaddleToneArm(ToneArm):
    """Authentic Wurlitzer jukebox tonearm with paddle design."""

    def __init__(self, x: int, y: int, length: int = 180) -> None:
        super().__init__(x, y, length)

        self.arm_length = length * 0.85
        self.head_radius = length * 0.15
        self.base_width = 70
        self.top_width = 70

        self.play_angle = -8
        self.end_angle = 12
        self.current_angle = -22
        self.target_angle = -22

        self.arm_color = (140, 140, 145)
        self.arm_shadow = (100, 100, 105)
        self.arm_highlight = (170, 170, 175)
        self.head_color = (130, 130, 135)
        self.base_color = (120, 120, 125)
        self.pivot_brass = (180, 150, 100)

    def draw(self, surface: pygame.Surface) -> None:
        pivot_x = self.pivot_x
        pivot_y = self.pivot_y + self.current_height

        angle_rad = math.radians(self.current_angle + self.play_wobble)

        head_x = pivot_x + self.arm_length * math.sin(angle_rad)
        head_y = pivot_y - self.arm_length * math.cos(angle_rad)

        base_half = self.base_width / 2
        perp_angle = angle_rad + math.pi / 2

        base_left_x = pivot_x + base_half * math.cos(perp_angle)
        base_left_y = pivot_y + base_half * math.sin(perp_angle)
        base_right_x = pivot_x - base_half * math.cos(perp_angle)
        base_right_y = pivot_y - base_half * math.sin(perp_angle)

        top_half = self.top_width / 2
        top_offset = self.arm_length * 0.85

        top_center_x = pivot_x + top_offset * math.sin(angle_rad)
        top_center_y = pivot_y - top_offset * math.cos(angle_rad)

        top_left_x = top_center_x + top_half * math.cos(perp_angle)
        top_left_y = top_center_y + top_half * math.sin(perp_angle)
        top_right_x = top_center_x - top_half * math.cos(perp_angle)
        top_right_y = top_center_y - top_half * math.sin(perp_angle)

        # Draw base flare
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

        # Draw paddle arm
        paddle_points = [
            (int(base_left_x), int(base_left_y)),
            (int(base_right_x), int(base_right_y)),
            (int(top_right_x), int(top_right_y)),
            (int(top_left_x), int(top_left_y))
        ]

        pygame.draw.polygon(surface, self.arm_color, paddle_points)
        pygame.draw.line(surface, self.arm_highlight, (int(base_left_x), int(base_left_y)), (int(top_left_x), int(top_left_y)), 35)
        pygame.draw.line(surface, self.arm_shadow, (int(base_right_x), int(base_right_y)), (int(top_right_x), int(top_right_y)), 35)

        # Draw head
        pygame.draw.circle(surface, self.head_color, (int(head_x), int(head_y)), int(self.head_radius))
        pygame.draw.circle(surface, self.arm_shadow, (int(head_x), int(head_y)), int(self.head_radius), 2)

        # Draw grooves
        groove_length = self.head_radius * 0.6
        groove_spacing = self.head_radius * 0.25
        groove_angle = angle_rad

        for offset in [-groove_spacing, groove_spacing]:
            groove_start_x = head_x + offset * math.cos(perp_angle) - (groove_length/2) * math.sin(groove_angle)
            groove_start_y = head_y + offset * math.sin(perp_angle) + (groove_length/2) * math.cos(groove_angle)
            groove_end_x = head_x + offset * math.cos(perp_angle) + (groove_length/2) * math.sin(groove_angle)
            groove_end_y = head_y + offset * math.sin(perp_angle) - (groove_length/2) * math.cos(groove_angle)
            pygame.draw.line(surface, self.arm_shadow, (int(groove_start_x), int(groove_start_y)), (int(groove_end_x), int(groove_end_y)), 2)

        # Draw needle
        needle_length = self.head_radius * 0.4
        needle_x = head_x + (self.head_radius + needle_length) * math.sin(angle_rad)
        needle_y = head_y - (self.head_radius + needle_length) * math.cos(angle_rad)
        pygame.draw.line(surface, (80, 80, 85), (head_x, head_y), (needle_x, needle_y), 3)
        pygame.draw.circle(surface, self.needle_color, (int(needle_x), int(needle_y)), 3)

        # Draw pivots
        pivot_pos_y = pivot_y - self.arm_length * 0.3
        pivot_pos_x = pivot_x + self.arm_length * 0.3 * math.sin(angle_rad)
        pygame.draw.circle(surface, self.pivot_brass, (int(pivot_pos_x), int(pivot_pos_y)), 6)
        pygame.draw.circle(surface, (150, 120, 80), (int(pivot_pos_x), int(pivot_pos_y)), 6, 2)
        pygame.draw.circle(surface, (100, 80, 50), (int(pivot_pos_x), int(pivot_pos_y)), 2)

        pygame.draw.circle(surface, self.base_color, (pivot_x, pivot_y), 12)
        pygame.draw.circle(surface, self.arm_shadow, (pivot_x, pivot_y), 12, 2)
        pygame.draw.circle(surface, (80, 80, 85), (pivot_x, pivot_y), 5)
        pygame.draw.circle(surface, (60, 60, 65), (pivot_x, pivot_y), 2)

# ============================================================================ 
# SECTION 4.5: SONG SELECTION POPUP FUNCTIONS
# ============================================================================ 

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """
    Wrap text to fit within a specified pixel width.

    Breaks text into lines by word boundaries to ensure no line exceeds
    the maximum width. Uses the font metrics to calculate actual pixel widths.
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines


def fit_text_to_width(text: str, base_font_path: str, start_size: int, max_width: int, max_lines: int, draw: ImageDraw.ImageDraw) -> tuple[list[str], int, ImageFont.FreeTypeFont]:
    """
    Auto-fit text by reducing font size until it fits within constraints.

    Iteratively reduces font size by 2pt increments until text fits within
    the specified width and line limits.
    """
    font_size = start_size
    min_font_size = 16

    while font_size >= min_font_size:
        font = ImageFont.truetype(base_font_path, font_size)
        lines = wrap_text(text, font, max_width, draw)

        if len(lines) == 1:
            return lines, font_size, font

        if len(lines) <= max_lines:
            test_font = ImageFont.truetype(base_font_path, font_size - 2)
            test_lines = wrap_text(text, test_font, max_width, draw)
            if len(test_lines) <= max_lines:
                font_size -= 2
                continue
            else:
                return lines, font_size, font

        font_size -= 2

    font = ImageFont.truetype(base_font_path, min_font_size)
    return wrap_text(text, font, max_width, draw), min_font_size, font


def generate_selection_record_label(song_title: str, artist_name: str, available_labels: list[str], year: Optional[Union[int, str]] = None, song_file_path: Optional[str] = None) -> Optional[str]:
    """
    Generate a 45rpm record label image for song selection popup.

    Creates a custom record label with the song title and artist name,
    using the shared label cache to ensure consistency with the rotating popup.

    Args:
        song_title: Title of the song
        artist_name: Name of the artist
        available_labels: List of available label PNG files
        year: Year of the song (optional, for era filtering)
        song_file_path: Full path to MP3 file for ID3 extraction

    Returns:
        Path to the generated composite image file
    """
    print(f"\n[SELECTION POPUP] Generating label for: {song_title} - {artist_name}")

    # Get or assign label using shared cache (with ID3 priority)
    selected_label = get_or_assign_label(song_title, artist_name, available_labels, year, song_file_path)

    # Check if ID3 image should be used
    if selected_label == "USE_ID3_IMAGE" and os.path.exists('id3_image.png'):
        # ID3 COMPOSITE PATH - Use ID3 album art directly
        print(f"[SELECTION POPUP ID3] Using ID3 album art")

        # Load ID3 image and create green background composite
        try:
            record_label = Image.open('id3_image.png')

            # Create 610x610 green background
            bg_width = 610
            bg_height = 610
            green_color = (0, 128, 0, 255)
            background = Image.new('RGBA', (bg_width, bg_height), green_color)

            if record_label.mode != 'RGBA':
                record_label = record_label.convert('RGBA')

            # Center record on background
            record_width, record_height = record_label.size
            x_position = (bg_width - record_width) // 2
            y_position = (bg_height - record_height) // 2

            composite = background.copy()
            composite.paste(record_label, (x_position, y_position), record_label)

            # Resize to 250x250
            popup_width = 250
            popup_height = 250
            composite = composite.resize((popup_width, popup_height), Image.Resampling.LANCZOS)

            # Save composite
            composite_filename = 'final_record_with_background.png'
            composite.save(composite_filename, 'PNG')
            print(f"[SELECTION POPUP ID3] Created composite: {composite_filename} ({popup_width}x{popup_height})")

            return composite_filename

        except Exception as e:
            print(f"[SELECTION POPUP ID3] Error creating composite: {e}")
            # Fall through to standard path

    # STANDARD PATH - Use blank label from record_labels directory
    label_path = os.path.join("record_labels/blank_record_labels", selected_label)

    # Determine font color based on filename
    font_color = (255, 255, 255, 255) if selected_label.startswith("w_") else (0, 0, 0, 255)
    color_mode = "WHITE" if selected_label.startswith("w_") else "BLACK"
    print(f"[SELECTION POPUP] Using label: {selected_label} ({color_mode} text)")

    # Load the blank record label
    base_img = Image.open(label_path)
    width, height = base_img.size

    # Configuration
    font_path = "fonts/OpenSans-ExtraBold.ttf"
    max_text_width = 300
    artist_max_text_width = 250
    song_y = (height // 2) + 90
    artist_y = (height // 2) + 120
    song_line_height = 25
    artist_line_height = 30

    # Create working copy
    img = base_img.copy()
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    draw = ImageDraw.Draw(img)

    # Auto-fit song title text
    song_lines, song_font_size, song_font = fit_text_to_width(
        song_title, font_path, 28, max_text_width, 2, draw
    )

    # Auto-fit artist name text
    artist_lines, artist_font_size, artist_font = fit_text_to_width(
        artist_name, font_path, 25, artist_max_text_width, 2, draw
    )

    # Draw song title lines (centered)
    for i, line in enumerate(song_lines):
        song_bbox = draw.textbbox((0, 0), line, font=song_font)
        song_width = song_bbox[2] - song_bbox[0]
        song_x = (width - song_width) // 2
        draw.text(
            (song_x, song_y + (i * song_line_height)),
            line, 
            font=song_font,
            fill=font_color
        )

    # Adjust artist Y position based on song lines
    artist_y_adjusted = artist_y + ((len(song_lines) - 1) * song_line_height)

    # Draw artist name lines (centered)
    for i, line in enumerate(artist_lines):
        artist_bbox = draw.textbbox((0, 0), line, font=artist_font)
        artist_width = artist_bbox[2] - artist_bbox[0]
        artist_x = (width - artist_width) // 2
        draw.text(
            (artist_x, artist_y_adjusted + (i * artist_line_height)),
            line, 
            font=artist_font,
            fill=font_color
        )

    # Save the record image
    filename = 'final_record_pressing.png'
    img.save(filename, 'PNG')
    print(f"[SELECTION POPUP] Saved record label: {filename}")

    # Log record image creation

    now = datetime.now().replace(microsecond=0)
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S")
    try:
        with open('log.txt', 'a') as log:
            log.write(f'\n{log_date}, {log_time}, {song_title}, {artist_name}, New Record Image Pressed, {selected_label}')
    except IOError as log_error:
        print(f"[ERROR] Failed to write to log.txt: {log_error}")

    # Composite with green background
    try:
        record_label = Image.open(filename)

        # Create 610x610 green background
        bg_width = 610
        bg_height = 610
        green_color = (0, 128, 0, 255)
        background = Image.new('RGBA', (bg_width, bg_height), green_color)

        if record_label.mode != 'RGBA':
            record_label = record_label.convert('RGBA')

        # Center record on background
        record_width, record_height = record_label.size
        x_position = (bg_width - record_width) // 2
        y_position = (bg_height - record_height) // 2

        composite = background.copy()
        composite.paste(record_label, (x_position, y_position), record_label)

        # Resize to 320x320
        popup_width = 250
        popup_height = 250
        composite = composite.resize((popup_width, popup_height), Image.Resampling.LANCZOS)

        # Save composite
        composite_filename = 'final_record_with_background.png'
        composite.save(composite_filename, 'PNG')
        print(f"[SELECTION POPUP] Created composite: {composite_filename} ({popup_width}x{popup_height})")

        return composite_filename

    except Exception as e:
        print(f"[SELECTION POPUP] Error creating composite: {e}")
        return filename


# ============================================================================ 
# SECTION 5: TEXT FORMATTING HELPER
# ============================================================================ 

def format_button_text(text: str, max_length: int = 22) -> str:
    """
    Format text for button display with left justification and truncation.

    Ensures text displayed on song selection buttons is limited to a maximum length
    to prevent overflow. Text longer than max_length is truncated to exactly max_length
    characters and left-justified.

    Args:
        text (str): The text to format (song title or artist name)
        max_length (int): Maximum characters to display (default 22)

    Returns:
        str: Formatted text, truncated to max_length if necessary

    Example:
        >>> format_button_text("Short Title", 22)
        'Short Title'
        >>> format_button_text("This Is A Very Long Song Title That Exceeds Limit", 22)
        'This Is A Very Long So'
    """
    if len(text) >= max_length:
        # Truncate to exactly max_length characters
        return text[:max_length]
    else:
        # Text is shorter than limit, return as-is
        return text


# ============================================================================ 
# SECTION 6: BUTTON GRID CLASS
# ============================================================================ 

class ButtonGrid:
    """Manages the selection button grid (A1-A7, B1-B7, C1-C7)"""

    def __init__(self, start_x: int, start_y: int, song_list: list[dict], selection_window_number: int = 0) -> None:
        """Initialize the button grid

        Args:
            start_x: X position to start drawing the grid
            start_y: Y position to start drawing the grid
            song_list: List of song dictionaries from MusicMasterSongList.txt
            selection_window_number: Starting index for displaying songs (default 0)
        """
        self.start_x = start_x
        self.start_y = start_y
        self.song_list = song_list
        self.selection_window_number = selection_window_number

        # Load button images
        try:
            self.button_id_img = pygame.image.load(BUTTON_ID_BG)
            self.button_black_img = pygame.image.load(BUTTON_ID_BLACK_BG)
            self.selection_bg_img = pygame.image.load(SELECTION_TOP_BG)
        except pygame.error as e:
            print(f"Error loading button images: {e}")
            raise

        # Create fonts (using Montserrat-Bold from fonts directory)
        self.font_id = pygame.font.Font('fonts/Montserrat-Bold.ttf', 16)
        self.font_song = pygame.font.Font('fonts/Montserrat-Bold.ttf', 14)

        # Load "The" bands data for artist name checking
        self.the_bands_set = load_the_bands_data()

        # Pre-create dimmed versions of button images (avoids per-frame surface copies)
        self._dimmed_cache = {}
        for img in [self.button_id_img, self.button_black_img, self.selection_bg_img]:
            dimmed = img.copy()
            dimmed.set_alpha(128)
            self._dimmed_cache[id(img)] = dimmed

        # Build button grid structure
        self.buttons = self._create_button_layout()

    def _create_button_layout(self) -> list[list[dict]]:
        """Create the button grid layout data structure

        Returns:
            List of button definitions with positions and properties
        """
        buttons = []

        # Define button columns (A, B, C)
        columns = ['A', 'B', 'C']

        # Current Y position tracker
        current_y = self.start_y

        # Create 7 rows
        for row in range(1, 8):
            row_buttons = []
            current_x = self.start_x

            # Create 3 columns per row
            for col_idx, col_letter in enumerate(columns):
                # Calculate song index offset (A=0-6, B=7-13, C=14-20, sequential)
                song_offset = (col_idx * 7) + (row - 1)

                # ID Button (e.g., "A1", "B1", "C1")
                button_id = f"{col_letter}{row}"
                row_buttons.append({
                    'type': 'id',
                    'text': button_id,
                    'x': current_x,
                    'y': current_y,
                    'image': self.button_id_img,
                    'font': self.font_id
                })
                current_x += self.button_id_img.get_width()

                # Song Title Button
                song_idx = self.selection_window_number + song_offset
                title_text = ""
                if song_idx < len(self.song_list):
                    # Format title with 22-char truncation to prevent overflow
                    title_text = format_button_text(self.song_list[song_idx]['title'], 22)

                row_buttons.append({
                    'type': 'title',
                    'text': title_text,
                    'x': current_x,
                    'y': current_y,
                    'image': self.selection_bg_img,
                    'font': self.font_song,
                    'song_index': song_offset
                })
                current_x += self.selection_bg_img.get_width()

            buttons.append(row_buttons)
            current_y += self.button_id_img.get_height()

            # Add artist row (spacer + artist text)
            artist_row = []
            current_x = self.start_x

            for col_idx, col_letter in enumerate(columns):
                song_offset = (col_idx * 7) + (row - 1)

                # Black spacer
                artist_row.append({
                    'type': 'spacer',
                    'text': '',
                    'x': current_x,
                    'y': current_y,
                    'image': self.button_black_img,
                    'font': self.font_id
                })
                current_x += self.button_black_img.get_width()

                # Artist name
                song_idx = self.selection_window_number + song_offset
                artist_text = ""
                if song_idx < len(self.song_list):
                    artist_text = self.song_list[song_idx]['artist']
                    # Apply "The" prefix check
                    artist_text = apply_the_prefix(artist_text, self.the_bands_set)
                    # Format artist with 22-char truncation to prevent overflow
                    artist_text = format_button_text(artist_text, 22)

                artist_row.append({
                    'type': 'artist',
                    'text': artist_text,
                    'x': current_x,
                    'y': current_y,
                    'image': self.selection_bg_img,
                    'font': self.font_song,
                    'song_index': song_offset
                })
                current_x += self.selection_bg_img.get_width()

            buttons.append(artist_row)
            current_y += self.button_black_img.get_height()

        return buttons

    def update_selection_window(self, new_selection_window_number: int) -> None:
        """Update the grid to show a different page of songs

        Args:
            new_selection_window_number: New starting index for songs
        """
        self.selection_window_number = new_selection_window_number
        # Rebuild the button layout with new song data
        self.buttons = self._create_button_layout()

    def draw(self, screen: pygame.Surface, selection_letter: Optional[str] = None, selection_number: Optional[int] = None) -> None:
        """Draw all buttons in the grid

        Args:
            screen: Pygame surface to draw on
            selection_letter: Currently selected letter (A, B, or C) or None
            selection_number: Currently selected number (1-7) or None
        """
        for row in self.buttons:
            for button in row:
                # Determine if this button should be dimmed
                is_dimmed = False

                # If a letter is selected, dim other columns
                if selection_letter and button['type'] in ('id', 'title', 'artist', 'spacer'):
                    button_letter = None
                    if 'text' in button and len(button['text']) > 0:
                        button_letter = button['text'][0] if button['type'] == 'id' else None

                    # Check song_index to determine column
                    if 'song_index' in button:
                        song_idx = button['song_index']
                        if song_idx < 7:
                            button_letter = 'A'
                        elif song_idx < 14:
                            button_letter = 'B'
                        else:
                            button_letter = 'C'

                    if button_letter and button_letter != selection_letter:
                        is_dimmed = True

                # If a number is selected, dim other rows
                if selection_number and button['type'] in ('id', 'title', 'artist', 'spacer'):
                    if button['type'] == 'id' and len(button['text']) > 1:
                        button_number = int(button['text'][1])
                        if button_number != selection_number:
                            is_dimmed = True
                    elif 'song_index' in button:
                        # Calculate row from song_index
                        song_idx = button['song_index']
                        if song_idx < 7:
                            row_num = song_idx + 1
                        elif song_idx < 14:
                            row_num = (song_idx - 7) + 1
                        else:
                            row_num = (song_idx - 14) + 1
                        if row_num != selection_number:
                            is_dimmed = True

                # Draw button background image
                img = button['image']
                if is_dimmed:
                    # Use pre-created dimmed version (cached at init)
                    screen.blit(self._dimmed_cache[id(img)], (button['x'], button['y']))
                else:
                    screen.blit(img, (button['x'], button['y']))

                # Draw button text if present
                if button['text']:
                    # Render text
                    text_color = (0, 0, 0) if not is_dimmed else (128, 128, 128)
                    text_surface = button['font'].render(button['text'], True, text_color)

                    # Center text on button
                    text_rect = text_surface.get_rect()
                    button_rect = button['image'].get_rect()
                    text_rect.center = (
                        button['x'] + button_rect.width // 2,
                        button['y'] + button_rect.height // 2
                    )

                    screen.blit(text_surface, text_rect)

# ============================================================================ 
# SECTION 5: CONTROL BUTTON CLASS
# ============================================================================ 

class ControlButtons:
    """Manages the control buttons (A, B, C, 1-7, SELECT, CORRECT)"""

    def __init__(self, start_x: int, start_y: int) -> None:
        """Initialize control buttons

        Args:
            start_x: X position to start drawing buttons
            start_y: Y position to start drawing buttons
        """
        self.start_x = start_x
        self.start_y = start_y

        # Load button images
        try:
            self.a_button_img = pygame.image.load(A_BUTTON_IMG)
            self.b_button_img = pygame.image.load(B_BUTTON_IMG)
            self.c_button_img = pygame.image.load(C_BUTTON_IMG)
            self.select_button_img = pygame.image.load(SELECT_BUTTON_IMG)
            self.correct_button_img = pygame.image.load(CORRECT_BUTTON_IMG)
            self.blank_button_img = pygame.image.load(BLANK_BUTTON_IMG)

            # Load number button images (1-7)
            self.num_button_imgs = {}
            for i in range(1, 8):
                self.num_button_imgs[i] = pygame.image.load(NUM_BUTTON_IMG.format(i))
        except pygame.error as e:
            print(f"Error loading control button images: {e}")
            raise

        # Build button layout
        self.buttons = self._create_button_layout()

        # Pre-create dimmed versions of each button image (avoids per-frame surface copies)
        self._dimmed_cache = {}
        for button in self.buttons:
            img = button['image']
            img_id = id(img)
            if img_id not in self._dimmed_cache:
                dimmed = img.copy()
                dimmed.set_alpha(100)
                self._dimmed_cache[img_id] = dimmed

    def _create_button_layout(self) -> list[dict]:
        """Create control button layout

        Returns:
            List of button definitions
        """
        buttons = []

        # Row 1: Blank spacers, A, B, C, 1, 2
        current_x = self.start_x
        current_y = self.start_y

        # Skip initial blanks (35px + 4 × 50px = 235px)
        current_x += 35 + (4 * 50)

        # A button
        buttons.append({
            'key': 'A',
            'x': current_x,
            'y': current_y,
            'image': self.a_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 50, 50)
        })
        current_x += 50

        # B button
        buttons.append({
            'key': 'B',
            'x': current_x,
            'y': current_y,
            'image': self.b_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 50, 50)
        })
        current_x += 50

        # C button
        buttons.append({
            'key': 'C',
            'x': current_x,
            'y': current_y,
            'image': self.c_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 50, 50)
        })
        current_x += 50

        # Number buttons 1 and 2
        for num in [1, 2]:
            buttons.append({
                'key': str(num),
                'x': current_x,
                'y': current_y,
                'image': self.num_button_imgs[num],
                'enabled': False,
                'rect': pygame.Rect(current_x, current_y, 50, 50)
            })
            current_x += 50

        # Row 2: Skip blank (50px), CORRECT button (150px), skip blank (35px), then 3-7, skip blank, SELECT
        current_x = self.start_x
        current_y = self.start_y + 50 + 6  # 50px button height + 6px spacing

        # Skip blank (50px)
        current_x += 50

        # CORRECT button
        buttons.append({
            'key': 'CORRECT',
            'x': current_x,
            'y': current_y,
            'image': self.correct_button_img,
            'enabled': True,
            'rect': pygame.Rect(current_x, current_y, 150, 50)
        })
        current_x += 150

        # Skip blank (35px)
        current_x += 35

        # Number buttons 3-7
        for num in [3, 4, 5, 6, 7]:
            buttons.append({
                'key': str(num),
                'x': current_x,
                'y': current_y,
                'image': self.num_button_imgs[num],
                'enabled': False,
                'rect': pygame.Rect(current_x, current_y, 50, 50)
            })
            current_x += 50

        # Skip blank (35px)
        current_x += 35

        # SELECT button
        buttons.append({
            'key': 'SELECT',
            'x': current_x,
            'y': current_y,
            'image': self.select_button_img,
            'enabled': False,
            'rect': pygame.Rect(current_x, current_y, 150, 50)
        })

        return buttons

    def update_button_states(self, selection_letter: Optional[str] = None, selection_number: Optional[int] = None) -> None:
        """Update which buttons are enabled/disabled

        Args:
            selection_letter: Selected letter (A, B, C) or None
            selection_number: Selected number (1-7) or None
        """
        for button in self.buttons:
            key = button['key']

            if key in ['A', 'B', 'C']:
                # Letter buttons enabled if no letter selected, or this is the selected letter
                button['enabled'] = (selection_letter is None) or (key == selection_letter)

            elif key in ['1', '2', '3', '4', '5', '6', '7']:
                # Number buttons enabled only if letter selected but number not yet selected
                button['enabled'] = (selection_letter is not None) and (selection_number is None)

            elif key == 'SELECT':
                # SELECT enabled only if both letter and number selected
                button['enabled'] = (selection_letter is not None) and (selection_number is not None)

            elif key == 'CORRECT':
                # CORRECT button always enabled
                button['enabled'] = True

    def draw(self, screen: pygame.Surface, selection_letter: Optional[str] = None, selection_number: Optional[int] = None) -> None:
        """Draw all control buttons

        Args:
            screen: Pygame surface to draw on
            selection_letter: Currently selected letter (A, B, or C) or None
            selection_number: Currently selected number (1-7) or None
        """
        for button in self.buttons:
            # Determine if button should be dimmed
            should_dim = False

            # Dim if button is disabled
            if not button['enabled']:
                should_dim = True
            # Also dim if this button is the selected letter
            elif button['key'] in ['A', 'B', 'C'] and button['key'] == selection_letter:
                should_dim = True
            # Also dim if this button is the selected number
            elif button['key'] in ['1', '2', '3', '4', '5', '6', '7'] and button['key'] == str(selection_number):
                should_dim = True

            # Draw button
            img = button['image']
            if should_dim:
                # Use pre-created dimmed version (cached at init)
                screen.blit(self._dimmed_cache[id(img)], (button['x'], button['y']))
            else:
                screen.blit(img, (button['x'], button['y']))

    def handle_click(self, pos: tuple[int, int]) -> Optional[str]:
        """Check if a button was clicked

        Args:
            pos: Mouse position (x, y)

        Returns:
            Button key if clicked and enabled, None otherwise
        """
        for button in self.buttons:
            if button['enabled'] and button['rect'].collidepoint(pos):
                return button['key']
        return None

# ============================================================================ 
# SECTION 6: INFO SCREEN CLASS
# ============================================================================ 

class InfoScreen:
    """Manages the info screen display (now playing, upcoming, credits)"""

    def __init__(self, start_x: int, start_y: int, song_list: list[dict]) -> None:
        """Initialize info screen

        Args:
            start_x: X position to start drawing
            start_y: Y position to start drawing
            song_list: Full song list for lookups
        """
        self.start_x = start_x
        self.start_y = start_y
        self.song_list = song_list

        # Create fonts (using Montserrat-Bold from fonts directory)
        self.font_header_large = pygame.font.Font('fonts/Montserrat-Bold.ttf', 26)
        self.font_header_medium = pygame.font.Font('fonts/Montserrat-Bold.ttf', 18)
        self.font_song_title = pygame.font.Font('fonts/Montserrat-Bold.ttf', 18)
        self.font_song_artist = pygame.font.Font('fonts/Montserrat-Bold.ttf', 16)
        self.font_info = pygame.font.Font('fonts/Montserrat-Bold.ttf', 12)
        self.font_credits = pygame.font.Font('fonts/Montserrat-Bold.ttf', 26)

        # Initialize display data
        self.current_song_index = None
        self.upcoming_songs = []
        self.credits = 0
        self.time_remaining = ""

        # Text surface cache - avoids ~20 font.render() calls per frame
        self._cache = {}
        self._cache_key = None  # Tuple used to detect data changes

        # Pre-render static text surfaces (never change)
        self._static_now_playing = self.font_header_large.render("Now Playing", True, COLOR_SEAGREEN3)
        self._static_mode = self.font_info.render("  Mode: Playing Song", True, COLOR_SEAGREEN3)
        self._static_upcoming = self.font_header_medium.render("Upcoming Selections", True, COLOR_SEAGREEN3)
        self._static_25cents = self.font_info.render("Twenty-Five Cents Per Selection", True, COLOR_SEAGREEN3)
        self._static_total_songs = self.font_info.render(
            f"{len(self.song_list)} Song Selections Available", True, COLOR_SEAGREEN3
        )

    def update(self, current_song_index: Optional[int], upcoming_songs: list[str], credits: int, time_remaining_seconds: Optional[float] = None) -> None:
        """Update info screen data

        Args:
            current_song_index: Index of currently playing song or None
            upcoming_songs: List of upcoming song indices
            credits: Number of credits available
            time_remaining_seconds: Seconds remaining in current song or None
        """
        self.current_song_index = current_song_index
        self.upcoming_songs = upcoming_songs[:10]  # Max 10 upcoming
        self.credits = credits

        if time_remaining_seconds is not None:
            self.time_remaining = format_time_remaining(time_remaining_seconds)
        else:
            self.time_remaining = ""

        # Build cache key to detect changes - only re-render when data actually changes
        new_key = (current_song_index, tuple(self.upcoming_songs), credits, self.time_remaining)
        if new_key != self._cache_key:
            self._cache_key = new_key
            self._rebuild_cache()

    def _rebuild_cache(self) -> None:
        """Re-render text surfaces only when display data has changed"""
        c = {}

        # Song-specific surfaces
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            c['title'] = self.font_song_title.render(song['title'], True, COLOR_WHITE)
            c['artist'] = self.font_song_artist.render(song['artist'], True, COLOR_WHITE)
            c['mini_title'] = self.font_info.render('  Title: ' + song['title'], True, COLOR_SEAGREEN3)
            c['mini_artist'] = self.font_info.render('  Artist: ' + song['artist'], True, COLOR_SEAGREEN3)
            if self.time_remaining:
                year_time = f"  Year: {song['year']}   Length: {song['duration']}   Remaining: {self.time_remaining}"
            else:
                year_time = f"  Year: {song['year']}   Length: {song['duration']}"
            c['year_time'] = self.font_info.render(year_time, True, COLOR_SEAGREEN3)
            c['album'] = self.font_info.render('  Album: ' + song['album'], True, COLOR_SEAGREEN3)

        # Upcoming song surfaces
        c['upcoming'] = []
        for i, song_str in enumerate(self.upcoming_songs):
            upcoming_text = f"{i+1}. {song_str}"
            c['upcoming'].append(self.font_info.render(upcoming_text, True, COLOR_SEAGREEN3))

        # Credits
        c['credits'] = self.font_credits.render(f"CREDITS {self.credits}", True, COLOR_WHITE)

        self._cache = c

    def draw(self, screen: pygame.Surface) -> None:
        """Draw info screen on the display using cached text surfaces

        Args:
            screen: Pygame surface to draw on
        """
        c = self._cache
        current_y = self.start_y + 10

        # "Now Playing" header (static)
        rect = self._static_now_playing.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(self._static_now_playing, rect)
        current_y += 30

        # Current song title
        if 'title' in c:
            rect = c['title'].get_rect(center=(self.start_x + 145, current_y))
            screen.blit(c['title'], rect)
        current_y += 25

        # Current artist
        if 'artist' in c:
            rect = c['artist'].get_rect(center=(self.start_x + 145, current_y))
            screen.blit(c['artist'], rect)
        current_y += 25

        # Mode indicator (static)
        screen.blit(self._static_mode, (self.start_x, current_y))
        current_y += 18

        # Mini song title
        if 'mini_title' in c:
            screen.blit(c['mini_title'], (self.start_x, current_y))
        current_y += 18

        # Mini artist
        if 'mini_artist' in c:
            screen.blit(c['mini_artist'], (self.start_x, current_y))
        current_y += 18

        # Year & Time Remaining
        if 'year_time' in c:
            screen.blit(c['year_time'], (self.start_x, current_y))
        current_y += 18

        # Album
        if 'album' in c:
            screen.blit(c['album'], (self.start_x, current_y))
        current_y += 30

        # "Upcoming Selections" header (static)
        rect = self._static_upcoming.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(self._static_upcoming, rect)
        current_y += 28

        # Spacer
        current_y += 5

        # 10 upcoming song slots
        for i in range(10):
            if i < len(c.get('upcoming', [])):
                screen.blit(c['upcoming'][i], (self.start_x, current_y))
            current_y += 18

        # Spacer
        current_y += 5

        # Credits display
        if 'credits' in c:
            rect = c['credits'].get_rect(center=(self.start_x + 145, current_y))
            screen.blit(c['credits'], rect)
        current_y += 30

        # "Twenty-Five Cents Per Selection" (static)
        rect = self._static_25cents.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(self._static_25cents, rect)
        current_y += 18

        # Total songs available (static)
        rect = self._static_total_songs.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(self._static_total_songs, rect)

# ============================================================================ 
# SECTION 7: VLC PLAYBACK ENGINE
# ============================================================================ 

class PlaybackEngine:
    """Manages VLC playback of songs from paid and random playlists"""

    def __init__(self, song_list: list[dict], paid_playlist_path: str, random_music_enabled: bool = True) -> None:
        """Initialize playback engine

        Args:
            song_list: Full list of songs
            paid_playlist_path: Path to PaidMusicPlayList.txt
            random_music_enabled: Boolean - whether random music should play (default True)
        """
        self.song_list = song_list
        self.paid_playlist_path = paid_playlist_path
        self.random_music_enabled = random_music_enabled
        # Initialize VLC with audio compressor and normalizer filters
        # Compressor fixes fluctuations WITHIN songs (quiet parts louder, loud parts softer)
        # Normalizer fixes volume differences BETWEEN songs (1950s vs 2020s mastering)
        self.vlc_instance = vlc.Instance(
            '--quiet',
            '--no-video',
            '--audio-filter=compressor:normvol',  # Enable both filters
            '--compressor-rms-peak=0.0',          # RMS sensing (smoother)
            '--compressor-attack=25.0',           # 25ms attack (catches peaks)
            '--compressor-release=200.0',         # 200ms release (sustains volume)
            '--compressor-threshold=-20.0',       # Start compressing at -20dB
            '--compressor-ratio=4.0',             # 4:1 compression ratio (radio style)
            '--compressor-knee=5.0',              # Soft knee for smooth transition
            '--compressor-makeup-gain=10.0',      # Boost overall volume after compression
            '--norm-max-level=1.6',               # Normalizer target level
            '--norm-buff-size=20'                 # Normalizer buffer size
        )
        self.player = self.vlc_instance.media_player_new()
        self.current_song_index = None
        self.paid_playlist = []
        self.random_playlist = deque()
        self.upcoming_song_list = []  # Display strings for upcoming songs
        self.is_paid_song = False  # Track if current song is paid or random

        # Genre filter flags
        self.genre0 = 'null'
        self.genre1 = 'null'
        self.genre2 = 'null'
        self.genre3 = 'null'

        # Year range filter settings
        self.year_range_enabled = False
        self.year_range_start = 1967
        self.year_range_end = 1967

    def load_paid_playlist(self) -> None:
        """Load paid playlist from file"""
        try:
            if os.path.exists(self.paid_playlist_path):
                with open(self.paid_playlist_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.paid_playlist = json.loads(content)
                    else:
                        self.paid_playlist = []
            else:
                self.paid_playlist = []
        except Exception as e:
            print(f"Error loading paid playlist: {e}")
            self.paid_playlist = []

    def save_paid_playlist(self) -> None:
        """Save paid playlist to file"""
        try:
            with open(self.paid_playlist_path, 'w') as f:
                json.dump(self.paid_playlist, f)
        except Exception as e:
            print(f"Error saving paid playlist: {e}")

    def load_genre_flags(self) -> None:
        """Load genre filter flags from user_config.txt

        Reads the genre flags from user_config.txt and sets the 4 genre filter slots.
        If file doesn't exist or is invalid, defaults to 'null' for all slots.
        """
        try:
            if os.path.exists('user_config.txt'):
                with open('user_config.txt', 'r') as f:
                    config = json.load(f)
                    if isinstance(config, dict) and 'genre_flags' in config:
                        genre_list = config['genre_flags']
                        self.genre0 = genre_list[0] if len(genre_list) > 0 else 'null'
                        self.genre1 = genre_list[1] if len(genre_list) > 1 else 'null'
                        self.genre2 = genre_list[2] if len(genre_list) > 2 else 'null'
                        self.genre3 = genre_list[3] if len(genre_list) > 3 else 'null'
                    else:
                        # No genre_flags field, use defaults
                        self.genre0 = self.genre1 = self.genre2 = self.genre3 = 'null'

                # Print genre filter status
                print("\n[GENRE FILTERS]")
                if self.genre0 != 'null':
                    print(f"  Genre 0: {self.genre0}")
                if self.genre1 != 'null':
                    print(f"  Genre 1: {self.genre1}")
                if self.genre2 != 'null':
                    print(f"  Genre 2: {self.genre2}")
                if self.genre3 != 'null':
                    print(f"  Genre 3: {self.genre3}")
                if (self.genre0 == 'null' and self.genre1 == 'null' and
                    self.genre2 == 'null' and self.genre3 == 'null'):
                    print("  No genre filters set - playing all songs")
            else:
                # File doesn't exist, use defaults
                self.genre0 = self.genre1 = self.genre2 = self.genre3 = 'null'
                print("[GENRE FILTERS] No genre filters set - playing all songs")
        except Exception as e:
            print(f"[ERROR] Failed to load genre flags: {e}")
            self.genre0 = self.genre1 = self.genre2 = self.genre3 = 'null'

    def set_random_music_enabled(self, enabled: bool) -> None:
        """Update the random music enabled setting

        Args:
            enabled: Boolean - True to enable random music, False to disable
        """
        self.random_music_enabled = enabled
        print(f"[PLAYBACK] Random music {'enabled' if enabled else 'disabled'}")

        # If random music is now disabled and we're currently playing a random song,
        # don't interrupt it - just prevent future random songs from playing
        if not enabled:
            print("[PLAYBACK] Random music will stop after current song (if random)")

    def generate_random_playlist(self) -> None:
        """Generate random playlist from all songs (respects genre filters, year range, skips 'norandom')"""
        # Load current genre filter settings
        self.load_genre_flags()

        playlist_build = []

        for index, song in enumerate(self.song_list):
            # Skip songs marked with 'norandom' in comment field
            if 'norandom' in song.get('comment', '').lower():
                continue

            # Apply year range filter if enabled
            if self.year_range_enabled:
                year_str = song.get('year', '')
                if year_str and year_str.isdigit():
                    year = int(year_str)
                    # Skip songs outside the year range
                    if year < self.year_range_start or year > self.year_range_end:
                        continue
                else:
                    # Skip songs without valid year data when year filter is active
                    continue

            # Apply genre filters
            # If no genre filters are set, add all songs (that passed year filter)
            if (self.genre0 == "null" and self.genre1 == "null" and
                self.genre2 == "null" and self.genre3 == "null"):
                playlist_build.append(index)
            else:
                # Add songs matching any of the genre filters
                comment = song.get('comment', '')
                if (self.genre0 != "null" and self.genre0 in comment) or \
                   (self.genre1 != "null" and self.genre1 in comment) or \
                   (self.genre2 != "null" and self.genre2 in comment) or \
                   (self.genre3 != "null" and self.genre3 in comment):
                    playlist_build.append(index)

        # Shuffle then convert to deque for O(1) popleft
        random.shuffle(playlist_build)
        self.random_playlist = deque(playlist_build)
        print(f"[RANDOM PLAYLIST] Generated {len(self.random_playlist)} songs")
        if len(self.random_playlist) == 0:
            print("[WARNING] No songs match the current genre filters!")

        # Log random playlist generation with active genres

        now = datetime.now().replace(microsecond=0)
        log_date = now.strftime("%Y-%m-%d")
        log_time = now.strftime("%H:%M:%S")

        # Build genre list for log entry
        active_genres = []
        if self.genre0 != "null":
            active_genres.append(self.genre0)
        if self.genre1 != "null":
            active_genres.append(self.genre1)
        if self.genre2 != "null":
            active_genres.append(self.genre2)
        if self.genre3 != "null":
            active_genres.append(self.genre3)

        # If no genres set, log "all genres"
        if not active_genres:
            genre_text = "all genres"
        else:
            genre_text = ", ".join(active_genres)

        # Build year range text for log
        if self.year_range_enabled:
            year_text = f", years: {self.year_range_start}-{self.year_range_end}"
        else:
            year_text = ""

        try:
            with open(LOG_FILE_PATH, 'a') as log:
                log.write(f'\n{log_date}, {log_time}, Random playlist generated with genres: {genre_text}{year_text}')
        except IOError as log_error:
            print(f"[ERROR] Failed to write to log.txt: {log_error}")

    def update(self) -> None:
        """Update playback state - called every frame"""
        # Check if current song finished or errored
        vlc_state = self.player.get_state()
        if vlc_state == vlc.State.Ended or vlc_state == vlc.State.Error:
            if vlc_state == vlc.State.Error:
                print("[ERROR] VLC playback error - skipping to next song")
            else:
                print("Song finished")

            # If this was a paid song, remove it from playlist AFTER playback completes
            if self.is_paid_song:
                print("Removing completed paid song from playlist")
                # Re-read file to capture any songs added during playback (0.82.8 bug fix)
                self.load_paid_playlist()

                # Remove first song (the one that just finished)
                if len(self.paid_playlist) > 0:
                    self.paid_playlist.pop(0)
                    self.save_paid_playlist()
                    print(f"Paid playlist now has {len(self.paid_playlist)} songs")

                # Note: upcoming_song_list is already updated when song started playing

            # Now play next song
            print("Loading next song")
            self.play_next_song()

    def play_next_song(self) -> None:
        """Play next song - paid songs first, then random songs.
        Uses a loop (max 50 retries) instead of recursion to skip invalid entries safely."""
        for _retry in range(50):
            # Reload paid playlist to capture any new additions
            self.load_paid_playlist()

            # Priority 1: Play paid songs first
            if len(self.paid_playlist) > 0:
                song_index = self.paid_playlist[0]

                if song_index < len(self.song_list):
                    song = self.song_list[song_index]
                    song_path = song['location']

                    print(f"Playing PAID: {song['title']} by {song['artist']}")
                    print(f"Path: {song_path}")

                    # Write CurrentSongPlaying.txt before playing
                    try:
                        with open(CURRENT_SONG_PLAYING_PATH, 'w') as f:
                            f.write(song_path)
                    except Exception as e:
                        print(f"Error writing CurrentSongPlaying.txt: {e}")

                    # Release old media to prevent handle/memory leak over long sessions
                    old_media = self.player.get_media()
                    if old_media:
                        old_media.release()

                    # Create media and play
                    media = self.vlc_instance.media_new(song_path)
                    self.player.set_media(media)
                    self.player.play()

                    self.current_song_index = song_index
                    self.is_paid_song = True

                    # Log paid song play
    
                    now = datetime.now().replace(microsecond=0)
                    log_date = now.strftime("%Y-%m-%d")
                    log_time = now.strftime("%H:%M:%S")
                    try:
                        with open(LOG_FILE_PATH, 'a') as log:
                            log.write(f'\n{log_date}, {log_time}, {song["title"]}, {song["artist"]}, Paid')
                    except IOError as log_error:
                        print(f"[ERROR] Failed to write to log.txt: {log_error}")

                    # Remove from upcoming display list (song is now playing, not upcoming)
                    if len(self.upcoming_song_list) > 0:
                        # Check if this song matches the first upcoming entry
                        expected_str = f"{song['title']} - {song['artist']}"
                        if self.upcoming_song_list[0] == expected_str:
                            self.upcoming_song_list.pop(0)
                            print(f"Removed from upcoming list. {len(self.upcoming_song_list)} songs remaining in queue")

                    # DO NOT remove from paid playlist here - will be removed after song completes
                    return  # Song is now playing
                else:
                    print(f"Invalid paid song index: {song_index}")
                    # Remove invalid entry immediately
                    self.paid_playlist.pop(0)
                    self.save_paid_playlist()
                    # Loop back to try next song (avoids recursion)
                    continue

            # Priority 2: Play random songs if no paid songs AND random music is enabled
            elif self.random_music_enabled and len(self.random_playlist) > 0:
                song_index = self.random_playlist[0]

                if song_index < len(self.song_list):
                    song = self.song_list[song_index]
                    song_path = song['location']

                    print(f"Playing RANDOM: {song['title']} by {song['artist']}")
                    print(f"Path: {song_path}")

                    # Write CurrentSongPlaying.txt before playing
                    try:
                        with open(CURRENT_SONG_PLAYING_PATH, 'w') as f:
                            f.write(song_path)
                    except Exception as e:
                        print(f"Error writing CurrentSongPlaying.txt: {e}")

                    # Release old media to prevent handle/memory leak over long sessions
                    old_media = self.player.get_media()
                    if old_media:
                        old_media.release()

                    # Create media and play
                    media = self.vlc_instance.media_new(song_path)
                    self.player.set_media(media)
                    self.player.play()

                    self.current_song_index = song_index
                    self.is_paid_song = False

                    # Log random song play
    
                    now = datetime.now().replace(microsecond=0)
                    log_date = now.strftime("%Y-%m-%d")
                    log_time = now.strftime("%H:%M:%S")
                    try:
                        with open(LOG_FILE_PATH, 'a') as log:
                            log.write(f'\n{log_date}, {log_time}, {song["title"]}, {song["artist"]}, Random')
                    except IOError as log_error:
                        print(f"[ERROR] Failed to write to log.txt: {log_error}")

                    # Remove from random playlist (move to end for continuous play)
                    self.random_playlist.popleft()
                    self.random_playlist.append(song_index)  # Add to end for rotation
                    return  # Song is now playing
                else:
                    print(f"Invalid random song index: {song_index}")
                    # Remove invalid entry
                    self.random_playlist.popleft()
                    # Loop back to try next song (avoids recursion)
                    continue

            else:
                # No paid songs and either no random playlist or random music disabled
                if self.random_music_enabled:
                    print("No songs available (regenerating random playlist)")
                    self.generate_random_playlist()
                    if len(self.random_playlist) > 0:
                        continue  # Retry with regenerated playlist
                    else:
                        print("[PLAYBACK] Random playlist regenerated empty - jukebox silent")
                        return
                else:
                    print("[PLAYBACK] No paid songs and random music is disabled - jukebox silent")
                    return

        # Exhausted retries (50 consecutive invalid entries)
        print("[ERROR] play_next_song: exceeded 50 retries skipping invalid entries")

    def get_time_remaining(self) -> Optional[float]:
        """Get time remaining in current song

        Returns:
            float: Seconds remaining or None if not playing
        """
        if self.player.is_playing():
            current_time_ms = self.player.get_time()
            duration_ms = self.player.get_length()

            if current_time_ms >= 0 and duration_ms > 0:
                elapsed_seconds = current_time_ms / 1000.0
                total_seconds = duration_ms / 1000.0
                return total_seconds - elapsed_seconds

        return None

    def get_upcoming_songs(self) -> list[str]:
        """Get list of upcoming song display strings

        Returns:
            list: Formatted strings (title - artist) for upcoming songs
        """
        return self.upcoming_song_list.copy()

# ============================================================================ 
# SECTION 8: FILE INITIALIZATION
# ============================================================================ 

def setup_files() -> None:
    """
    Check for required files on disk. If they don't exist, create them with default content.

    This function ensures all necessary data files exist before the jukebox starts.
    Creates 7 files if missing:
    - user_config.txt: User configuration settings (access code, random music, credits, year range, genre flags)
    - log.txt: Playback and error logging
    - MusicMasterSongListCheck.txt: Song list change tracking
    - PaidMusicPlayList.txt: Queue of user-selected paid songs
    - YearRangeLabelList.txt: Year range to record label mapping
    - RecordLabelAssignList.txt: Artist to record label assignments
    - FullYearRangeLabelList.txt: Complete year range label data
    """


    # Get current timestamp for log file
    now = datetime.now().replace(microsecond=0)
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S")

    # Setup log file
    try:
        if not os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, 'w') as log:
                log.write(f"{log_date}, {log_time}, Jukebox Program Started For The Day")
            print(f"[INIT] Created log file: {LOG_FILE_PATH}")
        else:
            with open(LOG_FILE_PATH, 'a') as log:
                log.write(f'\n{log_date}, {log_time}, Jukebox Program Started For The Day')
    except IOError as e:
        print(f"[ERROR] Failed to setup log.txt: {e}")

    # Setup user_config.txt with all default settings
    try:
        if not os.path.exists('user_config.txt'):
            default_config = {
                "access_code": ['7', '7', '7', '7'],
                "random_music_enabled": True,
                "credits_enabled": True,
                "year_range_enabled": False,
                "year_range_start": 1967,
                "year_range_end": 1967,
                "genre_flags": ['null', 'null', 'null', 'null'],
                "popup_animation_enabled": True
            }
            with open('user_config.txt', 'w') as config_file:
                json.dump(default_config, config_file, indent=2)
            print(f"[INIT] Created user_config.txt with default settings")
    except (IOError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to setup user_config.txt: {e}")

    # Setup music master song list check file
    try:
        if not os.path.exists(MUSIC_MASTER_SONG_LIST_CHECK_PATH):
            with open(MUSIC_MASTER_SONG_LIST_CHECK_PATH, 'w') as check_file:
                json.dump([], check_file)
            print(f"[INIT] Created song list check file: {MUSIC_MASTER_SONG_LIST_CHECK_PATH}")
    except (IOError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to setup MusicMasterSongListCheck.txt: {e}")

    # Setup paid music playlist file
    try:
        if not os.path.exists(PAID_MUSIC_PLAYLIST_PATH):
            with open(PAID_MUSIC_PLAYLIST_PATH, 'w') as paid_list_file:
                json.dump([], paid_list_file)
            print(f"[INIT] Created paid playlist file: {PAID_MUSIC_PLAYLIST_PATH}")
    except (IOError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to setup PaidMusicPlayList.txt: {e}")

    # Setup year range label list file
    try:
        if not os.path.exists(YEAR_RANGE_LABEL_LIST_PATH):
            with open(YEAR_RANGE_LABEL_LIST_PATH, 'w') as year_range_file:
                year_range_file.write('[]')
            print(f"[INIT] Created year range label list file: {YEAR_RANGE_LABEL_LIST_PATH}")
    except IOError as e:
        print(f"[ERROR] Failed to setup YearRangeLabelList.txt: {e}")

    # Setup record label assign list file
    try:
        if not os.path.exists(RECORD_LABEL_ASSIGN_LIST_PATH):
            with open(RECORD_LABEL_ASSIGN_LIST_PATH, 'w') as label_assign_file:
                label_assign_file.write('[]')
            print(f"[INIT] Created record label assign list file: {RECORD_LABEL_ASSIGN_LIST_PATH}")
    except IOError as e:
        print(f"[ERROR] Failed to setup RecordLabelAssignList.txt: {e}")

    # Setup full year range label list file
    try:
        if not os.path.exists(FULL_YEAR_RANGE_LABEL_LIST_PATH):
            with open(FULL_YEAR_RANGE_LABEL_LIST_PATH, 'w') as full_year_range_file:
                full_year_range_file.write('[]')
            print(f"[INIT] Created full year range label list file: {FULL_YEAR_RANGE_LABEL_LIST_PATH}")
    except IOError as e:
        print(f"[ERROR] Failed to setup FullYearRangeLabelList.txt: {e}")

def load_access_code() -> list[str]:
    """
    Load operator access code from user_config.txt (JSON format).

    Returns:
        List of strings representing the access code (e.g., ['2', '1', '2', '4'])
        Returns default ['7', '7', '7', '7'] if file doesn't exist or is invalid
    """
    try:
        if os.path.exists('user_config.txt'):
            with open('user_config.txt', 'r') as f:
                content = f.read().strip()

                # Try to parse as JSON first
                try:
                    config = json.loads(content)
                    if isinstance(config, dict) and 'access_code' in config:
                        code = config['access_code']
                        if len(code) == 4 and all(d in '1234567' for d in code):
                            print(f"[INIT] Loaded access code from user_config.txt (JSON)")
                            return code
                        else:
                            print(f"[WARNING] Invalid access code in JSON, using default")
                            return ['7', '7', '7', '7']
                except json.JSONDecodeError:
                    # Backward compatibility: Try old CSV format
                    print(f"[INIT] Detected old CSV format, converting to JSON")
                    code = [digit.strip() for digit in content.split(',')]
                    if len(code) == 4 and all(d in '1234567' for d in code):
                        # Convert to JSON format
                        config = {
                            "access_code": code,
                            "random_music_enabled": True,  # Default to True
                            "credits_enabled": True,  # Default to True
                            "year_range_enabled": False,  # Default to False
                            "year_range_start": 1967,  # Default to 1967
                            "year_range_end": 1967,  # Default to 1967
                            "genre_flags": ['null', 'null', 'null', 'null']  # Default to no filters
                        }
                        with open('user_config.txt', 'w') as f_write:
                            json.dump(config, f_write, indent=2)
                        print(f"[INIT] Converted CSV to JSON format")
                        return code
                    else:
                        print(f"[WARNING] Invalid CSV access code, using default")
                        return ['7', '7', '7', '7']
        else:
            print(f"[INIT] user_config.txt not found, creating with defaults")
            # Create file with default config
            config = {
                "access_code": ['7', '7', '7', '7'],
                "random_music_enabled": True,
                "credits_enabled": True,
                "year_range_enabled": False,
                "year_range_start": 1967,
                "year_range_end": 1967,
                "genre_flags": ['null', 'null', 'null', 'null']
            }
            with open('user_config.txt', 'w') as f:
                json.dump(config, f, indent=2)
            return ['7', '7', '7', '7']
    except Exception as e:
        print(f"[ERROR] Failed to load access code: {e}, using default")
        return ['7', '7', '7', '7']

def save_access_code(code: list[str]) -> bool:
    """
    Save operator access code to user_config.txt (JSON format).
    Preserves other settings like random_music_enabled and credits_enabled.

    Args:
        code: List of strings representing the access code (e.g., ['2', '1', '2', '4'])

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Validate code
        if len(code) != 4 or not all(d in '1234567' for d in code):
            print(f"[ERROR] Invalid access code format")
            return False

        # Load existing config to preserve other settings
        config = {
            "access_code": code,
            "random_music_enabled": True,  # Default
            "credits_enabled": True,  # Default
            "year_range_enabled": False,  # Default
            "year_range_start": 1967,  # Default
            "year_range_end": 1967,  # Default
            "genre_flags": ['null', 'null', 'null', 'null']  # Default
        }

        if os.path.exists('user_config.txt'):
            try:
                with open('user_config.txt', 'r') as f:
                    existing_config = json.load(f)
                    # Preserve random_music_enabled if it exists
                    if 'random_music_enabled' in existing_config:
                        config['random_music_enabled'] = existing_config['random_music_enabled']
                    # Preserve credits_enabled if it exists
                    if 'credits_enabled' in existing_config:
                        config['credits_enabled'] = existing_config['credits_enabled']
                    # Preserve year_range settings if they exist
                    if 'year_range_enabled' in existing_config:
                        config['year_range_enabled'] = existing_config['year_range_enabled']
                    if 'year_range_start' in existing_config:
                        config['year_range_start'] = existing_config['year_range_start']
                    if 'year_range_end' in existing_config:
                        config['year_range_end'] = existing_config['year_range_end']
                    # Preserve genre_flags if they exist
                    if 'genre_flags' in existing_config:
                        config['genre_flags'] = existing_config['genre_flags']
            except (json.JSONDecodeError, IOError):
                # If file is corrupt, use defaults
                pass

        # Save as JSON
        with open('user_config.txt', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[SAVE] Access code saved to user_config.txt")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save access code: {e}")
        return False

def load_random_music_setting() -> bool:
    """
    Load random music enabled setting from user_config.txt (JSON format).

    Returns:
        bool: True if random music enabled, False otherwise
        Returns default True if file doesn't exist or is invalid
    """
    try:
        if os.path.exists('user_config.txt'):
            with open('user_config.txt', 'r') as f:
                content = f.read().strip()

                try:
                    config = json.loads(content)
                    if isinstance(config, dict) and 'random_music_enabled' in config:
                        enabled = config['random_music_enabled']
                        print(f"[INIT] Random music enabled: {enabled}")
                        return enabled
                    else:
                        print(f"[INIT] random_music_enabled not found, using default (True)")
                        return True
                except json.JSONDecodeError:
                    print(f"[INIT] Invalid JSON in user_config.txt, using default random music (True)")
                    return True
        else:
            print(f"[INIT] user_config.txt not found, random music default (True)")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to load random music setting: {e}, using default (True)")
        return True

def save_random_music_setting(enabled: bool) -> bool:
    """
    Save random music enabled setting to user_config.txt (JSON format).
    Preserves other settings like access_code and credits_enabled.

    Args:
        enabled: Boolean - True if random music should be enabled, False otherwise

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Load existing config to preserve other settings
        config = {
            "access_code": ['7', '7', '7', '7'],  # Default
            "random_music_enabled": enabled,
            "credits_enabled": True,  # Default
            "year_range_enabled": False,  # Default
            "year_range_start": 1967,  # Default
            "year_range_end": 1967,  # Default
            "genre_flags": ['null', 'null', 'null', 'null']  # Default
        }

        if os.path.exists('user_config.txt'):
            try:
                with open('user_config.txt', 'r') as f:
                    existing_config = json.load(f)
                    # Preserve access_code if it exists
                    if 'access_code' in existing_config:
                        config['access_code'] = existing_config['access_code']
                    # Preserve credits_enabled if it exists
                    if 'credits_enabled' in existing_config:
                        config['credits_enabled'] = existing_config['credits_enabled']
                    # Preserve year_range settings if they exist
                    if 'year_range_enabled' in existing_config:
                        config['year_range_enabled'] = existing_config['year_range_enabled']
                    if 'year_range_start' in existing_config:
                        config['year_range_start'] = existing_config['year_range_start']
                    if 'year_range_end' in existing_config:
                        config['year_range_end'] = existing_config['year_range_end']
                    # Preserve genre_flags if they exist
                    if 'genre_flags' in existing_config:
                        config['genre_flags'] = existing_config['genre_flags']
            except (json.JSONDecodeError, IOError):
                # If file is corrupt, use defaults
                pass

        # Save as JSON
        with open('user_config.txt', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[SAVE] Random music setting saved: {enabled}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save random music setting: {e}")
        return False

def load_credits_enabled() -> bool:
    """
    Load credits enabled setting from user_config.txt (JSON format).

    Returns:
        bool: True if credits are required, False for free play mode
        Returns default True if file doesn't exist or is invalid
    """
    try:
        if os.path.exists('user_config.txt'):
            with open('user_config.txt', 'r') as f:
                content = f.read().strip()

                try:
                    config = json.loads(content)
                    if isinstance(config, dict) and 'credits_enabled' in config:
                        enabled = config['credits_enabled']
                        print(f"[INIT] Credits enabled: {enabled}")
                        return enabled
                    else:
                        print(f"[INIT] credits_enabled not found, using default (True)")
                        return True
                except json.JSONDecodeError:
                    print(f"[INIT] Invalid JSON in user_config.txt, using default credits (True)")
                    return True
        else:
            print(f"[INIT] user_config.txt not found, credits default (True)")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to load credits setting: {e}, using default (True)")
        return True

def save_credits_enabled(enabled: bool) -> bool:
    """
    Save credits enabled setting to user_config.txt (JSON format).
    Preserves other settings like access_code and random_music_enabled.

    Args:
        enabled: Boolean - True if credits are required, False for free play mode

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Load existing config to preserve other settings
        config = {
            "access_code": ['7', '7', '7', '7'],  # Default
            "random_music_enabled": True,  # Default
            "credits_enabled": enabled,
            "year_range_enabled": False,  # Default
            "year_range_start": 1967,  # Default
            "year_range_end": 1967,  # Default
            "genre_flags": ['null', 'null', 'null', 'null']  # Default
        }

        if os.path.exists('user_config.txt'):
            try:
                with open('user_config.txt', 'r') as f:
                    existing_config = json.load(f)
                    # Preserve access_code if it exists
                    if 'access_code' in existing_config:
                        config['access_code'] = existing_config['access_code']
                    # Preserve random_music_enabled if it exists
                    if 'random_music_enabled' in existing_config:
                        config['random_music_enabled'] = existing_config['random_music_enabled']
                    # Preserve year_range settings if they exist
                    if 'year_range_enabled' in existing_config:
                        config['year_range_enabled'] = existing_config['year_range_enabled']
                    if 'year_range_start' in existing_config:
                        config['year_range_start'] = existing_config['year_range_start']
                    if 'year_range_end' in existing_config:
                        config['year_range_end'] = existing_config['year_range_end']
                    # Preserve genre_flags if they exist
                    if 'genre_flags' in existing_config:
                        config['genre_flags'] = existing_config['genre_flags']
            except (json.JSONDecodeError, IOError):
                # If file is corrupt, use defaults
                pass

        # Save as JSON
        with open('user_config.txt', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[SAVE] Credits enabled setting saved: {enabled}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save credits enabled setting: {e}")
        return False

def load_popup_animation_setting() -> bool:
    """
    Load popup animation enabled setting from user_config.txt (JSON format).

    Returns:
        bool: True if 45 RPM animation is enabled, False otherwise
        Returns default True if file doesn't exist or is invalid
    """
    try:
        if os.path.exists('user_config.txt'):
            with open('user_config.txt', 'r') as f:
                content = f.read().strip()

                try:
                    config = json.loads(content)
                    if isinstance(config, dict) and 'popup_animation_enabled' in config:
                        enabled = config['popup_animation_enabled']
                        print(f"[INIT] Popup animation enabled: {enabled}")
                        return enabled
                    else:
                        print(f"[INIT] popup_animation_enabled not found, using default (True)")
                        return True
                except json.JSONDecodeError:
                    print(f"[INIT] Invalid JSON in user_config.txt, using default popup animation (True)")
                    return True
        else:
            print(f"[INIT] user_config.txt not found, popup animation default (True)")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to load popup animation setting: {e}, using default (True)")
        return True

def save_popup_animation_setting(enabled: bool) -> bool:
    """
    Save popup animation enabled setting to user_config.txt (JSON format).
    Preserves other settings.

    Args:
        enabled: Boolean - True if 45 RPM animation is enabled, False to disable

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Load existing config to preserve other settings
        config = {
            "access_code": ['7', '7', '7', '7'],
            "random_music_enabled": True,
            "credits_enabled": True,
            "year_range_enabled": False,
            "year_range_start": 1967,
            "year_range_end": 1967,
            "genre_flags": ['null', 'null', 'null', 'null'],
            "popup_animation_enabled": enabled
        }

        if os.path.exists('user_config.txt'):
            try:
                with open('user_config.txt', 'r') as f:
                    existing_config = json.load(f)
                    if 'access_code' in existing_config:
                        config['access_code'] = existing_config['access_code']
                    if 'random_music_enabled' in existing_config:
                        config['random_music_enabled'] = existing_config['random_music_enabled']
                    if 'credits_enabled' in existing_config:
                        config['credits_enabled'] = existing_config['credits_enabled']
                    if 'year_range_enabled' in existing_config:
                        config['year_range_enabled'] = existing_config['year_range_enabled']
                    if 'year_range_start' in existing_config:
                        config['year_range_start'] = existing_config['year_range_start']
                    if 'year_range_end' in existing_config:
                        config['year_range_end'] = existing_config['year_range_end']
                    if 'genre_flags' in existing_config:
                        config['genre_flags'] = existing_config['genre_flags']
            except (json.JSONDecodeError, IOError):
                pass

        # Save as JSON
        with open('user_config.txt', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[SAVE] Popup animation setting saved: {enabled}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save popup animation setting: {e}")
        return False

def load_year_range_settings() -> tuple[bool, int, int]:
    """
    Load year range settings from user_config.txt (JSON format).

    Returns:
        tuple: (year_range_enabled, start_year, end_year)
        Returns default (False, 1967, 1967) if file doesn't exist or is invalid
    """
    try:
        if os.path.exists('user_config.txt'):
            with open('user_config.txt', 'r') as f:
                content = f.read().strip()

                try:
                    config = json.loads(content)
                    if isinstance(config, dict):
                        enabled = config.get('year_range_enabled', False)
                        start_year = config.get('year_range_start', 1967)
                        end_year = config.get('year_range_end', 1967)
                        print(f"[INIT] Year range settings: enabled={enabled}, start={start_year}, end={end_year}")
                        return (enabled, start_year, end_year)
                    else:
                        print(f"[INIT] year_range settings not found, using defaults")
                        return (False, 1967, 1967)
                except json.JSONDecodeError:
                    print(f"[INIT] Invalid JSON in user_config.txt, using default year range")
                    return (False, 1967, 1967)
        else:
            print(f"[INIT] user_config.txt not found, year range defaults")
            return (False, 1967, 1967)
    except Exception as e:
        print(f"[ERROR] Failed to load year range settings: {e}, using defaults")
        return (False, 1967, 1967)

def save_year_range_settings(enabled: bool, start_year: int, end_year: int) -> bool:
    """
    Save year range settings to user_config.txt (JSON format).
    Preserves other settings like access_code, random_music_enabled, and credits_enabled.

    Args:
        enabled: Boolean - True if year range filter is active, False otherwise
        start_year: Integer - Starting year of range
        end_year: Integer - Ending year of range

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Validate inputs
        if not isinstance(start_year, int) or not isinstance(end_year, int):
            print(f"[ERROR] Invalid year range types")
            return False

        if start_year > end_year:
            print(f"[ERROR] Start year must be <= end year")
            return False

        # Load existing config to preserve other settings
        config = {
            "access_code": ['7', '7', '7', '7'],  # Default
            "random_music_enabled": True,  # Default
            "credits_enabled": True,  # Default
            "year_range_enabled": enabled,
            "year_range_start": start_year,
            "year_range_end": end_year,
            "genre_flags": ['null', 'null', 'null', 'null']  # Default
        }

        if os.path.exists('user_config.txt'):
            try:
                with open('user_config.txt', 'r') as f:
                    existing_config = json.load(f)
                    # Preserve existing settings
                    if 'access_code' in existing_config:
                        config['access_code'] = existing_config['access_code']
                    if 'random_music_enabled' in existing_config:
                        config['random_music_enabled'] = existing_config['random_music_enabled']
                    if 'credits_enabled' in existing_config:
                        config['credits_enabled'] = existing_config['credits_enabled']
                    if 'genre_flags' in existing_config:
                        config['genre_flags'] = existing_config['genre_flags']
            except (json.JSONDecodeError, IOError):
                # If file is corrupt, use defaults
                pass

        # Save as JSON
        with open('user_config.txt', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[SAVE] Year range settings saved: enabled={enabled}, start={start_year}, end={end_year}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save year range settings: {e}")
        return False

def save_genre_flags(genre_flags: list[str]) -> bool:
    """
    Save genre filter flags to user_config.txt (JSON format).
    Preserves other settings like access_code, random_music_enabled, credits_enabled, and year_range settings.

    Args:
        genre_flags: List of 4 strings representing genre filters (e.g., ['rock', 'null', 'null', 'null'])

    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # Validate input
        if not isinstance(genre_flags, list) or len(genre_flags) != 4:
            print(f"[ERROR] Invalid genre_flags format - must be list of 4 strings")
            return False

        # Load existing config to preserve other settings
        config = {
            "access_code": ['7', '7', '7', '7'],  # Default
            "random_music_enabled": True,  # Default
            "credits_enabled": True,  # Default
            "year_range_enabled": False,  # Default
            "year_range_start": 1967,  # Default
            "year_range_end": 1967,  # Default
            "genre_flags": genre_flags
        }

        if os.path.exists('user_config.txt'):
            try:
                with open('user_config.txt', 'r') as f:
                    existing_config = json.load(f)
                    # Preserve existing settings
                    if 'access_code' in existing_config:
                        config['access_code'] = existing_config['access_code']
                    if 'random_music_enabled' in existing_config:
                        config['random_music_enabled'] = existing_config['random_music_enabled']
                    if 'credits_enabled' in existing_config:
                        config['credits_enabled'] = existing_config['credits_enabled']
                    if 'year_range_enabled' in existing_config:
                        config['year_range_enabled'] = existing_config['year_range_enabled']
                    if 'year_range_start' in existing_config:
                        config['year_range_start'] = existing_config['year_range_start']
                    if 'year_range_end' in existing_config:
                        config['year_range_end'] = existing_config['year_range_end']
            except (json.JSONDecodeError, IOError):
                # If file is corrupt, use defaults
                pass

        # Save as JSON
        with open('user_config.txt', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[SAVE] Genre flags saved: {genre_flags}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save genre flags: {e}")
        return False

# ============================================================================
# SECTION 8B: SONG LIST GENERATION
# ============================================================================ 

def generate_mp3_metadata(music_dir: str) -> list[tuple]:
    """
    Scan music directory and extract ID3 metadata from all MP3 files.
    Displays a threaded pygame progress bar during processing.

    Args:
        music_dir (str): Path to music directory

    Returns:
        list: List of tuples containing metadata (number, location, title, artist, album, year, comment, duration)
    """
    music_id3_metadata_list = []
    progress_bar = None

    try:
        mp3_music_files = glob.glob(os.path.join(music_dir, '*.mp3'))
    except Exception as e:
        print(f"[ERROR] Failed to search for MP3 files: {e}")
        return []

    if not mp3_music_files:
        print("[ERROR] No MP3 files found in music directory")
        return []

    print(f"\nFound {len(mp3_music_files)} MP3 files. Processing...")
    print("Please Be Patient - Regenerating Your Songlist From Scratch")
    print("Music Will Start When Finished\n")

    # Initialize and start progress bar in separate thread
    progress_bar = MetadataProgressBar(len(mp3_music_files))
    progress_bar.start()

    counter = 0

    for file_path in mp3_music_files:
        try:
            # Update progress bar with current file
            file_name = os.path.basename(file_path)
            progress_bar.update(counter, file_name)

            id3tag = TinyTag.get(file_path)

            if id3tag is None:
                print(f"[ERROR] Could not read metadata from {file_path}")
                continue

            # Convert duration to MM:SS format (matching original)
            get_song_duration_seconds = "%f" % id3tag.duration
            remove_song_duration_decimals = float(get_song_duration_seconds)
            song_duration_decimals_removed = int(remove_song_duration_decimals)
            song_duration_minutes_seconds = int(song_duration_decimals_removed)
            song_duration = time.strftime("%M:%S", time.gmtime(song_duration_minutes_seconds))

            song_metadata = (
                counter,
                file_path,
                "%s" % id3tag.title,
                "%s" % id3tag.artist,
                "%s" % id3tag.album,
                "%s" % id3tag.year,
                "%s" % id3tag.comment,
                song_duration
            )
            music_id3_metadata_list.append(song_metadata)
            counter += 1
        except Exception as e:
            print(f"[ERROR] Failed to extract metadata from {file_path}: {e}")
            continue

    # Stop progress bar and pause for 1 second
    if progress_bar:
        progress_bar.stop()
        time.sleep(1)  # Pause after progress bar closes

    if not music_id3_metadata_list:
        print("[ERROR] No valid metadata was extracted from MP3 files")
        return []

    print(f"[SUCCESS] Extracted metadata from {counter} songs")
    return music_id3_metadata_list

def generate_music_master_song_list_dictionary(music_id3_metadata_list: list[tuple], output_file: str, check_file: str) -> list[dict]:
    """
    Convert metadata tuples to dictionary format and save to files.

    Args:
        music_id3_metadata_list (list): List of metadata tuples
        output_file (str): Path to MusicMasterSongList.txt
        check_file (str): Path to MusicMasterSongListCheck.txt

    Returns:
        list: List of song dictionaries
    """
    try:
        print("\n[GENERATE] Creating Master Song List Dictionary...")

        # Assign keys for MusicMasterSongList Dictionary
        keys = ['number', 'location', 'title', 'artist', 'album', 'year', 'comment', 'duration']

        # Build MusicMasterSongList Dictionary
        music_master_song_list = [dict(zip(keys, sublst)) for sublst in music_id3_metadata_list]

        # Sort by artist (case-insensitive) for consistent alphabetical display on all platforms
        print("[SORT] Sorting songs alphabetically by artist...")
        music_master_song_list.sort(key=lambda x: x['artist'].lower())

        # Renumber songs sequentially after sorting
        for idx, song in enumerate(music_master_song_list):
            song['number'] = idx
        print(f"[SUCCESS] Songs sorted and renumbered (0-{len(music_master_song_list)-1})")

        # Save MusicMasterSongList Dictionary
        try:
            with open(output_file, 'w') as master_list_file:
                json.dump(music_master_song_list, master_list_file)
            print(f"[SUCCESS] Saved master song list to {os.path.basename(output_file)}")

            # Log new songlist generation

            now = datetime.now().replace(microsecond=0)
            log_date = now.strftime("%Y-%m-%d")
            log_time = now.strftime("%H:%M:%S")
            try:
                with open(LOG_FILE_PATH, 'a') as log:
                    log.write(f'\n{log_date}, {log_time}, New Songlist Generated')
            except IOError as log_error:
                print(f"[ERROR] Failed to write to log.txt: {log_error}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to save MusicMasterSongList.txt: {e}")
            return []

        # Create and save file list size value
        list_size = len(music_master_song_list)
        try:
            with open(check_file, 'w') as check_file_handle:
                json.dump(list_size, check_file_handle)
            print(f"[SUCCESS] Saved song list check file ({list_size} songs)")
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to save MusicMasterSongListCheck.txt: {e}")
            return []

        return music_master_song_list
    except Exception as e:
        print(f"[ERROR] Unexpected error in generate_music_master_song_list_dictionary: {e}")
        return []




# ============================================================================ 
# SECTION 9: MAIN APPLICATION
# ============================================================================ 
def main() -> None:
    """Main application entry point"""

    # Initialize required data files
    setup_files()

    # ======================================================================== 
    # SONG LIST GENERATION/LOADING - MUST HAPPEN BEFORE PYGAME INIT
    # ======================================================================== 
    # The MetadataProgressBar uses pygame in a separate thread. This must
    # complete and call pygame.quit() before main pygame.init() is called
    # to avoid pygame double-initialization crash.
    # ======================================================================== 

    # Check if song list needs generation or loading
    song_list = []

    if os.path.exists(SONG_LIST_PATH):
        print("\n[CHECK] Found existing music database")

        # Count current MP3 files in directory
        try:
            current_file_count = len(glob.glob(os.path.join(MUSIC_DIRECTORY, '*.mp3')))
            print(f"[CHECK] Current MP3 files in directory: {current_file_count}")
        except Exception as e:
            print(f"[ERROR] Failed to count MP3 files: {e}")
            current_file_count = -1

        # Load stored file count from previous run
        try:
            with open(MUSIC_MASTER_SONG_LIST_CHECK_PATH, 'r') as check_file:
                stored_file_count = json.load(check_file)
                print(f"[CHECK] Stored MP3 file count: {stored_file_count}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to load MusicMasterSongListCheck.txt: {e}")
            stored_file_count = -1

        # Check for match
        if current_file_count == stored_file_count and current_file_count != -1:
            print("[SUCCESS] Music database matches current files")
            # Try to load existing MusicMasterSongList
            try:
                with open(SONG_LIST_PATH, 'r') as master_list_file:
                    song_list = json.load(master_list_file)
                print(f"[LOADED] {len(song_list)} songs from {SONG_LIST_PATH}")

                # Log existing songlist usage

                now = datetime.now().replace(microsecond=0)
                log_date = now.strftime("%Y-%m-%d")
                log_time = now.strftime("%H:%M:%S")
                try:
                    with open(LOG_FILE_PATH, 'a') as log:
                        log.write(f'\n{log_date}, {log_time}, Using Existing Songlist')
                except IOError as log_error:
                    print(f"[ERROR] Failed to write to log.txt: {log_error}")
            except (IOError, json.JSONDecodeError) as e:
                print(f"[ERROR] Failed to load MusicMasterSongList.txt: {e}")
                print("[REGENERATE] Corrupted file - regenerating...")
                # Fall through to regeneration
        else:
            print("[REGENERATE] Music database count mismatch - regenerating")
            # Fall through to regeneration

    # If song_list is still empty, regenerate
    if not song_list:
        print("\n" + "="*60)
        print("GENERATING SONG LIST FROM MUSIC DIRECTORY")
        print("="*60)

        # Generate metadata (this will use pygame in separate thread)
        music_id3_metadata_list = generate_mp3_metadata(MUSIC_DIRECTORY)

        if music_id3_metadata_list:
            # Convert to dictionary and save
            song_list = generate_music_master_song_list_dictionary(
                music_id3_metadata_list,
                SONG_LIST_PATH,
                MUSIC_MASTER_SONG_LIST_CHECK_PATH
            )

        print("="*60)
        print(f"SONG LIST GENERATION COMPLETE: {len(song_list)} songs")
        print("="*60 + "\n")

    # Verify we have songs
    if not song_list:
        print("\n[FATAL ERROR] No songs found in music directory!")
        sys.exit(1)

    # ======================================================================== 
    # EXTRACT AND LOG AVAILABLE GENRES FROM MUSIC COLLECTION
    # ======================================================================== 
    print("\n[ANALYZE] Extracting available genres from music collection...")

    # Extract all unique individual genre tags (split comment field by spaces)
    all_genres = set()
    for song in song_list:
        comment = song.get('comment', '')
        if comment:  # Only include non-empty comments
            # Split by spaces to get individual genre tags
            genre_tags = comment.split()
            for tag in genre_tags:
                # Strip whitespace and filter empty strings
                cleaned_tag = tag.strip()
                if cleaned_tag:  # Only add non-empty tags
                    all_genres.add(cleaned_tag)

    # Sort genres alphabetically for readability
    sorted_genres = sorted(all_genres)

    # Print to console
    print(f"[GENRES] Found {len(sorted_genres)} unique genre tags:")
    for genre in sorted_genres:
        print(f"         - {genre}")

    # Log to file with timestamp

    now = datetime.now().replace(microsecond=0)
    log_date = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%H:%M:%S")

    try:
        with open(LOG_FILE_PATH, 'a') as log:
            log.write(f'\n{log_date}, {log_time}, Genres Available ({len(sorted_genres)} unique tags):\n')
            for genre in sorted_genres:
                log.write(f'{log_date}, {log_time},   - {genre}\n')
    except IOError as log_error:
        print(f"[ERROR] Failed to write genres to log.txt: {log_error}")

    print(f"[SUCCESS] Genre list logged to {LOG_FILE_PATH}\n")

    # ======================================================================== 
    # PYGAME INITIALIZATION - AFTER SONG LIST GENERATION COMPLETES
    # ======================================================================== 

    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Create window (no title bar)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Convergence Jukebox")

    # Load background image
    try:
        background = pygame.image.load(BACKGROUND_IMAGE_PATH)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for: {BACKGROUND_IMAGE_PATH}")
        pygame.quit()
        sys.exit(1)

    # Create pre-sorted lists for optimized search (binary search)
    print("Creating optimized search indices...")
    title_sorted_list = sorted(song_list, key=lambda x: x['title'].lower())

    # Extract unique artist names and sort
    all_artists = list(set(song['artist'] for song in song_list))
    artist_sorted_list = sorted(all_artists, key=lambda x: x.lower())
    print(f"Search optimization complete: {len(song_list)} songs, {len(artist_sorted_list)} unique artists")

    # Load arrow button images
    try:
        arrow_left_img = pygame.image.load(ARROW_LEFT_IMG)
        arrow_right_img = pygame.image.load(ARROW_RIGHT_IMG)
    except pygame.error as e:
        print(f"Error loading arrow images: {e}")
        pygame.quit()
        sys.exit(1)

    # Load sound effects
    try:
        buzz_sound = pygame.mixer.Sound(BUZZ_SOUND_PATH)
    except pygame.error as e:
        print(f"Error loading buzz sound: {e}")
        buzz_sound = None

    try:
        success_sound = pygame.mixer.Sound(SUCCESS_SOUND_PATH)
    except pygame.error as e:
        print(f"Error loading success sound: {e}")
        success_sound = None

    # Create button grid with song data
    try:
        button_grid = ButtonGrid(GRID_START_X, GRID_START_Y, song_list, selection_window_number=0)
    except pygame.error as e:
        print(f"Error creating button grid: {e}")
        pygame.quit()
        sys.exit(1)

    # Create control buttons
    try:
        control_buttons = ControlButtons(CONTROL_START_X, CONTROL_START_Y)
    except pygame.error as e:
        print(f"Error creating control buttons: {e}")
        pygame.quit()
        sys.exit(1)

    # Create info screen
    try:
        info_screen = InfoScreen(INFO_START_X, INFO_START_Y, song_list)
    except Exception as e:
        print(f"Error creating info screen: {e}")
        pygame.quit()
        sys.exit(1)

    # Load random music setting
    random_music_enabled = load_random_music_setting()

    # Create playback engine
    try:
        playback_engine = PlaybackEngine(song_list, PAID_MUSIC_PLAYLIST_PATH, random_music_enabled)
    except Exception as e:
        print(f"Error creating playback engine: {e}")
        pygame.quit()
        sys.exit(1)

    # Load year range settings from config
    year_range_enabled, year_range_start, year_range_end = load_year_range_settings()
    playback_engine.year_range_enabled = year_range_enabled
    playback_engine.year_range_start = year_range_start
    playback_engine.year_range_end = year_range_end

    # Initialize random playlist and start playback
    print("Generating random playlist...")
    playback_engine.generate_random_playlist()
    print("Starting music playback...")
    playback_engine.play_next_song()

    # Load "The" bands data for record image generation
    print("Loading 'The' bands data for record images...")
    the_bands_set = load_the_bands_data()

    # Initialize state variables
    selection_window_number = 0
    selection_entry_letter = None
    selection_entry_number = None
    credits = 0

    # Cache record label PNG file list (avoids os.listdir on every song selection)
    cached_label_png_files = [f for f in os.listdir(BLANK_RECORDS_DIR) if f.endswith('.png')]
    print(f"[INIT] Cached {len(cached_label_png_files)} record label PNG files")

    # Operator panel state variables
    SECRET_OPERATOR_CODE = load_access_code()  # Load from user_config.txt
    CREDITS_ENABLED = load_credits_enabled()  # Load from user_config.txt
    POPUP_ANIMATION_ENABLED = load_popup_animation_setting()  # Load from user_config.txt
    secret_code_buffer = []
    show_control_panel = False

    # Initialize popup state variables (rotating record popup)
    last_keypress_time = time.time()
    popup_active = False
    popup_record_image = None
    popup_record_surface = None
    popup_rotated_frames = None
    popup_rotation_angle = 0
    popup_tonearm = None
    popup_play_time = 0.0

    # Pre-generated frames for next popup (built in background during idle)
    prepped_rotated_frames = None
    prepped_record_image = None
    prepped_song_index = None

    # Initialize selection popup state variables
    selection_popup_active = False
    selection_popup_surface = None
    selection_popup_start_time = 0.0
    selection_popup_duration = 3.0  # 3 seconds

    # Create rectangles for arrow button click detection
    arrow_left_rect = pygame.Rect(ARROW_LEFT_X, ARROW_LEFT_Y, arrow_left_img.get_width(), arrow_left_img.get_height())
    arrow_right_rect = pygame.Rect(ARROW_RIGHT_X, ARROW_RIGHT_Y, arrow_right_img.get_width(), arrow_right_img.get_height())

    # Main loop
    clock = pygame.time.Clock()
    running = True

    print("Convergence Jukebox v0.90.41 - Add Comprehensive Logging System")
    print("Press ESC to exit")
    print("Press X to add credit")
    print("Press T for title search, Shift+A for artist search")
    print("Press A/B/C to select column, 1-7 to select song, S to confirm")
    print("Music plays continuously: paid songs → random songs → check for more paid songs...")

    while running:
        # Handle control panel display
        if show_control_panel:
            operator_action = display_operator_panel(screen, SECRET_OPERATOR_CODE)

            # Handle access code change (returns tuple)
            if isinstance(operator_action, tuple) and operator_action[0] == 'change_code':
                new_code = operator_action[1]
                if save_access_code(new_code):
                    SECRET_OPERATOR_CODE = new_code
                    print(f"Access code successfully changed and saved")
                else:
                    print(f"[ERROR] Failed to save new access code")
            elif operator_action == "Set Random Music Genres":
                print("Action: Set Random Music Genres")
                # Call genre selection screen - pass save function instead of file path
                genre_saved = select_random_music_genres(screen, song_list, save_genre_flags)
                if genre_saved:
                    print("[SUCCESS] Genre filters updated - regenerating random playlist")
                    # Reload genre flags in the playback engine
                    playback_engine.load_genre_flags()
                    # Regenerate random playlist with new genre filters
                    playback_engine.generate_random_playlist()
                else:
                    print("[CANCELLED] Genre selection cancelled")
            elif operator_action == "Turn Random Music On/Off":
                print("Action: Turn Random Music On/Off")
                # Call random music toggle screen
                current_setting = playback_engine.random_music_enabled
                new_setting = toggle_random_music(screen, current_setting)
                if new_setting is not None:
                    # User saved a new setting
                    if save_random_music_setting(new_setting):
                        playback_engine.set_random_music_enabled(new_setting)
                        print(f"[SUCCESS] Random music {'enabled' if new_setting else 'disabled'}")

                        # If enabling random music, generate playlist and start playback if idle
                        if new_setting and not current_setting:
                            print("[RANDOM MUSIC] Enabling random music - generating playlist")
                            playback_engine.generate_random_playlist()
                            # If jukebox is silent (nothing playing), start playback
                            if not playback_engine.player.is_playing():
                                print("[RANDOM MUSIC] Starting playback")
                                playback_engine.play_next_song()
                    else:
                        print("[ERROR] Failed to save random music setting")
                else:
                    print("[CANCELLED] Random music toggle cancelled")
            elif operator_action == "Turn Credits On/Off":
                print("Action: Turn Credits On/Off")
                # Call credits toggle screen
                current_setting = CREDITS_ENABLED
                new_setting = toggle_credits(screen, current_setting)
                if new_setting is not None:
                    # User saved a new setting
                    if save_credits_enabled(new_setting):
                        CREDITS_ENABLED = new_setting
                        print(f"[SUCCESS] Credits {'enabled' if new_setting else 'disabled (free play mode)'}")
                    else:
                        print("[ERROR] Failed to save credits setting")
                else:
                    print("[CANCELLED] Credits toggle cancelled")
            elif operator_action == "Select Year Range":
                print("Action: Select Year Range")
                # Call year range selection screen
                current_enabled, current_start, current_end = load_year_range_settings()
                result = select_year_range(screen, song_list, current_enabled, current_start, current_end)
                if result is not None:
                    # User saved new settings
                    new_enabled, new_start, new_end = result
                    if save_year_range_settings(new_enabled, new_start, new_end):
                        playback_engine.year_range_enabled = new_enabled
                        playback_engine.year_range_start = new_start
                        playback_engine.year_range_end = new_end
                        # Regenerate random playlist with new year range filter
                        playback_engine.generate_random_playlist()
                        print(f"[SUCCESS] Year range {'enabled' if new_enabled else 'disabled'}: {new_start}-{new_end}")
                    else:
                        print("[ERROR] Failed to save year range settings")
                else:
                    print("[CANCELLED] Year range selection cancelled")
            elif operator_action == "45 RPM Animation On/Off":
                print("Action: 45 RPM Animation On/Off")
                current_setting = POPUP_ANIMATION_ENABLED
                new_setting = toggle_popup_animation(screen, current_setting)
                if new_setting is not None:
                    if save_popup_animation_setting(new_setting):
                        POPUP_ANIMATION_ENABLED = new_setting
                        print(f"[SUCCESS] 45 RPM animation {'enabled' if new_setting else 'disabled'}")
                    else:
                        print("[ERROR] Failed to save popup animation setting")
                else:
                    print("[CANCELLED] Popup animation toggle cancelled")
            # NOTE: "More Selections" is now handled internally by operator_panel_module.py
            elif operator_action == "Return To Jukebox":
                print("Action: Return To Jukebox")
                # No action needed, just close the panel
            elif operator_action is None: # ESC was pressed
                print("Control panel closed.")
            
            show_control_panel = False # Panel always closes after a selection or exit
            continue
        # Update playback engine
        playback_engine.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Reset idle timer on ANY keypress
                last_keypress_time = time.time()

                # Close popup on ANY keypress
                if popup_active:
                    popup_active = False
                    popup_record_image = None
                    popup_record_surface = None
                    popup_rotated_frames = None
                    popup_tonearm = None
                    print("Popup closed by keypress")

                # Secret operator code entry (only when not selecting a song number)
                if selection_entry_letter is None:
                    num_map = {
                        pygame.K_0: '0', pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4',
                        pygame.K_5: '5', pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8', pygame.K_9: '9',
                        pygame.K_KP_0: '0', pygame.K_KP_1: '1', pygame.K_KP_2: '2', pygame.K_KP_3: '3', pygame.K_KP_4: '4',
                        pygame.K_KP_5: '5', pygame.K_KP_6: '6', pygame.K_KP_7: '7', pygame.K_KP_8: '8', pygame.K_KP_9: '9'
                    }
                    if event.key in num_map:
                        secret_code_buffer.append(num_map[event.key])
                        # Check if the current buffer is a valid prefix of the secret code
                        if not SECRET_OPERATOR_CODE[:len(secret_code_buffer)] == secret_code_buffer:
                            secret_code_buffer = [] # Reset on wrong key
                        # Check for a full match
                        elif len(secret_code_buffer) == len(SECRET_OPERATOR_CODE):
                            print("Correct secret code entered. Opening control panel.")
                            show_control_panel = True
                            secret_code_buffer = [] # Reset buffer after success

                if event.key == pygame.K_ESCAPE:
                    # Check if selection popup is active first
                    if selection_popup_active:
                        selection_popup_active = False
                        selection_popup_surface = None
                        print("[SELECTION POPUP] Closed by ESC key")
                    else:
                        running = False

                # Credit button
                elif event.key == pygame.K_x:
                    credits += 1
                    print(f"Credit added! Total credits: {credits}")

                    # Log quarter insertion
    
                    now = datetime.now().replace(microsecond=0)
                    log_date = now.strftime("%Y-%m-%d")
                    log_time = now.strftime("%H:%M:%S")
                    try:
                        with open(LOG_FILE_PATH, 'a') as log:
                            log.write(f'\n{log_date}, {log_time}, Quarter Inserted')
                    except IOError as log_error:
                        print(f"[ERROR] Failed to write to log.txt: {log_error}")

                # Search functions (T for title, Shift+A for artist)
                elif event.key == pygame.K_t:
                    print("Opening title search...")
                    search_result = display_search_popup(
                        "title",
                        title_sorted_list,
                        artist_sorted_list,
                        song_list
                    )
                    if search_result is not None:
                        # Update idle timer from search window's last keypress
                        if 'last_keypress_time' in search_result:
                            last_keypress_time = search_result['last_keypress_time']
                            print(f"[SEARCH] Idle timer reset from search window")

                        # Update selection window to show selected song
                        selection_window_number = search_result['song_number']
                        button_grid.update_selection_window(selection_window_number)
                        print(f"Search result: navigated to song #{search_result['song_number']}")

                        # If title search, update button grid to highlight A1
                        if search_result.get('song_selected') == 'A1':
                            selection_entry_letter = 'A'
                            selection_entry_number = 1
                            control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                            print("Song set to A1 position - ready to select with S key")

                elif event.key == pygame.K_a and (event.mod & pygame.KMOD_SHIFT):
                    print("Opening artist search...")
                    search_result = display_search_popup(
                        "artist",
                        title_sorted_list,
                        artist_sorted_list,
                        song_list
                    )
                    if search_result is not None:
                        # Update idle timer from search window's last keypress
                        if 'last_keypress_time' in search_result:
                            last_keypress_time = search_result['last_keypress_time']
                            print(f"[SEARCH] Idle timer reset from search window")

                        # Update selection window to show first song by artist
                        selection_window_number = search_result['song_number']
                        button_grid.update_selection_window(selection_window_number)
                        print(f"Artist search result: navigated to song #{search_result['song_number']}")

                # Arrow keys for navigation
                elif event.key == pygame.K_RIGHT:
                    new_window_number = selection_window_number + 21
                    if new_window_number + 20 >= len(song_list):
                        new_window_number = len(song_list) - 21
                        if buzz_sound:
                            buzz_sound.play()
                    selection_window_number = new_window_number
                    button_grid.update_selection_window(selection_window_number)

                elif event.key == pygame.K_LEFT:
                    new_window_number = selection_window_number - 21
                    if new_window_number < 0:
                        new_window_number = 0
                        if buzz_sound:
                            buzz_sound.play()
                    selection_window_number = new_window_number
                    button_grid.update_selection_window(selection_window_number)

                # Letter selection (A, B, C)
                elif event.key == pygame.K_a:
                    if selection_entry_letter is None:
                        selection_entry_letter = 'A'
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected column: A")

                elif event.key == pygame.K_b:
                    if selection_entry_letter is None:
                        selection_entry_letter = 'B'
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected column: B")

                elif event.key == pygame.K_c:
                    # Check if Shift is pressed (uppercase 'C' for CORRECT button)
                    if event.mod & pygame.KMOD_SHIFT:
                        # CORRECT button - reset selection (Shift+C)
                        selection_entry_letter = None
                        selection_entry_number = None
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print("CORRECT: Selection cleared")
                    elif selection_entry_letter is None:
                        # Column C selection (lowercase 'c')
                        selection_entry_letter = 'C'
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected column: C")

                # Number selection (1-7)
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                    if selection_entry_letter is not None and selection_entry_number is None:
                        num_map = {
                            pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4,
                            pygame.K_5: 5, pygame.K_6: 6, pygame.K_7: 7
                        }
                        selection_entry_number = num_map[event.key]
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected row: {selection_entry_number}")

                # SELECT (S key)
                elif event.key == pygame.K_s:
                    if selection_entry_letter is not None and selection_entry_number is not None:
                        if not CREDITS_ENABLED or credits > 0:  # Allow if credits disabled OR have credits
                            # Calculate song index
                            letter_offset = {'A': 0, 'B': 7, 'C': 14}[selection_entry_letter]
                            row_offset = (selection_entry_number - 1)
                            song_index = selection_window_number + letter_offset + row_offset

                            if song_index < len(song_list):
                                song = song_list[song_index]
                                print(f"Selected: {song['title']} by {song['artist']}")

                                # Add to paid playlist
                                playback_engine.load_paid_playlist()
                                playback_engine.paid_playlist.append(song_index)
                                playback_engine.save_paid_playlist()

                                # Add to upcoming display list (formatted title - artist)
                                upcoming_str = f"{song['title']} - {song['artist']}"
                                playback_engine.upcoming_song_list.append(upcoming_str)
                                print(f"Added to upcoming list: {upcoming_str}")

                                # Play success sound
                                if success_sound:
                                    success_sound.play()

                                # Generate and show selection popup
                                try:
                                    # Get available labels
                                    png_files = cached_label_png_files

                                    # Generate record label image
                                    year = song.get('year', None)
                                    # Apply "The" prefix to artist name
                                    artist_name = apply_the_prefix(
                                        song['artist'], the_bands_set
                                    )
                                    # Get song file path for ID3 extraction
                                    song_file_path = song['location']

                                    composite_path = generate_selection_record_label(
                                        song['title'],
                                        artist_name,
                                        png_files,
                                        year,
                                        song_file_path
                                    )

                                    # Activate selection popup
                                    selection_popup_active = True
                                    selection_popup_start_time = time.time()
                                    print(f"[SELECTION POPUP] Activated for 3 seconds")

                                except Exception as e:
                                    print(f"[SELECTION POPUP] Error: {e}")
                                    import traceback
                                    traceback.print_exc()

                                # If nothing playing, start playback
                                if not playback_engine.player.is_playing():
                                    playback_engine.play_next_song()

                                # Deduct credit only if credits are enabled
                                if CREDITS_ENABLED:
                                    credits -= 1
                                    print(f"Credits remaining: {credits}")

                            # Reset selection
                            selection_entry_letter = None
                            selection_entry_number = None
                            control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        else:
                            if buzz_sound:
                                buzz_sound.play()
                            print("No credits available!")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos

                    # Check arrow buttons
                    if arrow_right_rect.collidepoint(mouse_pos):
                        new_window_number = selection_window_number + 21
                        if new_window_number + 20 >= len(song_list):
                            new_window_number = len(song_list) - 21
                            if buzz_sound:
                                buzz_sound.play()
                        selection_window_number = new_window_number
                        button_grid.update_selection_window(selection_window_number)

                    elif arrow_left_rect.collidepoint(mouse_pos):
                        new_window_number = selection_window_number - 21
                        if new_window_number < 0:
                            new_window_number = 0
                            if buzz_sound:
                                buzz_sound.play()
                        selection_window_number = new_window_number
                        button_grid.update_selection_window(selection_window_number)

                    # Check control buttons
                    else:
                        clicked_key = control_buttons.handle_click(mouse_pos)
                        if clicked_key:
                            if clicked_key in ['A', 'B', 'C']:
                                if selection_entry_letter is None:
                                    selection_entry_letter = clicked_key
                                    control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                    print(f"Selected column: {clicked_key}")

                            elif clicked_key in ['1', '2', '3', '4', '5', '6', '7']:
                                if selection_entry_letter is not None and selection_entry_number is None:
                                    selection_entry_number = int(clicked_key)
                                    control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                    print(f"Selected row: {selection_entry_number}")

                            elif clicked_key == 'CORRECT':
                                selection_entry_letter = None
                                selection_entry_number = None
                                control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                print("Selection cleared")

                            elif clicked_key == 'SELECT':
                                if selection_entry_letter is not None and selection_entry_number is not None:
                                    if not CREDITS_ENABLED or credits > 0:  # Allow if credits disabled OR have credits
                                        # Calculate song index
                                        letter_offset = {'A': 0, 'B': 7, 'C': 14}[selection_entry_letter]
                                        row_offset = (selection_entry_number - 1)
                                        song_index = selection_window_number + letter_offset + row_offset

                                        if song_index < len(song_list):
                                            song = song_list[song_index]
                                            print(f"Selected: {song['title']} by {song['artist']}")

                                            # Add to paid playlist
                                            playback_engine.load_paid_playlist()
                                            playback_engine.paid_playlist.append(song_index)
                                            playback_engine.save_paid_playlist()

                                            # Add to upcoming display list (formatted title - artist)
                                            upcoming_str = f"{song['title']} - {song['artist']}"
                                            playback_engine.upcoming_song_list.append(upcoming_str)
                                            print(f"Added to upcoming list: {upcoming_str}")

                                            # Play success sound
                                            if success_sound:
                                                success_sound.play()

                                            # Generate and show selection popup
                                            try:
                                                # Use cached label file list
                                                png_files = cached_label_png_files

                                                # Generate record label image
                                                year = song.get('year', None)
                                                # Apply "The" prefix to artist name
                                                artist_name = apply_the_prefix(
                                                    song['artist'], the_bands_set
                                                )
                                                # Get song file path for ID3 extraction
                                                song_file_path = song['location']

                                                composite_path = generate_selection_record_label(
                                                    song['title'],
                                                    artist_name,
                                                    png_files,
                                                    year,
                                                    song_file_path
                                                )

                                                # Activate selection popup
                                                selection_popup_active = True
                                                selection_popup_start_time = time.time()
                                                print(f"[SELECTION POPUP] Activated for 3 seconds")

                                            except Exception as e:
                                                print(f"[SELECTION POPUP] Error: {e}")
                                                import traceback
                                                traceback.print_exc()

                                            # If nothing playing, start playback
                                            if not playback_engine.player.is_playing():
                                                playback_engine.play_next_song()

                                            # Deduct credit only if credits are enabled
                                            if CREDITS_ENABLED:
                                                credits -= 1
                                                print(f"Credits remaining: {credits}")

                                        # Reset selection
                                        selection_entry_letter = None
                                        selection_entry_number = None
                                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                                    else:
                                        if buzz_sound:
                                            buzz_sound.play()
                                        print("No credits available!")

        # Update info screen with current state
        time_remaining = playback_engine.get_time_remaining()
        upcoming = playback_engine.get_upcoming_songs()
        info_screen.update(playback_engine.current_song_index, upcoming, credits, time_remaining)

        # Pre-generate rotated frames for current song (background prep during idle)
        if (playback_engine.current_song_index is not None and
                prepped_song_index != playback_engine.current_song_index and
                not popup_active and POPUP_ANIMATION_ENABLED):
            try:
                song = song_list[playback_engine.current_song_index]
                artist_name = apply_the_prefix(song['artist'], the_bands_set)
                song_file_path = song['location']
                year = song.get('year', None)

                prep_image = generate_record_image(song['title'], artist_name, year, song_file_path)
                if prep_image and os.path.exists(prep_image):
                    pil_image = Image.open(prep_image)
                    if pil_image.mode != 'RGBA':
                        pil_image = pil_image.convert('RGBA')
                    pil_image = pil_image.resize((500, 500), Image.Resampling.LANCZOS)
                    raw_bytes = pil_image.tobytes()
                    prep_surface = pygame.image.fromstring(raw_bytes, pil_image.size, 'RGBA')
                    prepped_rotated_frames = [pygame.transform.rotozoom(prep_surface, angle * 5, 1.0) for angle in range(72)]
                    prepped_record_image = prep_image
                    prepped_song_index = playback_engine.current_song_index
                    print(f"[POPUP PREP] Pre-generated 360 rotated frames for: {song['title']}")
            except Exception as e:
                print(f"[POPUP PREP] Error pre-generating frames: {e}")

        # Rotating record popup logic
        try:
            if playback_engine.player and playback_engine.current_song_index is not None:
                # Get VLC time information
                current_time_ms = playback_engine.player.get_time()
                duration_ms = playback_engine.player.get_length()

                if current_time_ms > 0 and duration_ms > 0:
                    elapsed_seconds = current_time_ms / 1000.0
                    total_seconds = duration_ms / 1000.0
                    time_remaining_seconds = total_seconds - elapsed_seconds
                    time_since_keypress = time.time() - last_keypress_time

                    # Conditions to SHOW popup
                    should_show = (
                        POPUP_ANIMATION_ENABLED and
                        elapsed_seconds >= POPUP_MIN_PLAYBACK_TIME and
                        time_since_keypress >= POPUP_MIN_IDLE_TIME and
                        time_remaining_seconds >= POPUP_CLOSE_SECONDS_REMAINING and
                        not popup_active
                    )

                    # Conditions to CLOSE popup
                    should_close = (
                        popup_active and
                        time_remaining_seconds < POPUP_CLOSE_SECONDS_REMAINING
                    )

                    # Show popup
                    if should_show:
                        song = song_list[playback_engine.current_song_index]

                        print(f"\n=== SHOWING ROTATING RECORD POPUP ===")
                        print(f"Song: {song['title']} by {song['artist']}")
                        print(f"Elapsed: {elapsed_seconds:.1f}s, Remaining: {time_remaining_seconds:.1f}s")

                        # Use pre-generated frames if available for this song
                        if prepped_song_index == playback_engine.current_song_index and prepped_rotated_frames:
                            popup_rotated_frames = prepped_rotated_frames
                            popup_record_image = prepped_record_image
                            print("[POPUP] Using pre-generated rotated frames (zero startup cost)")
                        else:
                            # Fallback: generate on the spot if prep didn't happen
                            print("[POPUP] Fallback: generating frames on the spot")
                            year = song.get('year', None)
                            artist_name = apply_the_prefix(song['artist'], the_bands_set)
                            song_file_path = song['location']
                            popup_record_image = generate_record_image(song['title'], artist_name, year, song_file_path)

                            if popup_record_image and os.path.exists(popup_record_image):
                                pil_image = Image.open(popup_record_image)
                                if pil_image.mode != 'RGBA':
                                    pil_image = pil_image.convert('RGBA')
                                pil_image = pil_image.resize((500, 500), Image.Resampling.LANCZOS)
                                raw_bytes = pil_image.tobytes()
                                popup_record_surface = pygame.image.fromstring(raw_bytes, pil_image.size, 'RGBA')
                                popup_rotated_frames = [pygame.transform.rotozoom(popup_record_surface, angle * 5, 1.0) for angle in range(72)]

                        # Log if image was pulled from cache
                        image_already_exists = os.path.exists(OUTPUT_FILENAME)
                        if image_already_exists:
            
                            now = datetime.now().replace(microsecond=0)
                            log_date = now.strftime("%Y-%m-%d")
                            log_time = now.strftime("%H:%M:%S")
                            try:
                                with open(LOG_FILE_PATH, 'a') as log:
                                    log.write(f'\n{log_date}, {log_time}, Rotating Record Image Pulled From Cache')
                            except IOError as log_error:
                                print(f"[ERROR] Failed to write to log.txt: {log_error}")

                        if popup_rotated_frames:
                            # Create tonearm
                            record_x = SCREEN_WIDTH // 2 + 170
                            record_y = SCREEN_HEIGHT // 2 + 110
                            tonearm_pivot_x = record_x - 200
                            tonearm_pivot_y = record_y + 280
                            popup_tonearm = WurlitzerPaddleToneArm(tonearm_pivot_x, tonearm_pivot_y, 350)

                            # Set tonearm position based on song progress
                            song_progress = elapsed_seconds / total_seconds if total_seconds > 0 else 0
                            initial_angle = popup_tonearm.play_angle + (popup_tonearm.end_angle - popup_tonearm.play_angle) * song_progress
                            popup_tonearm.current_angle = initial_angle
                            popup_tonearm.target_angle = initial_angle

                            popup_rotation_angle = 0
                            popup_play_time = elapsed_seconds
                            popup_active = True

                            print("Popup activated successfully")

                    # Close popup
                    if should_close:
                        popup_active = False
                        popup_record_image = None
                        popup_record_surface = None
                        popup_rotated_frames = None
                        popup_tonearm = None
                        print("Popup closed (song ending)")

        except Exception as e:
            print(f"Error in popup logic: {e}")
            pass

        # Check selection popup timeout
        if selection_popup_active:
            elapsed = time.time() - selection_popup_start_time
            if elapsed >= selection_popup_duration:
                selection_popup_active = False
                selection_popup_surface = None
                print("[SELECTION POPUP] Auto-closed after 3 seconds")

        # Update popup animation if active
        if popup_active and popup_tonearm:
            dt = 1.0 / 60.0  # Frame delta time

            # Update tonearm
            popup_tonearm.update(dt)

            # Update rotation
            popup_rotation_angle = (popup_rotation_angle - RECORD_ROTATION_SPEED) % 360

            # Update tonearm tracking
            popup_play_time += dt
            if playback_engine.player and playback_engine.current_song_index is not None:
                duration_ms = playback_engine.player.get_length()
                if duration_ms > 0:
                    total_seconds = duration_ms / 1000.0
                    progress = min(popup_play_time / total_seconds, 1.0)
                    current_target = popup_tonearm.play_angle + (popup_tonearm.end_angle - popup_tonearm.play_angle) * progress
                    popup_tonearm.target_angle = current_target

        # Draw background
        screen.blit(background, (0, 0))

        # Draw button grid (hide when popup active)
        if not popup_active:
            button_grid.draw(screen, selection_entry_letter, selection_entry_number)

        # Draw arrow buttons
        screen.blit(arrow_left_img, (ARROW_LEFT_X, ARROW_LEFT_Y))
        screen.blit(arrow_right_img, (ARROW_RIGHT_X, ARROW_RIGHT_Y))

        # Draw control buttons (hide when popup active)
        if not popup_active:
            control_buttons.draw(screen, selection_entry_letter, selection_entry_number)

        # Draw info screen
        info_screen.draw(screen)

        # Draw song selection popup (if active)
        if selection_popup_active:
            try:
                # Use cached surface (loaded once at activation, not every frame)
                if selection_popup_surface is None:
                    selection_popup_surface = pygame.image.load('final_record_with_background.png').convert_alpha()

                # Position at (32, 300)
                popup_x = 58
                popup_y = 350

                # Draw black border/background
                border_size = 2
                pygame.draw.rect(screen, (0, 0, 0),
                               (popup_x - border_size, popup_y - border_size,
                                selection_popup_surface.get_width() + border_size * 2,
                                selection_popup_surface.get_height() + border_size * 2))

                # Draw the record image
                screen.blit(selection_popup_surface, (popup_x, popup_y))

            except Exception as e:
                print(f"[SELECTION POPUP] Error rendering: {e}")
                selection_popup_active = False

        # Draw rotating record popup (if active)
        if popup_active and popup_rotated_frames and popup_tonearm:
            # Brown background circle behind record
            record_x = SCREEN_WIDTH // 2 + 170
            record_y = SCREEN_HEIGHT // 2 + 110
            brown_background = (101, 67, 33)
            background_radius = 275
            pygame.draw.circle(screen, brown_background, (record_x, record_y), background_radius)

            # Draw pre-rotated record frame
            frame_index = (int(popup_rotation_angle) // 5) % 72
            rotated_surface = popup_rotated_frames[frame_index]
            rotated_rect = rotated_surface.get_rect(center=(record_x, record_y))
            screen.blit(rotated_surface, rotated_rect)

            # Draw tonearm
            popup_tonearm.draw(screen)

        # Update display
        pygame.display.flip()

        # Cap at 60 FPS
        clock.tick(60)

    # Cleanup
    playback_engine.player.stop()
    pygame.quit()
    sys.exit(0)

# ============================================================================ 
# SECTION 9: PROGRAM ENTRY POINT
# ============================================================================ 

if __name__ == "__main__":
    main()
