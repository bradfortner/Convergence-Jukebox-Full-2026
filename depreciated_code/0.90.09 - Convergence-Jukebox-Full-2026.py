"""
CONVERGENCE JUKEBOX - PYGAME MIGRATION VERSION
Version 0.90.09 - Pure Pygame Implementation (Step 7: Free Music Playback)

This version begins the migration from FreeSimpleGUI to pure Pygame.

Migration Goals:
- Eliminate Pygame/Tkinter z-order conflicts
- Enable seamless rotating record popup integration
- Create foundation for future touchscreen/arcade features

Version 0.90.09 Changes:
- Added random/free music playback system
- Music plays continuously (alternates between paid and random songs)
- Random playlist generated from all songs (skips songs marked 'norandom')
- Playback engine now: plays all paid songs → plays one random song → checks for more paid songs
- Auto-starts playing random music on launch
- Keeps jukebox always playing music

Next Steps:
- Add rotating record popup (the original reason for Pygame migration!)
- Add title/artist search functionality

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

# ============================================================================
# SECTION 2: CONSTANTS
# ============================================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND_IMAGE_PATH = "images/Full Jukebox Background Master 2026.png"
SONG_LIST_PATH = "MusicMasterSongList.txt"
BUZZ_SOUND_PATH = "jukebox_required_audio_files/buzz.mp3"
PAID_MUSIC_PLAYLIST_PATH = "PaidMusicPlayList.txt"

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

# ============================================================================
# SECTION 3: UTILITY FUNCTIONS
# ============================================================================

def format_time_remaining(seconds):
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

# ============================================================================
# SECTION 4: BUTTON GRID CLASS
# ============================================================================

class ButtonGrid:
    """Manages the selection button grid (A1-A7, B1-B7, C1-C7)"""

    def __init__(self, start_x, start_y, song_list, selection_window_number=0):
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

        # Create fonts
        self.font_id = pygame.font.SysFont('Helvetica', 16, bold=True)
        self.font_song = pygame.font.SysFont('Helvetica', 12, bold=True)

        # Build button grid structure
        self.buttons = self._create_button_layout()

    def _create_button_layout(self):
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
                # Calculate song index offset (A=0, B=14, C=28, then +2 per row)
                song_offset = (col_idx * 14) + ((row - 1) * 2)

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
                    title_text = self.song_list[song_idx]['title'][:22]

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
                song_offset = (col_idx * 14) + ((row - 1) * 2)

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
                    artist_text = self.song_list[song_idx]['artist'][:22]

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

    def update_selection_window(self, new_selection_window_number):
        """Update the grid to show a different page of songs

        Args:
            new_selection_window_number: New starting index for songs
        """
        self.selection_window_number = new_selection_window_number
        # Rebuild the button layout with new song data
        self.buttons = self._create_button_layout()

    def draw(self, screen, selection_letter=None, selection_number=None):
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
                        if song_idx < 14:
                            button_letter = 'A'
                        elif song_idx < 28:
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
                        if song_idx < 14:
                            row_num = (song_idx // 2) + 1
                        elif song_idx < 28:
                            row_num = ((song_idx - 14) // 2) + 1
                        else:
                            row_num = ((song_idx - 28) // 2) + 1
                        if row_num != selection_number:
                            is_dimmed = True

                # Draw button background image
                img = button['image']
                if is_dimmed:
                    # Create dimmed version (50% opacity overlay)
                    dimmed = img.copy()
                    dimmed.set_alpha(128)
                    screen.blit(dimmed, (button['x'], button['y']))
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

    def __init__(self, start_x, start_y):
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

    def _create_button_layout(self):
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

    def update_button_states(self, selection_letter=None, selection_number=None):
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

    def draw(self, screen):
        """Draw all control buttons

        Args:
            screen: Pygame surface to draw on
        """
        for button in self.buttons:
            # Draw button (dimmed if disabled)
            img = button['image']
            if not button['enabled']:
                # Create dimmed version
                dimmed = img.copy()
                dimmed.set_alpha(100)
                screen.blit(dimmed, (button['x'], button['y']))
            else:
                screen.blit(img, (button['x'], button['y']))

    def handle_click(self, pos):
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

    def __init__(self, start_x, start_y, song_list):
        """Initialize info screen

        Args:
            start_x: X position to start drawing
            start_y: Y position to start drawing
            song_list: Full song list for lookups
        """
        self.start_x = start_x
        self.start_y = start_y
        self.song_list = song_list

        # Create fonts
        self.font_header_large = pygame.font.SysFont('Helvetica', 20, bold=True)
        self.font_header_medium = pygame.font.SysFont('Helvetica', 18, bold=True)
        self.font_song_title = pygame.font.SysFont('Helvetica', 18, bold=True)
        self.font_song_artist = pygame.font.SysFont('Helvetica', 16, bold=True)
        self.font_info = pygame.font.SysFont('Helvetica', 12, bold=True)
        self.font_credits = pygame.font.SysFont('Helvetica', 20, bold=True)

        # Initialize display data
        self.current_song_index = None
        self.upcoming_songs = []
        self.credits = 0
        self.time_remaining = ""

    def update(self, current_song_index, upcoming_songs, credits, time_remaining_seconds=None):
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

    def draw(self, screen):
        """Draw info screen on the display

        Args:
            screen: Pygame surface to draw on
        """
        current_y = self.start_y + 10

        # "Now Playing" header
        text = self.font_header_large.render("Now Playing", True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 30

        # Current song title
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            title_text = song['title'][:20]
            text = self.font_song_title.render(title_text, True, COLOR_WHITE)
            rect = text.get_rect(center=(self.start_x + 145, current_y))
            screen.blit(text, rect)
        current_y += 25

        # Current artist
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            artist_text = song['artist'][:24]
            text = self.font_song_artist.render(artist_text, True, COLOR_WHITE)
            rect = text.get_rect(center=(self.start_x + 145, current_y))
            screen.blit(text, rect)
        current_y += 25

        # Mode indicator
        mode_text = "  Mode: Playing Song"
        text = self.font_info.render(mode_text, True, COLOR_SEAGREEN3)
        screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Mini song title
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            mini_title = song['title'][:28]
            text = self.font_info.render(mini_title, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Mini artist
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            mini_artist = song['artist'][:28]
            text = self.font_info.render(mini_artist, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Year & Time Remaining
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            if self.time_remaining:
                year_time = f"  Year: {song['year']}   Remaining: {self.time_remaining}"
            else:
                year_time = f"  Year: {song['year']}   Length: {song['duration']}"
            text = self.font_info.render(year_time, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 18

        # Album
        if self.current_song_index is not None and self.current_song_index < len(self.song_list):
            song = self.song_list[self.current_song_index]
            album_text = song['album'][:28]
            text = self.font_info.render(album_text, True, COLOR_SEAGREEN3)
            screen.blit(text, (self.start_x, current_y))
        current_y += 30

        # "Upcoming Selections" header
        text = self.font_header_medium.render("Upcoming Selections", True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 28

        # Spacer
        current_y += 5

        # 10 upcoming song slots
        for i in range(10):
            if i < len(self.upcoming_songs):
                song_idx = self.upcoming_songs[i]
                if song_idx < len(self.song_list):
                    song = self.song_list[song_idx]
                    upcoming_text = f"{song['title'][:15]} - {song['artist'][:10]}"
                    text = self.font_info.render(upcoming_text, True, COLOR_SEAGREEN3)
                    screen.blit(text, (self.start_x, current_y))
            current_y += 18

        # Spacer
        current_y += 5

        # Credits display
        credits_text = f"CREDITS {self.credits}"
        text = self.font_credits.render(credits_text, True, COLOR_WHITE)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 30

        # "Twenty-Five Cents Per Selection"
        text = self.font_info.render("Twenty-Five Cents Per Selection", True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)
        current_y += 18

        # Total songs available
        total_text = f"{len(self.song_list)} Song Selections Available"
        text = self.font_info.render(total_text, True, COLOR_SEAGREEN3)
        rect = text.get_rect(center=(self.start_x + 145, current_y))
        screen.blit(text, rect)

# ============================================================================
# SECTION 7: VLC PLAYBACK ENGINE
# ============================================================================

class PlaybackEngine:
    """Manages VLC playback of songs from paid and random playlists"""

    def __init__(self, song_list, paid_playlist_path):
        """Initialize playback engine

        Args:
            song_list: Full list of songs
            paid_playlist_path: Path to PaidMusicPlayList.txt
        """
        self.song_list = song_list
        self.paid_playlist_path = paid_playlist_path
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.current_song_index = None
        self.paid_playlist = []
        self.random_playlist = []
        self.is_paid_song = False  # Track if current song is paid or random

    def load_paid_playlist(self):
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

    def save_paid_playlist(self):
        """Save paid playlist to file"""
        try:
            with open(self.paid_playlist_path, 'w') as f:
                json.dump(self.paid_playlist, f)
        except Exception as e:
            print(f"Error saving paid playlist: {e}")

    def generate_random_playlist(self):
        """Generate random playlist from all songs (skips songs marked 'norandom')"""
        self.random_playlist = []

        for index, song in enumerate(self.song_list):
            # Skip songs marked with 'norandom' in comment field
            if 'norandom' in song.get('comment', '').lower():
                continue
            self.random_playlist.append(index)

        # Shuffle the playlist
        random.shuffle(self.random_playlist)
        print(f"Generated random playlist with {len(self.random_playlist)} songs")

    def update(self):
        """Update playback state - called every frame"""
        # Check if current song finished
        if self.player.get_state() == vlc.State.Ended:
            print("Song finished, loading next song")
            self.play_next_song()

    def play_next_song(self):
        """Play next song - paid songs first, then random songs"""
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

                # Create media and play
                media = self.vlc_instance.media_new(song_path)
                self.player.set_media(media)
                self.player.play()

                self.current_song_index = song_index
                self.is_paid_song = True

                # Remove from paid playlist and save
                self.paid_playlist.pop(0)
                self.save_paid_playlist()
            else:
                print(f"Invalid paid song index: {song_index}")
                # Remove invalid entry
                self.paid_playlist.pop(0)
                self.save_paid_playlist()
                # Try next song
                self.play_next_song()

        # Priority 2: Play random songs if no paid songs
        elif len(self.random_playlist) > 0:
            song_index = self.random_playlist[0]

            if song_index < len(self.song_list):
                song = self.song_list[song_index]
                song_path = song['location']

                print(f"Playing RANDOM: {song['title']} by {song['artist']}")
                print(f"Path: {song_path}")

                # Create media and play
                media = self.vlc_instance.media_new(song_path)
                self.player.set_media(media)
                self.player.play()

                self.current_song_index = song_index
                self.is_paid_song = False

                # Remove from random playlist (move to end for continuous play)
                self.random_playlist.pop(0)
                self.random_playlist.append(song_index)  # Add to end for rotation
            else:
                print(f"Invalid random song index: {song_index}")
                # Remove invalid entry
                self.random_playlist.pop(0)
                # Try next song
                self.play_next_song()

        else:
            print("No songs available (regenerating random playlist)")
            self.generate_random_playlist()
            if len(self.random_playlist) > 0:
                self.play_next_song()

    def get_time_remaining(self):
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

    def get_upcoming_songs(self):
        """Get list of upcoming song indices

        Returns:
            list: Song indices from paid playlist
        """
        self.load_paid_playlist()
        return self.paid_playlist.copy()

# ============================================================================
# SECTION 8: MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Create window (no title bar)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
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

    # Load song list
    try:
        with open(SONG_LIST_PATH, 'r') as f:
            song_list = json.load(f)
        print(f"Loaded {len(song_list)} songs from {SONG_LIST_PATH}")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading song list: {e}")
        pygame.quit()
        sys.exit(1)

    # Load arrow button images
    try:
        arrow_left_img = pygame.image.load(ARROW_LEFT_IMG)
        arrow_right_img = pygame.image.load(ARROW_RIGHT_IMG)
    except pygame.error as e:
        print(f"Error loading arrow images: {e}")
        pygame.quit()
        sys.exit(1)

    # Load buzz sound
    try:
        buzz_sound = pygame.mixer.Sound(BUZZ_SOUND_PATH)
    except pygame.error as e:
        print(f"Error loading buzz sound: {e}")
        buzz_sound = None

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

    # Create playback engine
    try:
        playback_engine = PlaybackEngine(song_list, PAID_MUSIC_PLAYLIST_PATH)
    except Exception as e:
        print(f"Error creating playback engine: {e}")
        pygame.quit()
        sys.exit(1)

    # Initialize random playlist and start playback
    print("Generating random playlist...")
    playback_engine.generate_random_playlist()
    print("Starting music playback...")
    playback_engine.play_next_song()

    # Initialize state variables
    selection_window_number = 0
    selection_entry_letter = None
    selection_entry_number = None
    credits = 0

    # Create rectangles for arrow button click detection
    arrow_left_rect = pygame.Rect(ARROW_LEFT_X, ARROW_LEFT_Y, arrow_left_img.get_width(), arrow_left_img.get_height())
    arrow_right_rect = pygame.Rect(ARROW_RIGHT_X, ARROW_RIGHT_Y, arrow_right_img.get_width(), arrow_right_img.get_height())

    # Main loop
    clock = pygame.time.Clock()
    running = True

    print("Convergence Jukebox v0.90.09 - Free Music Playback")
    print("Press ESC to exit")
    print("Press X to add credit")
    print("Press A/B/C to select column, 1-7 to select song, S to confirm")
    print("Music plays continuously: paid songs → random songs → check for more paid songs...")

    while running:
        # Update playback engine
        playback_engine.update()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Credit button
                elif event.key == pygame.K_x:
                    credits += 1
                    print(f"Credit added! Total credits: {credits}")

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

                elif event.key == pygame.K_c and event.mod == 0:
                    if selection_entry_letter is None:
                        selection_entry_letter = 'C'
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print(f"Selected column: C")
                    else:
                        # CORRECT button - reset selection
                        selection_entry_letter = None
                        selection_entry_number = None
                        control_buttons.update_button_states(selection_entry_letter, selection_entry_number)
                        print("Selection cleared")

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
                        if credits > 0:
                            # Calculate song index
                            letter_offset = {'A': 0, 'B': 14, 'C': 28}[selection_entry_letter]
                            row_offset = (selection_entry_number - 1) * 2
                            song_index = selection_window_number + letter_offset + row_offset

                            if song_index < len(song_list):
                                song = song_list[song_index]
                                print(f"Selected: {song['title']} by {song['artist']}")

                                # Add to paid playlist
                                playback_engine.load_paid_playlist()
                                playback_engine.paid_playlist.append(song_index)
                                playback_engine.save_paid_playlist()

                                # If nothing playing, start playback
                                if not playback_engine.player.is_playing():
                                    playback_engine.play_next_song()

                                # Deduct credit
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
                                    if credits > 0:
                                        # Calculate song index
                                        letter_offset = {'A': 0, 'B': 14, 'C': 28}[selection_entry_letter]
                                        row_offset = (selection_entry_number - 1) * 2
                                        song_index = selection_window_number + letter_offset + row_offset

                                        if song_index < len(song_list):
                                            song = song_list[song_index]
                                            print(f"Selected: {song['title']} by {song['artist']}")

                                            # Add to paid playlist
                                            playback_engine.load_paid_playlist()
                                            playback_engine.paid_playlist.append(song_index)
                                            playback_engine.save_paid_playlist()

                                            # If nothing playing, start playback
                                            if not playback_engine.player.is_playing():
                                                playback_engine.play_next_song()

                                            # Deduct credit
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

        # Draw background
        screen.blit(background, (0, 0))

        # Draw button grid
        button_grid.draw(screen, selection_entry_letter, selection_entry_number)

        # Draw arrow buttons
        screen.blit(arrow_left_img, (ARROW_LEFT_X, ARROW_LEFT_Y))
        screen.blit(arrow_right_img, (ARROW_RIGHT_X, ARROW_RIGHT_Y))

        # Draw control buttons
        control_buttons.draw(screen)

        # Draw info screen
        info_screen.draw(screen)

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
