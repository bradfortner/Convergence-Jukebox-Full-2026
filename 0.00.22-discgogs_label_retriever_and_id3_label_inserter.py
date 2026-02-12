"""
Music File Cleaner v0.00.22
Persistent Genre Search List

CHANGELOG v0.00.22:
- **PERSISTENT GENRE SEARCH LIST**:
  1. Genre file lists saved to genre_search.txt for session persistence
  2. Detects existing genre_search.txt on startup and prompts user to resume
  3. Removes processed/skipped files from genre_search.txt immediately
  4. Deletes genre_search.txt automatically when all files processed
  5. Corrupted genre_search.txt deleted automatically on startup
  6. Warns user if selecting new genre while existing search in progress
  7. Missing files (in list but not in Music dir) removed and skipped

CHANGELOG v0.00.21:
- **REMOVED the_bands.txt AUTO-UPDATE**:
  1. Removed _check_and_update_bands_file() method
  2. Removed call to update the_bands.txt when processing artists
  3. File now only reads from the_bands.txt, never writes to it
  4. Prevents unwanted modifications to the_bands.txt file

CHANGELOG v0.00.20:
- **CRITICAL FIXES**:
  1. Progress bar updates EVERY file (not every 10) - visible feedback during scan
  2. Fixed screen freeze after genre completion - clears genre_selection_screen
  3. Properly transitions back to search_options after genre processing completes

CHANGELOG v0.00.19:
- **CRITICAL BUGFIXES**:
  1. Fixed bypass logic for genre search - changed from True to False
  2. Now correctly skips files already processed (with "image" or "noimage" in comment)
  3. Screen properly transitions to "searching_music_file" state when genre is selected
  4. Genre search now respects skip logic like other search modes

CHANGELOG v0.00.18:
- **MULTI-COLUMN GENRE LAYOUT**:
  1. Modified GenreSelectionScreen to display genres in 4 columns
  2. Calculates column layout automatically based on total genres
  3. Fits more genres on screen without scrolling
  4. Maintains clickable checkboxes for each genre

CHANGELOG v0.00.17:
- **GENRE SPLITTING FIX**:
  1. Modified scan_all_genres() to split Comment tags by spaces
  2. Each word in Comment becomes a separate genre (e.g., "Rock Soul Blues" → "Rock", "Soul", "Blues")
  3. Users can now select individual genres instead of combined strings
  4. Strips whitespace and filters out empty strings

CHANGELOG v0.00.16:
- **CRITICAL BUGFIX - Comment Tag Reading**:
  1. Fixed scan_all_genres() to read COMM tags using raw ID3 format (not easy mode)
  2. Fixed find_files_by_genre() to read COMM tags correctly
  3. Changed from mutagen.File(easy=True) to mutagen.File() for proper tag access
  4. Uses get_tag_text() pattern: audio.get('COMM::eng', audio.get('COMM'))
  5. Now correctly finds genres in Comment tags

CHANGELOG v0.00.15:
- **GENRE SCANNING PROGRESS BAR**:
  1. Added draw_progress_bar() helper function for visual feedback
  2. Modified scan_all_genres() to display real-time progress bar
  3. Shows progress as percentage and "X of Y files scanned"
  4. Updates display after each file is processed
  5. Prevents UI freeze during long scan operations

CHANGELOG v0.00.14:
- **GENRE SELECTION SCREEN**:
  1. Added GenreSelectionScreen class - displays all unique genres found in Music directory
  2. Scans all Comment tags automatically when Option 5 is selected
  3. Shows genres as clickable checkboxes (no confirm button needed)
  4. Clicking a genre immediately starts processing files with that genre
  5. Helper function scan_all_genres() extracts and sorts unique genres
  6. Strips "image" and "noimage" suffixes from Comment tags before displaying

CHANGELOG v0.00.13:
- **GENRE SEARCH FEATURE**:
  1. Added Option 5: "Search By Genre" to SearchOptionsScreen
  2. Searches ID3 Comment tags for genre keywords (case-insensitive)
  3. Returns list of all matching files for batch processing
  4. Genre input box appears when Option 5 is selected
  5. Helper function find_files_by_genre() searches through Music directory

CHANGELOG v0.00.12:
- **EARLY OCR VALIDATION**:
  1. Run OCR on raw Discogs images immediately when downloaded (before circle detection)
  2. Auto-skip images that don't contain artist/title text match
  3. Auto-advance to next Discogs release when all images fail OCR validation
  4. Saves time by rejecting mismatches before expensive circle detection/cropping
  5. Validates against FILENAME artist/title (not Discogs metadata)

CHANGELOG v0.00.11:
- **MAJOR PERFORMANCE IMPROVEMENTS**:
  1. Parallel image downloads using ThreadPoolExecutor (3-5x faster for multi-image releases)
  2. Circle detection caching to avoid re-processing same images
  3. Reuse circle data from detect_circular_label() in extract_label() (eliminates duplicate detection)
  4. OCR result caching to avoid re-running expensive text extraction
  5. Batch image processing instead of sequential operations

CHANGELOG v0.00.06:
- FinalRecordViewer now displays record metadata (Artist, Title, Year, Genre)
- Added "Use This Label?" checkbox to FinalRecordViewer
- Clicking Use This Label goes directly to ConfirmationScreen (files already generated)
- Pass data_bundle to FinalRecordViewer so it has access to all metadata

CHANGELOG v0.00.05:
- FIXED: Changed final_record.png from incorrect 250x250 to correct 420x420
- This matches the ACTUAL original specification from v0.00.01
- 420x420 is the resolution written to ID3 album art when "Are You Sure" is pressed
- Updated all preview generation, ResultViewer, and FinalRecordViewer to use 420x420

CHANGELOG v0.00.04:
- Generate final_record.png using original specifications (WRONG: was 250x250, should be 420x420)
- Show thumbnail of final_record.png on FileDisplay browsing screen
- Click thumbnail to view full-size final_record.png in dedicated viewer
- Proper file naming: generates final_record.png (not temp files)

CHANGELOG v0.00.03:
- Auto-generate preview with adaptor on FileDisplay screen while browsing
- Show side-by-side: Original Discogs label | Label with adaptor inserted
- User sees final result BEFORE clicking "Create Label"
- Preview generated automatically when cycling through Discogs results

CHANGELOG v0.00.02:
- Add PreviewComparisonScreen to show side-by-side comparison
- Left side: Original cropped Discogs label
- Right side: Final label with adaptor inserted (from final_record.png)
- "Are You Sure?" button proceeds to ConfirmationScreen
- Pre-generates final_record.png for preview (reuses existing file)

CHANGELOG v0.00.01:
- Fetch ALL images from each Discogs release (not just first image)
- Pre-filter images using circle detection to identify 45rpm labels
- Only display images that contain circular label patterns
- Add left/right arrow navigation to cycle through filtered label images
- Display image counter (e.g., "Label 1 of 3")

DEPENDENCIES:
1. Local Python Modules:
   - music_file_cleaner_config.py (Discogs API token)
   - label_pressing_module.py (Label image generation)
   - id3_tag_writer_module.py (ID3 tagging)

2. Data Files:
   - discogs_search_list.txt (List of songs to process)
   - clean_up_log.txt (Log output)
   - the_bands.txt (Artist name cleaning)

3. Required Assets:
   - images/blank_record.png
   - fonts/ (Project fonts)

4. Temporary Files (Created/Overwritten):
   - temp_id3_image.png
   - temp_rotated_record.png
"""

import pygame
import discogs_client
import music_file_cleaner_config # Local Module: Configuration and Discogs Token
import json
import requests
import io
import datetime # Import datetime for time calculations
import os
import ast
import mutagen
import cv2
import numpy as np
import time
import logging
import threading
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import label_pressing_module # Local Module: Label Image Generation
import id3_tag_writer_module # Local Module: ID3 Tag Writer
try:
    import pytesseract
    from difflib import SequenceMatcher
    # Configure Tesseract path for Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_AVAILABLE = True
    print("✓ OCR (pytesseract) successfully loaded - text validation enabled")
except ImportError:
    OCR_AVAILABLE = False
    print("WARNING: pytesseract not available. OCR text validation will be skipped.")

# Configure logging to write to a file
logging.basicConfig(filename='clean_up_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s', filemode='w')


# Initialize Pygame and global variables
pygame.init()
FONT = pygame.font.Font(None, 32)
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

# v0.00.11: Performance optimization caches
CIRCLE_DETECTION_CACHE = {}  # Cache circle detection results by image hash
OCR_CACHE = {}  # Cache OCR results by image hash
MAX_CACHE_SIZE = 100  # Limit cache size to prevent memory issues

# Initialize Discogs client
d = discogs_client.Client('YourApp/1.0', user_token=music_file_cleaner_config.DISCOGS_USER_TOKEN)

def search_discogs(query, page=1, search_type='release', max_results=10):
    """
    Searches the Discogs database for releases and returns a list of 45rpm releases for a given page.
    max_results: Maximum number of results to return (default 10, can be increased for "Load More" feature)
    """
    print(f"\nSearching Discogs for '{query}' (page: {page}, type: {search_type}, max_results: {max_results})...")
    release_list = []
    try:
        start_time = time.time()
        results = d.search(query, type=search_type)
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"d.search() for '{query}' took {duration:.2f} seconds.")

        if results and page <= results.pages:
            print(f"Found {results.count} results. Filtering for 45rpm releases on page {page}.")
            for result in results.page(page):
                if len(release_list) >= max_results:
                    break
                if isinstance(result, discogs_client.models.Release):
                    is_45rpm = any(
                        format_entry.get('name') == 'Vinyl' and '7"' in format_entry.get('descriptions', []) and '45 RPM' in format_entry.get('descriptions', [])
                        for format_entry in result.formats or []
                    )
                    if is_45rpm:
                        release_list.append(result)

            if not release_list:
                print(f"No 45rpm releases found on page {page}.")
        else:
            print(f"  No {search_type} results found for '{query}' or page {page} out of range.")
    except json.JSONDecodeError as e:
        print(f"A JSON decoding error occurred during search: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during search: {e}")
    return release_list

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.placeholder_text = text
        self.focused = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.focused = True
            else:
                self.focused = False

        if event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in (pygame.K_TAB, pygame.K_RETURN, pygame.K_ESCAPE):
                self.text += event.unicode
        return None

    def draw(self, screen):
        display_text = self.text
        text_color = (255, 255, 255)
        if self.text == '' and not self.focused:
            display_text = self.placeholder_text
            text_color = (150, 150, 150) # Dim color for placeholder

        txt_surface = FONT.render(display_text, True, text_color)
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, COLOR_ACTIVE if self.focused else COLOR_INACTIVE, self.rect, 2)


class Button:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.focused = False

    def handle_event(self, event):
        # Buttons are handled by the main loop based on focus/clicks,
        # but this method prevents AttributeErrors in the event loop.
        pass

    def draw(self, screen):
        color = COLOR_ACTIVE if self.focused else COLOR_INACTIVE
        pygame.draw.rect(screen, color, self.rect)
        text_surf = FONT.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class Checkbox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.checked = False
        self.focused = False

    def handle_event(self, event, checkboxes):
        toggled = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                toggled = True
        if event.type == pygame.KEYDOWN:
            if self.focused and event.key == pygame.K_RETURN:
                toggled = True

        if toggled:
            self.checked = not self.checked
            if self.checked:
                for cb in checkboxes:
                    if cb != self:
                        cb.checked = False

    def draw(self, screen):
        color = COLOR_ACTIVE if self.focused else COLOR_INACTIVE
        pygame.draw.rect(screen, color, self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, (255, 255, 255), (self.rect.x + 3, self.rect.y + 3), (self.rect.x + self.rect.w - 3, self.rect.y + self.rect.h - 3), 2)
            pygame.draw.line(screen, (255, 255, 255), (self.rect.x + self.rect.w - 3, self.rect.y + 3), (self.rect.x + 3, self.rect.y + self.rect.h - 3), 2)

class ColoredCheckbox:
    """Checkbox that shows green when checked, red when unchecked"""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.checked = True  # Start checked (use default data)
        self.focused = False

    def handle_event(self, event):
        """Toggle checkbox on click, returns True if toggled"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False

    def draw(self, screen):
        """Draw checkbox - green when checked, red when unchecked"""
        # Fill color based on checked state
        fill_color = (0, 200, 0) if self.checked else (200, 0, 0)
        pygame.draw.rect(screen, fill_color, self.rect)

        # Border
        border_color = COLOR_ACTIVE if self.focused else COLOR_INACTIVE
        pygame.draw.rect(screen, border_color, self.rect, 2)

        # White checkmark when checked
        if self.checked:
            pygame.draw.line(screen, (255, 255, 255),
                           (self.rect.x + 3, self.rect.y + 10),
                           (self.rect.x + 8, self.rect.y + 15), 3)
            pygame.draw.line(screen, (255, 255, 255),
                           (self.rect.x + 8, self.rect.y + 15),
                           (self.rect.x + 17, self.rect.y + 3), 3)

class FileDisplay:
    def __init__(self, screen, filename, artist, title, fetched_data):
        self.screen = screen
        self.filename = filename
        self.artist = artist
        self.title = title

        # --- Fonts and UI Elements ---
        self.font_header = pygame.font.Font(None, 32)
        self.font_label = pygame.font.Font(None, 28)
        self.font_data = pygame.font.Font(None, 26)
        self.font_id3_label = pygame.font.Font(None, 22)
        self.font_id3_data = pygame.font.Font(None, 22)

        button_y_start = 480
        self.update_data_only_button = Button(screen.get_width() / 2 - 110, button_y_start, 220, 32, "Update Data Only")
        self.update_data_use_id3_button = Button(screen.get_width() / 2 - 110, button_y_start + 38, 220, 32, "Update Data/Use ID3 Image")
        self.edit_id3_button = Button(screen.get_width() / 2 - 110, button_y_start + 76, 220, 32, "Edit ID3 Tags")
        self.next_discogs_file_button = Button(screen.get_width() / 2 - 110, button_y_start + 114, 220, 32, "Next Discogs File")
        self.next_music_file_button = Button(screen.get_width() / 2 - 110, button_y_start + 152, 220, 32, "Next Music File")
        self.focusable_widgets = [self.update_data_only_button, self.update_data_use_id3_button, self.edit_id3_button, self.next_discogs_file_button, self.next_music_file_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

        self.thumb_rect = pygame.Rect(450, 100, 200, 200)
        self.adaptor_preview_rect = pygame.Rect(670, 100, 200, 200)  # v0.00.03: Preview with adaptor
        self.mutagen_thumb_rect = pygame.Rect(950, 100, 150, 150)

        # --- Populate Data from Prefetched Dictionary ---
        self.mutagen_tags = fetched_data.get('mutagen_tags', {})
        self.discogs_results = fetched_data.get('discogs_results', [])
        self.full_release = fetched_data.get('full_release', None)

        mutagen_image_data = fetched_data.get('mutagen_image_data')
        # v0.00.01: Changed from single image to list of filtered label images
        label_images_data = fetched_data.get('label_images_data', [])  # Now a list

        self.mutagen_image_surface = None
        if mutagen_image_data:
            try:
                image_file = io.BytesIO(mutagen_image_data)
                self.mutagen_image_surface = pygame.image.load(image_file)
            except pygame.error as e:
                print(f"Error loading mutagen image data: {e}")

        # v0.00.01: Support multiple filtered label images
        self.label_images_surfaces = []  # List of pygame surfaces
        self.current_label_image_index = 0  # Track which label image we're viewing
        for img_data in label_images_data:
            try:
                image_file = io.BytesIO(img_data)
                surface = pygame.image.load(image_file)
                self.label_images_surfaces.append(surface)
            except pygame.error as e:
                print(f"Error loading discogs label image data: {e}")

        # For backward compatibility, set label_image_surface to first filtered image
        self.label_image_surface = self.label_images_surfaces[0] if self.label_images_surfaces else None

        # v0.00.03: Adaptor-inserted preview surface (generated automatically)
        self.adaptor_preview_surface = None

        # --- Initialize remaining attributes ---
        self.discogs_result_index = 0
        self.is_fetching_discogs_data = False
        self.discogs_artist = "N/A"
        self.discogs_title = "N/A"
        self.year = "N/A"
        self.genres = []
        self.song_length = "N/A"
        self.artist_match = False
        self.title_match = False
        self.artist_case_mismatch = False
        self.title_case_mismatch = False
        self.year_match = False

        # --- Load More Results Feature (v0.00.70) ---
        self.max_results_limit = 10  # Start with 10, increases by 10 when "Load More" is clicked
        self.load_more_checkbox = Checkbox(650, 305, 20, 20, "")
        self.is_loading_more = False

        # v0.00.10: Track auto-advance attempts to prevent infinite loops
        self.auto_advance_attempts = 0
        self.max_auto_advance_attempts = 5  # Try up to 5 releases automatically

        # --- Threading for cycling through results ---
        self.fetch_thread = None
        self.fetch_result = {}

        # --- Process Prefetched Discogs Data ---
        if self.full_release:
            self._process_discogs_release(self.full_release, label_images_data)

    def _process_discogs_release(self, release, images_data=None):
        """Process a Discogs release and update all display data"""
        if release.artists:
            self.discogs_artist = release.artists[0].name
        self.discogs_title = release.title
        self.year = getattr(release, 'year', 'N/A')
        self.song_length, self.genres = self._get_song_length_and_genres(release)

        # v0.00.01: Update label images if provided (now handles list)
        if images_data:
            self.label_images_surfaces = []
            self.current_label_image_index = 0
            for img_data in images_data:
                try:
                    image_file = io.BytesIO(img_data)
                    surface = pygame.image.load(image_file)
                    self.label_images_surfaces.append(surface)
                except pygame.error as e:
                    print(f"Error loading discogs label image data: {e}")
            # Update current display surface
            self.label_image_surface = self.label_images_surfaces[0] if self.label_images_surfaces else None

            # v0.00.03: Auto-generate adaptor preview for FileDisplay browsing
            if self.label_image_surface:
                self._generate_adaptor_preview()

        # Check matches
        cleaned_artist_filename = self._clean_string(self.artist)
        cleaned_artist_discogs = self._clean_string(self.discogs_artist)
        cleaned_title_filename = self._clean_string(self.title)
        cleaned_title_discogs = self._clean_string(self.discogs_title)

        self.artist_match = cleaned_artist_filename.lower() == cleaned_artist_discogs.lower()
        self.title_match = cleaned_title_filename.lower() == cleaned_title_discogs.lower()

        self.artist_case_mismatch = False
        self.title_case_mismatch = False

        if self.artist_match and cleaned_artist_filename != cleaned_artist_discogs:
            self.artist_case_mismatch = True

        if self.title_match and cleaned_title_filename != cleaned_title_discogs:
            self.title_case_mismatch = True

        # Check year match
        id3_year = str(self.mutagen_tags.get('year', 'N/A'))
        discogs_year = str(self.year)
        # Extract just the year part (handles formats like "2024-01-01" -> "2024")
        if id3_year != 'N/A' and len(id3_year) >= 4:
            id3_year = id3_year[:4]
        if discogs_year != 'N/A' and len(discogs_year) >= 4:
            discogs_year = discogs_year[:4]
        self.year_match = id3_year == discogs_year and id3_year != 'N/A'

    def _clean_string(self, text):
        cleaned_text = text.replace("'", "").replace(",", "")
        if cleaned_text.lower().startswith("the "):
            cleaned_text = cleaned_text[4:]
        return cleaned_text

    def _generate_adaptor_preview(self, recursion_depth=0):
        """
        v0.00.08: Generate final_record.png at CORRECT original specs (420x420)
        and load it as thumbnail for FileDisplay browsing screen.
        Added validation: if final image is malformed, auto-skip to next image.
        """
        # Prevent infinite recursion if all images fail validation
        if recursion_depth > len(self.label_images_surfaces):
            print("⚠ All label images failed validation, stopping auto-skip")
            self.adaptor_preview_surface = None
            return

        try:
            print("Generating final_record.png with adaptor (420x420)...")

            # Step 1: Extract label using circle detection
            cropped_label_surface = extract_label(self.label_image_surface)

            if not cropped_label_surface:
                print("Could not extract label - no circles detected")
                # Auto-skip to next image
                if len(self.label_images_surfaces) > 1:
                    print(f"⏭ Auto-skipping to next label image ({self.current_label_image_index + 1}/{len(self.label_images_surfaces)})")
                    self.current_label_image_index = (self.current_label_image_index + 1) % len(self.label_images_surfaces)
                    self.label_image_surface = self.label_images_surfaces[self.current_label_image_index]
                    self._generate_adaptor_preview(recursion_depth + 1)
                else:
                    # v0.00.10: Try next Discogs release automatically
                    print("⚠ NO MORE LABEL IMAGES in current release - All images failed validation")
                    if self._try_next_discogs_release():
                        # Auto-advance succeeded, preview will be generated when new data loads
                        return
                    else:
                        # Hit auto-advance limit or no more releases
                        self.adaptor_preview_surface = None
                return

            # Step 2: Save cropped label to new_cutout_label.png
            pygame.image.save(cropped_label_surface, 'new_cutout_label.png')

            # Step 3: Generate final_record.png using CORRECT original specifications (420x420)
            success = label_pressing_module.combine_pngs(
                label_path='new_cutout_label.png',
                adaptor_path='adaptor.png',
                output_path='final_record.png',
                size=(420, 420),
                base_record_path='blank_record.png'
            )

            if not success:
                print("Failed to generate final_record.png")
                # Auto-skip to next image
                if len(self.label_images_surfaces) > 1:
                    print(f"⏭ Auto-skipping to next label image ({self.current_label_image_index + 1}/{len(self.label_images_surfaces)})")
                    self.current_label_image_index = (self.current_label_image_index + 1) % len(self.label_images_surfaces)
                    self.label_image_surface = self.label_images_surfaces[self.current_label_image_index]
                    self._generate_adaptor_preview(recursion_depth + 1)
                else:
                    # v0.00.10: Try next Discogs release automatically
                    print("⚠ NO MORE LABEL IMAGES in current release - All images failed validation")
                    if self._try_next_discogs_release():
                        # Auto-advance succeeded, preview will be generated when new data loads
                        return
                    else:
                        # Hit auto-advance limit or no more releases
                        self.adaptor_preview_surface = None
                return

            # v0.00.08: Step 4: Validate the final combined image (structure)
            is_valid = validate_final_record('final_record.png', debug=True)

            if not is_valid:
                print("⚠ Final image failed validation (malformed label/adaptor)")
                # Auto-skip to next image
                if len(self.label_images_surfaces) > 1:
                    print(f"⏭ Auto-skipping to next label image ({self.current_label_image_index + 1}/{len(self.label_images_surfaces)})")
                    self.current_label_image_index = (self.current_label_image_index + 1) % len(self.label_images_surfaces)
                    self.label_image_surface = self.label_images_surfaces[self.current_label_image_index]
                    self._generate_adaptor_preview(recursion_depth + 1)
                else:
                    # v0.00.10: Try next Discogs release automatically
                    print("⚠ NO MORE LABEL IMAGES in current release - All images failed validation")
                    if self._try_next_discogs_release():
                        # Auto-advance succeeded, preview will be generated when new data loads
                        return
                    else:
                        # Hit auto-advance limit or no more releases
                        self.adaptor_preview_surface = None
                return

            # v0.00.09: Step 5: Validate label text contains artist/title using OCR
            # v0.00.10 FIX: Use ORIGINAL filename artist/title, not Discogs result (which changes when auto-advancing)
            text_valid = validate_label_text('new_cutout_label.png', self.artist, self.title, debug=True)

            if not text_valid:
                print("⚠ Final image failed OCR text validation (artist/title not found on label)")
                # Auto-skip to next image
                if len(self.label_images_surfaces) > 1:
                    print(f"⏭ Auto-skipping to next label image ({self.current_label_image_index + 1}/{len(self.label_images_surfaces)})")
                    self.current_label_image_index = (self.current_label_image_index + 1) % len(self.label_images_surfaces)
                    self.label_image_surface = self.label_images_surfaces[self.current_label_image_index]
                    self._generate_adaptor_preview(recursion_depth + 1)
                else:
                    # v0.00.10: Try next Discogs release automatically
                    print("⚠ NO MORE LABEL IMAGES in current release - All images failed validation")
                    if self._try_next_discogs_release():
                        # Auto-advance succeeded, preview will be generated when new data loads
                        return
                    else:
                        # Hit auto-advance limit or no more releases
                        self.adaptor_preview_surface = None
                return

            # Step 6: Load final_record.png as thumbnail surface (only if all validations passed)
            self.adaptor_preview_surface = pygame.image.load('final_record.png')
            print("✓ final_record.png generated and validated successfully (420x420)")

            # v0.00.10: Reset auto-advance counter on success
            self.auto_advance_attempts = 0

        except Exception as e:
            print(f"Error generating adaptor preview: {e}")
            self.adaptor_preview_surface = None

    def _try_next_discogs_release(self):
        """
        v0.00.10: Automatically advance to next Discogs release when all label images fail validation.
        Returns True if successfully advanced, False if limit reached.
        """
        self.auto_advance_attempts += 1

        if self.auto_advance_attempts > self.max_auto_advance_attempts:
            print(f"⚠ Reached maximum auto-advance limit ({self.max_auto_advance_attempts} releases tried)")
            print(f"   Stopping automatic advancement. Press 'Next Discogs File' to continue manually.")
            return False

        if not self.discogs_results or len(self.discogs_results) <= 1:
            print("⚠ No more Discogs releases available to try automatically")
            return False

        print(f"")
        print(f"🔄 AUTO-ADVANCING to next Discogs release (attempt {self.auto_advance_attempts}/{self.max_auto_advance_attempts})...")
        print(f"")

        # Call the existing method to advance to next release
        self._update_with_current_discogs_result()

        return True

    def _update_with_current_discogs_result(self):
        """Cycle to the next Discogs result and fetch its full details"""
        if not self.discogs_results:
            print("No Discogs results to cycle through.")
            return

        if self.is_fetching_discogs_data:
            print("Already fetching data, please wait...")
            return

        # Increment index
        self.discogs_result_index += 1

        # Determine the start of the current range (v0.00.70)
        # If max_results_limit = 10: range is 1-10 (indices 0-9), wrap to 0
        # If max_results_limit = 20: range is 11-20 (indices 10-19), wrap to 10
        # If max_results_limit = 30: range is 21-30 (indices 20-29), wrap to 20
        range_start = max(0, self.max_results_limit - 10)

        # Wrap around to the start of the current range when exceeding limit
        if self.discogs_result_index >= len(self.discogs_results) or self.discogs_result_index >= self.max_results_limit:
            self.discogs_result_index = range_start
            print(f"Wrapping to start of current range: record {range_start + 1}")

        print(f"Cycling to Discogs result {self.discogs_result_index + 1} of {len(self.discogs_results)}")

        # Start fetching in background thread
        def fetch_worker():
            # v0.00.01: Changed to fetch and filter ALL images
            fetched = {'full_release': None, 'images_data': []}
            try:
                result = self.discogs_results[self.discogs_result_index]
                release = d.release(result.id)
                fetched['full_release'] = release

                # v0.00.12: Download ALL images and filter in parallel with EARLY OCR validation
                filtered_images = download_and_filter_images_parallel(release, artist_name=self.artist, song_title=self.title, max_workers=5)
                fetched['images_data'] = [img_bytes for img_bytes, circle_data in filtered_images]
            except Exception as e:
                print(f"Error fetching Discogs result: {e}")

            self.fetch_result.update(fetched)

        self.is_fetching_discogs_data = True
        self.fetch_result.clear()
        self.fetch_thread = threading.Thread(target=fetch_worker)
        self.fetch_thread.start()

    def _get_song_length_and_genres(self, release):
        """Extract song length and genres from a release object"""
        total_duration_seconds = 0
        genres = []

        if hasattr(release, 'tracklist') and release.tracklist:
            for track in release.tracklist:
                if track.duration:
                    try:
                        minutes, seconds = map(int, track.duration.split(':'))
                        total_duration_seconds += (minutes * 60) + seconds
                    except ValueError:
                        pass

        if hasattr(release, 'genres') and release.genres:
            genres = release.genres

        if total_duration_seconds > 0:
            total_duration = str(datetime.timedelta(seconds=total_duration_seconds))
            if len(total_duration.split(':')) == 2:
                 total_duration = "0" + total_duration
        else:
            total_duration = "N/A"

        return total_duration, genres

    def _draw_match_indicator(self, x, y, is_match, is_case_mismatch=False):
        box_rect = pygame.Rect(x, y, 20, 20)
        if is_match and not is_case_mismatch:  # Only perfect matches get green
            pygame.draw.rect(self.screen, (0, 255, 0), box_rect)  # Green
            pygame.draw.line(self.screen, (0, 0, 0), (x + 5, y + 10), (x + 8, y + 13), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x + 8, y + 13), (x + 15, y + 6), 2)
        else:  # Any mismatch (either no match, or case mismatch) gets red
            pygame.draw.rect(self.screen, (255, 0, 0), box_rect)  # Red
            pygame.draw.line(self.screen, (0, 0, 0), (x + 5, y + 5), (x + 15, y + 15), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x + 5, y + 15), (x + 15, y + 5), 2)

    def _should_show_load_more_checkbox(self):
        """Show checkbox when at the last result (e.g., 10 of 10, 20 of 20, etc.)"""
        if not self.discogs_results:
            return False
        # Show when we're at the last result AND we've hit our current limit
        return (self.discogs_result_index + 1) == len(self.discogs_results) == self.max_results_limit

    def update(self):
        """Check if background fetch is complete and process results"""
        if self.fetch_thread and not self.fetch_thread.is_alive():
            self.fetch_thread = None
            self.is_fetching_discogs_data = False

            release = self.fetch_result.get('full_release')
            # v0.00.01: Changed from single image_data to images_data list
            images_data = self.fetch_result.get('images_data', [])

            if release:
                self.full_release = release
                self._process_discogs_release(release, images_data)
                label_count = len(self.label_images_surfaces)
                print(f"Updated to: {self.discogs_artist} - {self.discogs_title} ({label_count} label images)")

                # v0.00.12: If NO label images found (all failed early OCR validation), auto-advance to next release
                if label_count == 0:
                    print("⚠ NO VALID LABEL IMAGES found (all failed early OCR validation)")
                    if self._try_next_discogs_release():
                        print("🔄 Auto-advancing to next Discogs release...")
                    else:
                        print("⚠ No more Discogs releases to try")
                # v0.00.10: If we have label images and we're in auto-advance mode, generate preview automatically
                elif label_count > 0 and self.auto_advance_attempts > 0:
                    print(f"🔄 Auto-generating preview for new release...")
                    self._generate_adaptor_preview()
            else:
                print("Failed to fetch Discogs data")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # v0.00.01: Add left/right arrow navigation for cycling through filtered label images
            if event.key == pygame.K_LEFT:
                if len(self.label_images_surfaces) > 1:
                    self.current_label_image_index = (self.current_label_image_index - 1) % len(self.label_images_surfaces)
                    self.label_image_surface = self.label_images_surfaces[self.current_label_image_index]
                    print(f"← Previous label image ({self.current_label_image_index + 1}/{len(self.label_images_surfaces)})")
                    # v0.00.03: Regenerate adaptor preview for new label
                    self._generate_adaptor_preview()
                return None, None
            elif event.key == pygame.K_RIGHT:
                if len(self.label_images_surfaces) > 1:
                    self.current_label_image_index = (self.current_label_image_index + 1) % len(self.label_images_surfaces)
                    self.label_image_surface = self.label_images_surfaces[self.current_label_image_index]
                    print(f"→ Next label image ({self.current_label_image_index + 1}/{len(self.label_images_surfaces)})")
                    # v0.00.03: Regenerate adaptor preview for new label
                    self._generate_adaptor_preview()
                return None, None
            elif event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
            elif event.key == pygame.K_RETURN:
                focused_widget = self.focusable_widgets[self.focused_index]
                if focused_widget == self.next_music_file_button:
                    return "continue", None
                elif focused_widget == self.next_discogs_file_button:
                    self.auto_advance_attempts = 0  # v0.00.10: Reset counter on manual advance
                    self._update_with_current_discogs_result()
                elif focused_widget == self.update_data_only_button:
                    # Show confirmation screen without image
                    data_bundle = {
                        'data_bundle': {
                            'mutagen_tags': self.mutagen_tags,
                            'discogs_artist': self.discogs_artist,
                            'discogs_title': self.discogs_title,
                            'discogs_year': self.year,
                            'discogs_genres': self.genres,
                            'artist_match': self.artist_match,
                            'title_match': self.title_match,
                            'year_match': self.year_match,
                            'filename': self.filename
                        }
                    }
                    return "show_confirmation_no_image", data_bundle
                elif focused_widget == self.update_data_use_id3_button:
                    # Same as clicking the ID3 image - show full screen mutagen image
                    if self.mutagen_image_surface:
                        data_bundle = {
                            'image_surface': self.mutagen_image_surface,
                            'mutagen_tags': self.mutagen_tags,
                            'discogs_artist': self.discogs_artist,
                            'discogs_title': self.discogs_title,
                            'discogs_year': self.year,
                            'discogs_genres': self.genres,
                            'artist_match': self.artist_match,
                            'title_match': self.title_match,
                            'year_match': self.year_match,
                            'filename': self.filename
                        }
                        return "view_full_screen_image", data_bundle
                    return None, None
                elif focused_widget == self.edit_id3_button:
                    # Open ID3 edit screen
                    data_bundle = {
                        'mutagen_tags': self.mutagen_tags,
                        'mutagen_image_surface': self.mutagen_image_surface,
                        'filename': self.filename
                    }
                    return "edit_id3_tags", data_bundle

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.thumb_rect.collidepoint(event.pos) and self.label_image_surface:
                # Create data bundle with all metadata
                data_bundle = {
                    'image_surface': self.label_image_surface,
                    'mutagen_tags': self.mutagen_tags,
                    'discogs_artist': self.discogs_artist,
                    'discogs_title': self.discogs_title,
                    'discogs_year': self.year,
                    'discogs_genres': self.genres,
                    'artist_match': self.artist_match,
                    'title_match': self.title_match,
                    'year_match': self.year_match,
                    'filename': self.filename,
                    'filename_artist': self.artist,  # v0.00.10: Original artist from filename for OCR validation
                    'filename_title': self.title     # v0.00.10: Original title from filename for OCR validation
                }
                return "view_full_screen_image", data_bundle
            # v0.00.06: Click on adaptor preview thumbnail - pass data_bundle to FinalRecordViewer
            if self.adaptor_preview_rect.collidepoint(event.pos) and self.adaptor_preview_surface:
                data_bundle = {
                    'mutagen_tags': self.mutagen_tags,
                    'discogs_artist': self.discogs_artist,
                    'discogs_title': self.discogs_title,
                    'discogs_year': self.year,
                    'discogs_genres': self.genres,
                    'filename': self.filename
                }
                return "view_final_record", data_bundle
            if self.mutagen_thumb_rect.collidepoint(event.pos) and self.mutagen_image_surface:
                # Create data bundle for mutagen image
                data_bundle = {
                    'image_surface': self.mutagen_image_surface,
                    'mutagen_tags': self.mutagen_tags,
                    'discogs_artist': self.discogs_artist,
                    'discogs_title': self.discogs_title,
                    'discogs_year': self.year,
                    'discogs_genres': self.genres,
                    'artist_match': self.artist_match,
                    'title_match': self.title_match,
                    'year_match': self.year_match,
                    'filename': self.filename
                }
                return "view_full_screen_image", data_bundle
            if self.next_music_file_button.rect.collidepoint(event.pos):
                return "continue", None
            if self.next_discogs_file_button.rect.collidepoint(event.pos):
                self.auto_advance_attempts = 0  # v0.00.10: Reset counter on manual advance
                self._update_with_current_discogs_result()
            if self.update_data_only_button.rect.collidepoint(event.pos):
                # Show confirmation screen without image
                data_bundle = {
                    'data_bundle': {
                        'mutagen_tags': self.mutagen_tags,
                        'discogs_artist': self.discogs_artist,
                        'discogs_title': self.discogs_title,
                        'discogs_year': self.year,
                        'discogs_genres': self.genres,
                        'artist_match': self.artist_match,
                        'title_match': self.title_match,
                        'year_match': self.year_match,
                        'filename': self.filename
                    }
                }
                return "show_confirmation_no_image", data_bundle
            if self.update_data_use_id3_button.rect.collidepoint(event.pos):
                # Same as clicking the ID3 image - show full screen mutagen image
                if self.mutagen_image_surface:
                    data_bundle = {
                        'image_surface': self.mutagen_image_surface,
                        'mutagen_tags': self.mutagen_tags,
                        'discogs_artist': self.discogs_artist,
                        'discogs_title': self.discogs_title,
                        'discogs_year': self.year,
                        'discogs_genres': self.genres,
                        'artist_match': self.artist_match,
                        'title_match': self.title_match,
                        'year_match': self.year_match,
                        'filename': self.filename
                    }
                    return "view_full_screen_image", data_bundle
                return None, None
            if self.edit_id3_button.rect.collidepoint(event.pos):
                # Open ID3 edit screen
                data_bundle = {
                    'mutagen_tags': self.mutagen_tags,
                    'mutagen_image_surface': self.mutagen_image_surface,
                    'filename': self.filename
                }
                return "edit_id3_tags", data_bundle

            # Handle "Load 10 More?" checkbox click (v0.00.70)
            if self.load_more_checkbox.rect.collidepoint(event.pos):
                if self._should_show_load_more_checkbox():
                    print(f"Loading 10 more results (current limit: {self.max_results_limit})...")
                    return "load_more_results", None
        return None, None

    def draw(self, screen):
        # Headers
        header_file = self.font_header.render("File Data", True, (255, 255, 255))
        header_discogs = self.font_header.render("Discogs Data", True, (255, 255, 255))
        header_id3 = self.font_header.render("ID3 Tag Data", True, (255, 255, 255))
        screen.blit(header_file, (50, 50))
        screen.blit(header_discogs, (450, 50))
        screen.blit(header_id3, (950, 50))

        self._draw_file_info_column(screen)
        self._draw_discogs_info_column(screen)
        self._draw_mutagen_info_column(screen)
        self._draw_buttons(screen)

    def _draw_file_info_column(self, screen):
        # Column 1: File Data
        y_offset = 100
        x_pos = 50

        info_to_draw = [
            ("Filename: ", self.filename),
            ("Artist: ", self.artist),
            ("Title: ", self.title),
        ]

        for label_text, data_text in info_to_draw:
            if len(data_text) > 45:
                data_text = data_text[:42] + '...'

            label_surf = self.font_id3_label.render(label_text, True, (200, 200, 200))
            data_surf = self.font_id3_data.render(data_text, True, (255, 255, 255))

            screen.blit(label_surf, (x_pos, y_offset))
            screen.blit(data_surf, (x_pos + label_surf.get_width(), y_offset))

            y_offset += 25 # Reduced line spacing

    def _draw_discogs_info_column(self, screen):
        # Column 2: Discogs Data
        # Thumbnail
        if self.is_fetching_discogs_data:
            pygame.draw.rect(screen, (50, 50, 50), self.thumb_rect)
            text_surf = self.font_label.render("Loading...", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.thumb_rect.center)
            screen.blit(text_surf, text_rect)
        elif self.label_image_surface:
            screen.blit(pygame.transform.scale(self.label_image_surface, (self.thumb_rect.width, self.thumb_rect.height)), (self.thumb_rect.x, self.thumb_rect.y))

            # v0.00.01: Show label image counter if multiple filtered images exist
            if len(self.label_images_surfaces) > 1:
                label_counter_text = f"Label {self.current_label_image_index + 1} of {len(self.label_images_surfaces)} (← →)"
                label_counter_surf = self.font_id3_label.render(label_counter_text, True, (255, 255, 0))  # Yellow for visibility
                screen.blit(label_counter_surf, (self.thumb_rect.x, self.thumb_rect.y + self.thumb_rect.height + 5))
        else:
            pygame.draw.rect(screen, (50, 50, 50), self.thumb_rect)
            text_surf = self.font_label.render("No Label Image", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.thumb_rect.center)
            screen.blit(text_surf, text_rect)

        # v0.00.03: Draw adaptor-inserted preview thumbnail
        if self.adaptor_preview_surface:
            scaled_preview = pygame.transform.scale(self.adaptor_preview_surface, (self.adaptor_preview_rect.width, self.adaptor_preview_rect.height))
            screen.blit(scaled_preview, (self.adaptor_preview_rect.x, self.adaptor_preview_rect.y))

            # Label below preview
            preview_label = self.font_id3_label.render("With Adaptor", True, (255, 255, 0))
            label_x = self.adaptor_preview_rect.x + (self.adaptor_preview_rect.width - preview_label.get_width()) // 2
            screen.blit(preview_label, (label_x, self.adaptor_preview_rect.y + self.adaptor_preview_rect.height + 5))
        elif self.label_image_surface and not self.is_fetching_discogs_data:
            # Show "Generating..." if we have a label but no preview yet
            pygame.draw.rect(screen, (50, 50, 50), self.adaptor_preview_rect)
            text_surf = self.font_label.render("Generating...", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.adaptor_preview_rect.center)
            screen.blit(text_surf, text_rect)

        # Result counter
        if self.discogs_results:
            counter_text = f"Result {self.discogs_result_index + 1} of {len(self.discogs_results)}"
            counter_surf = self.font_id3_label.render(counter_text, True, (200, 200, 200))
            screen.blit(counter_surf, (450, 305))

            # Show "Load 10 More?" checkbox when at last result (v0.00.70)
            if self._should_show_load_more_checkbox():
                self.load_more_checkbox.draw(screen)
                label_surf = self.font_id3_label.render("Load 10 More?", True, (200, 200, 200))
                screen.blit(label_surf, (self.load_more_checkbox.rect.x + 25, self.load_more_checkbox.rect.y - 2))

        # Details below thumbnail
        y_offset = 320
        x_pos = 475
        indicator_x_pos = 450

        # Artist
        label_surf = self.font_id3_label.render("Artist: ", True, (200, 200, 200))
        data_surf = self.font_id3_data.render(self.discogs_artist, True, (255, 255, 255))
        self._draw_match_indicator(indicator_x_pos, y_offset + 2, self.artist_match, self.artist_case_mismatch)
        screen.blit(label_surf, (x_pos, y_offset))
        screen.blit(data_surf, (x_pos + label_surf.get_width(), y_offset))
        y_offset += 25

        # Title
        label_surf = self.font_id3_label.render("Title: ", True, (200, 200, 200))
        data_surf = self.font_id3_data.render(self.discogs_title, True, (255, 255, 255))
        self._draw_match_indicator(indicator_x_pos, y_offset + 2, self.title_match, self.title_case_mismatch)
        screen.blit(label_surf, (x_pos, y_offset))
        screen.blit(data_surf, (x_pos + label_surf.get_width(), y_offset))
        y_offset += 25

        # Year with match indicator
        label_surf = self.font_id3_label.render("Year: ", True, (200, 200, 200))
        data_surf = self.font_id3_data.render(str(self.year), True, (255, 255, 255))
        self._draw_match_indicator(indicator_x_pos, y_offset + 2, self.year_match)
        screen.blit(label_surf, (x_pos, y_offset))
        screen.blit(data_surf, (x_pos + label_surf.get_width(), y_offset))
        y_offset += 25

        # Other data
        genres_text = ", ".join(self.genres) if self.genres else "N/A"
        other_info = [
            ("Genre: ", genres_text),
            ("Length: ", self.song_length),
        ]

        for label_text, data_text in other_info:
            label_surf = self.font_id3_label.render(label_text, True, (200, 200, 200))
            data_surf = self.font_id3_data.render(data_text, True, (255, 255, 255))
            screen.blit(label_surf, (x_pos, y_offset))
            screen.blit(data_surf, (x_pos + label_surf.get_width(), y_offset))
            y_offset += 25

    def _draw_mutagen_info_column(self, screen):
        # Column 3: ID3 Tag Data
        y_offset = 100
        x_pos = 950

        # Image
        if self.mutagen_image_surface:
            try:
                screen.blit(pygame.transform.scale(self.mutagen_image_surface, (self.mutagen_thumb_rect.width, self.mutagen_thumb_rect.height)), (self.mutagen_thumb_rect.x, self.mutagen_thumb_rect.y))
            except pygame.error: # Handle potential invalid image data
                pygame.draw.rect(screen, (50, 50, 50), self.mutagen_thumb_rect)
                text_surf = self.font_data.render("Bad Art", True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=self.mutagen_thumb_rect.center)
                screen.blit(text_surf, text_rect)
        else:
            pygame.draw.rect(screen, (50, 50, 50), self.mutagen_thumb_rect)
            text_surf = self.font_data.render("No Art", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.mutagen_thumb_rect.center)
            screen.blit(text_surf, text_rect)
        y_offset += self.mutagen_thumb_rect.height + 20

        # --- Text data ---
        tags_to_draw = [
            ("Artist Tag:", 'artist'),
            ("Title Tag:", 'title'),
            ("Album Tag:", 'album'),
            ("Genre Tag:", 'genre'),
            ("Year Tag:", 'year'),
            ("Time:", 'time'),
            ("Comment:", 'comment'),
        ]

        for label, key in tags_to_draw:
            # Render the label with the new smaller font
            label_surf = self.font_id3_label.render(label + " ", True, (200, 200, 200))
            screen.blit(label_surf, (x_pos, y_offset))

            # Render the data with its new smaller font
            tag_text = str(self.mutagen_tags.get(key, 'N/A'))
            if len(tag_text) > 25: # Adjust truncation for smaller font
                tag_text = tag_text[:22] + '...'

            data_surf = self.font_id3_data.render(tag_text, True, (255, 255, 255))

            # Blit the data right after the label
            screen.blit(data_surf, (x_pos + label_surf.get_width(), y_offset))

            # Increment y_offset for the next line with smaller spacing
            y_offset += 25

    def _draw_buttons(self, screen):
        # Buttons at the bottom
        self.update_data_only_button.draw(screen)
        self.update_data_use_id3_button.draw(screen)
        self.edit_id3_button.draw(screen)
        self.next_discogs_file_button.draw(screen)
        self.next_music_file_button.draw(screen)


class ResultsViewer:
    def __init__(self, screen, results):
        self.screen = screen
        self.results = results
        self.font = pygame.font.Font(None, 24)
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.select_button = Button(screen.get_width() - 110, screen.get_height() - 42, 100, 32, "Select")
        self.next_button = Button(screen.get_width() - 220, screen.get_height() - 42, 100, 32, "Next 10")

        self.checkboxes = []
        self.images = self._load_images()
        y_offset = 50
        for i, result in enumerate(self.results):
            self.checkboxes.append(Checkbox(50, y_offset + 15, 20, 20))
            y_offset += 60

        self.focusable_widgets = self.checkboxes + [self.back_button, self.select_button, self.next_button]
        self.focused_index = 0
        if self.focusable_widgets:
            self.focusable_widgets[self.focused_index].focused = True

    def _load_images(self):
        images = []
        for result in self.results:
            image_surface = None
            if hasattr(result, 'images') and result.images:
                image_url = result.images[0]['uri']
                try:
                    headers = {'User-Agent': 'YourApp/1.0'}
                    response = requests.get(image_url, headers=headers)
                    response.raise_for_status()
                    image_data = response.content
                    image_file = io.BytesIO(image_data)
                    image_surface = pygame.image.load(image_file)
                except Exception as e:
                    print(f"Error loading image: {e}")
            if image_surface:
                images.append(pygame.transform.scale(image_surface, (50, 50)))
            else:
                placeholder = pygame.Surface((50, 50))
                placeholder.fill((50, 50, 50))
                images.append(placeholder)
        return images

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if self.focusable_widgets:
                    self.focusable_widgets[self.focused_index].focused = False
                    self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                    self.focusable_widgets[self.focused_index].focused = True
            elif event.key == pygame.K_RETURN:
                focused_widget = self.focusable_widgets[self.focused_index]
                if focused_widget == self.select_button:
                     for i, cb in enumerate(self.checkboxes):
                        if cb.checked:
                            return "view_details", self.results[i]
                elif focused_widget == self.back_button:
                    return "back", None
                elif focused_widget == self.next_button:
                    return "next_page", None

        for cb in self.checkboxes:
            cb.handle_event(event, self.checkboxes)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back", None
            if self.select_button.rect.collidepoint(event.pos):
                for i, cb in enumerate(self.checkboxes):
                    if cb.checked:
                        return "view_details", self.results[i]
            if self.next_button.rect.collidepoint(event.pos):
                return "next_page", None

        return None, None

    def draw(self):
        if not self.results:
            text_surface = self.font.render("No results found.", True, (255, 255, 255))
            self.screen.blit(text_surface, (50, 50))
        else:
            y_offset = 50
            for i, result in enumerate(self.results):
                self.checkboxes[i].draw(self.screen)
                self.screen.blit(self.images[i], (80, y_offset))
                title = getattr(result, 'title', 'N/A').encode('latin-1', 'replace').decode('latin-1')
                artist = 'N/A'
                if hasattr(result, 'artists') and result.artists:
                    artist = result.artists[0].name.encode('latin-1', 'replace').decode('latin-1')
                title_surface = self.font.render(f"Title: {title}", True, (255, 255, 255))
                artist_surface = self.font.render(f"Artist: {artist}", True, (255, 255, 255))
                self.screen.blit(title_surface, (140, y_offset))
                self.screen.blit(artist_surface, (140, y_offset + 20))
                y_offset += 60

        self.back_button.draw(self.screen)
        self.select_button.draw(self.screen)
        self.next_button.draw(self.screen)

class DetailsViewer:
    def __init__(self, screen, result):
        self.screen = screen
        self.result = result
        self.font = pygame.font.Font(None, 32)
        self.back_button = Button(10, 10, 100, 32, "Back")

        # Fetch full release details for comprehensive data
        self.full_release = d.release(self.result.id)
        self.image_surface = self._load_image()
        self.song_length, self.genres = self._get_song_length_and_genres()

    def _load_image(self):
        if hasattr(self.full_release, 'images') and self.full_release.images:
            image_url = self.full_release.images[0]['uri']
            try:
                headers = {'User-Agent': 'YourApp/1.0'}
                response = requests.get(image_url, headers=headers)
                response.raise_for_status()
                image_data = response.content
                image_file = io.BytesIO(image_data)
                return pygame.image.load(image_file)
            except Exception as e:
                print(f"Error loading image: {e}")
        return None

    def _get_song_length_and_genres(self):
        total_duration_seconds = 0
        genres = []

        if hasattr(self.full_release, 'tracklist') and self.full_release.tracklist:
            for track in self.full_release.tracklist:
                if track.duration:
                    try:
                        # Parse duration string "mm:ss"
                        minutes, seconds = map(int, track.duration.split(':'))
                        total_duration_seconds += (minutes * 60) + seconds
                    except ValueError:
                        # Handle cases where duration might be in an unexpected format
                        pass

        if hasattr(self.full_release, 'genres') and self.full_release.genres:
            genres = self.full_release.genres

        # Convert total seconds back to "HH:MM:SS" or "MM:SS"
        if total_duration_seconds > 0:
            total_duration = str(datetime.timedelta(seconds=total_duration_seconds))
            if len(total_duration.split(':')) == 2: # "M:SS" -> "MM:SS"
                 total_duration = "0" + total_duration
        else:
            total_duration = "N/A"

        return total_duration, genres

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.back_button.rect.collidepoint(event.pos):
            return "back_to_results"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
             return "back_to_results"
        return None

    def draw(self):
        if self.image_surface:
            self.screen.blit(pygame.transform.scale(self.image_surface, (400, 400)), (50, 50))
        else:
            pygame.draw.rect(self.screen, (50,50,50), (50, 50, 400, 400))
            error_text = self.font.render("Image not available", True, (255,255,255))
            self.screen.blit(error_text, (100, 200))

        title = getattr(self.full_release, 'title', 'N/A').encode('latin-1', 'replace').decode('latin-1')
        artist = 'N/A'
        if hasattr(self.full_release, 'artists') and self.full_release.artists:
            artist = self.full_release.artists[0].name.encode('latin-1', 'replace').decode('latin-1')
        year = getattr(self.full_release, 'year', 'N/A')

        genres_text = ", ".join(self.genres) if self.genres else "N/A"

        title_surface = self.font.render(f"Title: {title}", True, (255, 255, 255))
        artist_surface = self.font.render(f"Artist: {artist}", True, (255, 255, 255))
        year_surface = self.font.render(f"Year: {year}", True, (255, 255, 255))
        length_surface = self.font.render(f"Length: {self.song_length}", True, (255, 255, 255))
        genre_surface = self.font.render(f"Genre: {genres_text}", True, (255, 255, 255))

        self.screen.blit(title_surface, (470, 50))
        self.screen.blit(artist_surface, (470, 90))
        self.screen.blit(year_surface, (470, 130))
        self.screen.blit(length_surface, (470, 170))
        self.screen.blit(genre_surface, (470, 210))

        self.back_button.draw(self.screen)


class FullScreenImageViewer:
    def __init__(self, screen, data_bundle):
        self.screen = screen
        self.data_bundle = data_bundle
        self.image_surface = data_bundle['image_surface']
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.create_label_button = Button(screen.get_width() - 150, 10, 140, 32, "Create Label")
        self.focusable_widgets = [self.back_button, self.create_label_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
                return None, None

            focused_widget = self.focusable_widgets[self.focused_index]
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                if focused_widget == self.back_button or event.key == pygame.K_ESCAPE:
                    return "back_to_file_display", None
                elif focused_widget == self.create_label_button:
                    processed_image = extract_label(self.image_surface)
                    result_data = {'label_image': processed_image, 'data_bundle': self.data_bundle}
                    return "show_result", result_data

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_file_display", None
            if self.create_label_button.rect.collidepoint(event.pos):
                processed_image = extract_label(self.image_surface)
                result_data = {'label_image': processed_image, 'data_bundle': self.data_bundle}
                return "show_result", result_data
        return None, None

    def draw(self):
        # Scale image to fit the screen while maintaining aspect ratio
        screen_rect = self.screen.get_rect()
        img_rect = self.image_surface.get_rect()

        if img_rect.width == 0 or img_rect.height == 0:
            return # Avoid division by zero for invalid images

        scale = min(screen_rect.width / img_rect.width, screen_rect.height / img_rect.height)
        new_width = int(img_rect.width * scale)
        new_height = int(img_rect.height * scale)
        scaled_image = pygame.transform.scale(self.image_surface, (new_width, new_height))

        # Center the image
        blit_x = (screen_rect.width - new_width) // 2
        blit_y = (screen_rect.height - new_height) // 2
        self.screen.blit(scaled_image, (blit_x, blit_y))

        for widget in self.focusable_widgets:
            widget.draw(self.screen)


def detect_circular_label(image_bytes):
    """
    v0.00.11: OPTIMIZED with caching and circle data return.
    v0.00.07 FIX: STRICT pre-filter with validation to exclude non-label images.
    This is the PRE-FILTER - must be strict to avoid showing band photos/graphics.
    Returns (is_label, circle_data) tuple:
      - is_label: True only if a valid centered 45rpm label is detected
      - circle_data: (center_x, center_y, radius, rows, cols) or None
    Takes raw image bytes as input (from HTTP response).
    """
    global CIRCLE_DETECTION_CACHE

    try:
        # v0.00.11: Cache lookup by image hash
        img_hash = hashlib.md5(image_bytes).hexdigest()
        if img_hash in CIRCLE_DETECTION_CACHE:
            return CIRCLE_DETECTION_CACHE[img_hash]

        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            result = (False, None)
            CIRCLE_DETECTION_CACHE[img_hash] = result
            return result

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rows = gray.shape[0]
        cols = gray.shape[1]

        # v0.00.07: Enhanced preprocessing for better edge detection
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_clahe = clahe.apply(gray)
        gray_filtered = cv2.bilateralFilter(gray_clahe, 9, 75, 75)

        # v0.00.07 FIX: Use STRICT parameters for pre-filtering
        # Only try 2 strict strategies, not 4 loose ones

        # Strategy 1: Strict detection with enhanced preprocessing
        circles = cv2.HoughCircles(gray_filtered, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                   param1=100, param2=90,  # STRICTER than before (was 85)
                                   minRadius=int(rows * 0.2), maxRadius=int(rows * 0.49))

        if circles is None:
            # Strategy 2: Slightly more flexible with median blur fallback
            gray_median = cv2.medianBlur(gray, 5)
            circles = cv2.HoughCircles(gray_median, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                       param1=100, param2=85,  # Original strictness
                                       minRadius=int(rows * 0.2), maxRadius=int(rows * 0.49))

        # v0.00.07 FIX: Add validation - circle must be centered and properly sized
        if circles is not None:
            for circle in circles[0]:
                center_x, center_y, radius = circle[0], circle[1], circle[2]

                # Check if circle is reasonably centered (stricter than extract_label)
                center_offset_x = abs(center_x - cols / 2) / cols
                center_offset_y = abs(center_y - rows / 2) / rows

                # PRE-FILTER: Only allow 25% offset from center (stricter than 30%)
                if center_offset_x < 0.25 and center_offset_y < 0.25:
                    # Check if radius is in valid 45rpm range
                    radius_ratio = radius / rows
                    if 0.20 <= radius_ratio <= 0.50:  # Stricter range
                        # v0.00.11: Return circle data for reuse
                        result = (True, (center_x, center_y, radius, rows, cols))
                        # Cache management
                        if len(CIRCLE_DETECTION_CACHE) >= MAX_CACHE_SIZE:
                            CIRCLE_DETECTION_CACHE.clear()
                        CIRCLE_DETECTION_CACHE[img_hash] = result
                        return result

        result = (False, None)
        if len(CIRCLE_DETECTION_CACHE) >= MAX_CACHE_SIZE:
            CIRCLE_DETECTION_CACHE.clear()
        CIRCLE_DETECTION_CACHE[img_hash] = result
        return result

    except Exception as e:
        print(f"Error in detect_circular_label: {e}")
        return (False, None)


def download_and_filter_images_parallel(release, artist_name=None, song_title=None, max_workers=5):
    """
    v0.00.12: Download and filter release images in parallel with EARLY OCR validation.
    v0.00.11: Download and filter release images in parallel using ThreadPoolExecutor.
    Returns list of (image_bytes, circle_data) tuples for images containing labels.

    NEW in v0.00.12: If artist_name and song_title provided, runs OCR validation FIRST
    before circle detection. Only processes images that pass OCR text match.

    This is 3-5x faster than sequential downloads for multi-image releases.
    """
    if not release.images:
        return []

    filtered_images = []
    print(f"Found {len(release.images)} images, downloading and filtering in parallel (workers={max_workers})...")
    if artist_name and song_title:
        print(f"  EARLY OCR VALIDATION ENABLED: Checking for '{artist_name}' - '{song_title}'")

    def download_single_image(idx, img_info):
        """Worker function to download, OCR validate, and detect circles for one image"""
        try:
            img_response = requests.get(img_info['uri'], headers={'User-Agent': 'YourApp/1.0'}, timeout=10)
            img_response.raise_for_status()
            img_bytes = img_response.content

            # v0.00.12: NEW - Run OCR validation FIRST if artist/title provided
            if artist_name and song_title:
                extracted_text = extract_text_from_image_bytes(img_bytes, debug=False)
                ocr_match = check_ocr_text_match(extracted_text, artist_name, song_title, debug=False)

                if not ocr_match:
                    print(f"  Image {idx+1}/{len(release.images)}: OCR text mismatch, skipping ✗")
                    return None
                else:
                    print(f"  Image {idx+1}/{len(release.images)}: OCR match found ✓")

            # Check if image contains circular patterns (45rpm label)
            is_label, circle_data = detect_circular_label(img_bytes)

            if is_label:
                print(f"  Image {idx+1}/{len(release.images)}: LABEL DETECTED ✓")
                return (img_bytes, circle_data)
            else:
                print(f"  Image {idx+1}/{len(release.images)}: No circles, skipping")
                return None

        except Exception as e:
            print(f"  Image {idx+1}: Error downloading - {e}")
            return None

    # v0.00.11: Use ThreadPoolExecutor for parallel downloads
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_idx = {executor.submit(download_single_image, idx, img_info): idx
                         for idx, img_info in enumerate(release.images)}

        # Collect results as they complete
        for future in as_completed(future_to_idx):
            result = future.result()
            if result is not None:
                filtered_images.append(result)

    elapsed = time.time() - start_time
    print(f"Parallel download complete: {len(filtered_images)} labels found in {elapsed:.2f}s")

    return filtered_images


def validate_final_record(image_path, debug=False):
    """
    v0.00.08: Validates that the final combined record image is properly formed.
    Checks for:
    1. Outer circle (label edge)
    2. Inner hole/adaptor area
    3. Proper concentric circle structure

    Returns True if image is valid, False otherwise.
    """
    try:
        # Load the final image
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            if debug:
                print(f"Validation FAILED: Could not load image {image_path}")
            return False

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rows, cols = gray.shape

        # Enhanced preprocessing for better detection
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_clahe = clahe.apply(gray)
        gray_filtered = cv2.bilateralFilter(gray_clahe, 9, 75, 75)

        # Detect circles with multiple strategies
        strategies = [
            {'image': gray_filtered, 'param1': 100, 'param2': 80},
            {'image': cv2.medianBlur(gray, 5), 'param1': 100, 'param2': 70},
            {'image': gray_filtered, 'param1': 80, 'param2': 60}
        ]

        all_circles = None
        for strategy in strategies:
            circles = cv2.HoughCircles(
                strategy['image'],
                cv2.HOUGH_GRADIENT,
                1,
                rows / 8,
                param1=strategy['param1'],
                param2=strategy['param2'],
                minRadius=int(rows * 0.15),
                maxRadius=int(rows * 0.50)
            )
            if circles is not None:
                all_circles = circles
                break

        if all_circles is None:
            if debug:
                print("Validation FAILED: No circles detected in final image")
            return False

        # Sort circles by radius (largest first)
        circles_sorted = sorted(all_circles[0], key=lambda c: c[2], reverse=True)

        # Check for at least one large circle (outer label edge)
        largest_circle = circles_sorted[0]
        center_x, center_y, radius = largest_circle[0], largest_circle[1], largest_circle[2]

        # Validate the circle is reasonably centered and sized
        center_offset_x = abs(center_x - cols / 2) / cols
        center_offset_y = abs(center_y - rows / 2) / rows

        if center_offset_x > 0.15 or center_offset_y > 0.15:
            if debug:
                print(f"Validation FAILED: Circle not centered (offset: {center_offset_x:.2f}, {center_offset_y:.2f})")
            return False

        radius_ratio = radius / rows
        if radius_ratio < 0.30 or radius_ratio > 0.52:
            if debug:
                print(f"Validation FAILED: Circle radius out of range (ratio: {radius_ratio:.2f})")
            return False

        # Check for adaptor presence in center area
        center_region_size = int(rows * 0.20)  # 20% of image size
        center_y_int, center_x_int = int(center_y), int(center_x)
        half_region = center_region_size // 2

        # Extract center region (where adaptor should be)
        y_start = max(0, center_y_int - half_region)
        y_end = min(rows, center_y_int + half_region)
        x_start = max(0, center_x_int - half_region)
        x_end = min(cols, center_x_int + half_region)

        center_region = img[y_start:y_end, x_start:x_end]

        # Check if center region has color variation (adaptor is colored, not just black/white)
        if center_region.size > 0:
            hsv_center = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
            saturation = hsv_center[:, :, 1]
            mean_saturation = np.mean(saturation)

            # Adaptor should have some color (saturation > threshold)
            if mean_saturation < 20:
                if debug:
                    print(f"Validation FAILED: Center region lacks color (saturation: {mean_saturation:.2f})")
                return False

        if debug:
            print(f"Validation PASSED: Image is properly formed (radius ratio: {radius_ratio:.2f}, center offset: {center_offset_x:.2f}, {center_offset_y:.2f})")

        return True

    except Exception as e:
        if debug:
            print(f"Validation ERROR: {e}")
        return False


def extract_text_from_image_bytes(image_bytes, debug=False):
    """
    v0.00.12: Extract text from raw image bytes using OCR with caching.
    Takes image bytes directly (from HTTP response) instead of file path.
    Returns extracted text as a string, or empty string if OCR fails/unavailable.
    """
    global OCR_CACHE

    if debug:
        print(f"OCR: Extracting text from image bytes...")

    if not OCR_AVAILABLE:
        if debug:
            print("OCR: Skipped (pytesseract not installed)")
        return ""

    try:
        # v0.00.12: Check cache using image hash
        img_hash = hashlib.md5(image_bytes).hexdigest()

        if img_hash in OCR_CACHE:
            if debug:
                print(f"OCR: Cache hit! Skipping expensive OCR extraction")
            return OCR_CACHE[img_hash]

        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            if debug:
                print(f"OCR: Failed to decode image bytes")
            return ""

        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply preprocessing to improve OCR accuracy
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)

        # Extract text using pytesseract
        text = pytesseract.image_to_string(denoised, config='--psm 6')

        if debug:
            print(f"OCR: ===== FULL EXTRACTED TEXT =====")
            print(text)
            print(f"OCR: ===== END EXTRACTED TEXT =====")
            print(f"OCR: Total characters extracted: {len(text)}")

        # Store in cache
        if len(OCR_CACHE) >= MAX_CACHE_SIZE:
            OCR_CACHE.clear()
        OCR_CACHE[img_hash] = text

        return text

    except Exception as e:
        if debug:
            print(f"OCR: Error extracting text: {e}")
        return ""


def extract_text_from_label(image_path, debug=False):
    """
    v0.00.11: Extract text from label image using OCR with caching.
    v0.00.09: Extract text from label image using OCR.
    Returns extracted text as a string, or empty string if OCR fails/unavailable.
    """
    global OCR_CACHE

    if debug:
        print(f"OCR: Extracting text from {image_path}...")

    if not OCR_AVAILABLE:
        if debug:
            print("OCR: Skipped (pytesseract not installed)")
        return ""

    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            if debug:
                print(f"OCR: Failed to load image {image_path}")
            return ""

        # v0.00.11: Check cache using image hash
        img_bytes = cv2.imencode('.png', img)[1].tobytes()
        img_hash = hashlib.md5(img_bytes).hexdigest()

        if img_hash in OCR_CACHE:
            if debug:
                print(f"OCR: Cache hit! Skipping expensive OCR extraction")
            return OCR_CACHE[img_hash]

        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply preprocessing to improve OCR accuracy
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)

        # Extract text using pytesseract
        text = pytesseract.image_to_string(denoised, config='--psm 6')

        if debug:
            print(f"OCR: ===== FULL EXTRACTED TEXT =====")
            print(text)
            print(f"OCR: ===== END EXTRACTED TEXT =====")
            print(f"OCR: Total characters extracted: {len(text)}")

        # v0.00.11: Store in cache
        if len(OCR_CACHE) >= MAX_CACHE_SIZE:
            OCR_CACHE.clear()
        OCR_CACHE[img_hash] = text

        return text

    except Exception as e:
        if debug:
            print(f"OCR: Error extracting text: {e}")
        return ""


def similarity_ratio(str1, str2):
    """Calculate similarity ratio between two strings (0.0 to 1.0)"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def check_ocr_text_match(extracted_text, artist_name, song_title, debug=False):
    """
    v0.00.12: Check if extracted OCR text contains artist and title.
    Returns True if both artist AND title are found with sufficient match ratio.
    Similar to validate_label_text but works with pre-extracted text.
    """
    if debug:
        print(f"OCR MATCH CHECK: Looking for artist '{artist_name}' and title '{song_title}'")

    if not extracted_text or len(extracted_text.strip()) < 5:
        if debug:
            print("OCR MATCH CHECK: FAILED (no text extracted)")
        return False

    # Clean and normalize text
    extracted_text_clean = extracted_text.lower().strip()
    artist_clean = artist_name.lower().strip()
    title_clean = song_title.lower().strip()

    # Check for artist name in extracted text
    artist_match_ratio = 0.0
    # Try matching full artist name
    if artist_clean in extracted_text_clean:
        artist_match_ratio = 1.0
    else:
        # Try fuzzy matching (artist name might be partial or OCR imperfect)
        for word in artist_clean.split():
            if len(word) > 3:  # Only check words longer than 3 chars
                if word in extracted_text_clean:
                    artist_match_ratio = max(artist_match_ratio, 0.7)
                else:
                    # Check similarity with each word in extracted text
                    for extracted_word in extracted_text_clean.split():
                        if len(extracted_word) > 3:
                            ratio = similarity_ratio(word, extracted_word)
                            artist_match_ratio = max(artist_match_ratio, ratio)

    # Check for song title in extracted text
    title_match_ratio = 0.0
    # Try matching full title
    if title_clean in extracted_text_clean:
        title_match_ratio = 1.0
    else:
        # Try fuzzy matching (title might be partial or OCR imperfect)
        for word in title_clean.split():
            if len(word) > 3:  # Only check words longer than 3 chars
                if word in extracted_text_clean:
                    title_match_ratio = max(title_match_ratio, 0.7)
                else:
                    # Check similarity with each word in extracted text
                    for extracted_word in extracted_text_clean.split():
                        if len(extracted_word) > 3:
                            ratio = similarity_ratio(word, extracted_word)
                            title_match_ratio = max(title_match_ratio, ratio)

    # Require BOTH artist AND title to match
    artist_threshold = 0.50  # Artist must be at least 50% match
    title_threshold = 0.50   # Title must be at least 50% match
    passed = (artist_match_ratio >= artist_threshold) and (title_match_ratio >= title_threshold)

    if debug:
        print(f"")
        print(f"OCR MATCH CHECK RESULTS:")
        print(f"  Artist to find: '{artist_name}'")
        print(f"  Title to find:  '{song_title}'")
        print(f"  Artist match score: {artist_match_ratio:.2f} (threshold: {artist_threshold})")
        print(f"  Title match score:  {title_match_ratio:.2f} (threshold: {title_threshold})")
        print(f"")
        if passed:
            print(f"✓ OCR MATCH CHECK: PASSED (both artist AND title found)")
        else:
            if artist_match_ratio < artist_threshold and title_match_ratio < title_threshold:
                print(f"✗ OCR MATCH CHECK: FAILED (neither artist nor title found)")
            elif artist_match_ratio < artist_threshold:
                print(f"✗ OCR MATCH CHECK: FAILED (artist not found, only title)")
            else:
                print(f"✗ OCR MATCH CHECK: FAILED (title not found, only artist)")
        print(f"")

    return passed


def validate_label_text(image_path, artist_name, song_title, debug=False):
    """
    v0.00.09: Validate that label contains artist and/or title text.
    Returns True if text validation passes, False otherwise.
    If OCR is unavailable, returns True (don't block on missing OCR).

    Validation passes if:
    - Artist name has >60% match in OCR text, OR
    - Song title has >60% match in OCR text
    """
    if debug:
        print(f"=== OCR TEXT VALIDATION START ===")
        print(f"Checking image: {image_path}")
        print(f"Looking for artist: '{artist_name}' or title: '{song_title}'")
        print(f"OCR_AVAILABLE: {OCR_AVAILABLE}")

    if not OCR_AVAILABLE:
        if debug:
            print("OCR text validation: SKIPPED (pytesseract not available)")
        return True  # Don't block if OCR unavailable

    try:
        # Extract text from label
        extracted_text = extract_text_from_label(image_path, debug=debug)

        if not extracted_text or len(extracted_text.strip()) < 5:
            if debug:
                print("OCR text validation: FAILED (no text extracted)")
            return False

        # Clean and normalize text
        extracted_text_clean = extracted_text.lower().strip()
        artist_clean = artist_name.lower().strip()
        title_clean = song_title.lower().strip()

        # Check for artist name in extracted text
        artist_match_ratio = 0.0
        # Try matching full artist name
        if artist_clean in extracted_text_clean:
            artist_match_ratio = 1.0
        else:
            # Try fuzzy matching (artist name might be partial or OCR imperfect)
            for word in artist_clean.split():
                if len(word) > 3:  # Only check words longer than 3 chars
                    if word in extracted_text_clean:
                        artist_match_ratio = max(artist_match_ratio, 0.7)
                    else:
                        # Check similarity with each word in extracted text
                        for extracted_word in extracted_text_clean.split():
                            if len(extracted_word) > 3:
                                ratio = similarity_ratio(word, extracted_word)
                                artist_match_ratio = max(artist_match_ratio, ratio)

        # Check for song title in extracted text
        title_match_ratio = 0.0
        # Try matching full title
        if title_clean in extracted_text_clean:
            title_match_ratio = 1.0
        else:
            # Try fuzzy matching (title might be partial or OCR imperfect)
            for word in title_clean.split():
                if len(word) > 3:  # Only check words longer than 3 chars
                    if word in extracted_text_clean:
                        title_match_ratio = max(title_match_ratio, 0.7)
                    else:
                        # Check similarity with each word in extracted text
                        for extracted_word in extracted_text_clean.split():
                            if len(extracted_word) > 3:
                                ratio = similarity_ratio(word, extracted_word)
                                title_match_ratio = max(title_match_ratio, ratio)

        # v0.00.10 FIX: Require BOTH artist AND title to match (not just one)
        # This prevents accepting labels with just the artist name but wrong song
        artist_threshold = 0.50  # Artist must be at least 50% match
        title_threshold = 0.50   # Title must be at least 50% match
        passed = (artist_match_ratio >= artist_threshold) and (title_match_ratio >= title_threshold)

        if debug:
            print(f"")
            print(f"OCR MATCHING RESULTS:")
            print(f"  Artist to find: '{artist_name}'")
            print(f"  Title to find:  '{song_title}'")
            print(f"  Artist match score: {artist_match_ratio:.2f} (threshold: {artist_threshold})")
            print(f"  Title match score:  {title_match_ratio:.2f} (threshold: {title_threshold})")
            print(f"")
            if passed:
                print(f"✓ OCR text validation: PASSED (both artist AND title found)")
            else:
                if artist_match_ratio < artist_threshold and title_match_ratio < title_threshold:
                    print(f"✗ OCR text validation: FAILED (neither artist nor title found)")
                elif artist_match_ratio < artist_threshold:
                    print(f"✗ OCR text validation: FAILED (artist not found, only title)")
                else:
                    print(f"✗ OCR text validation: FAILED (title not found, only artist)")
            print(f"")

        return passed

    except Exception as e:
        if debug:
            print(f"OCR text validation ERROR: {e}")
        return True  # Don't block on errors


def extract_label(pygame_surface, debug=False):
    """
    v0.00.07: Enhanced circle detection with multi-strategy approach and validation.
    Takes a pygame surface, finds the 45rpm label using circle detection,
    and returns a new cropped pygame surface of just the label.
    """
    try:
        # 1. Convert Pygame surface to OpenCV image
        view = pygame.surfarray.pixels3d(pygame_surface)
        img = cv2.cvtColor(view.transpose([1, 0, 2]), cv2.COLOR_RGB2BGR)
        gray_original = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rows = gray_original.shape[0]
        cols = gray_original.shape[1]

        # v0.00.07: Enhanced preprocessing
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_clahe = clahe.apply(gray_original)

        # Apply bilateral filter to reduce noise while preserving edges
        gray_filtered = cv2.bilateralFilter(gray_clahe, 9, 75, 75)

        # Keep median blur version for fallback
        gray_median = cv2.medianBlur(gray_original, 5)

        # v0.00.07: Define multiple detection strategies
        strategies = [
            # Strategy 1: Original parameters with enhanced preprocessing
            {
                'name': 'Enhanced preprocessing (param2=85)',
                'image': gray_filtered,
                'param1': 100,
                'param2': 85,
                'minRadius': int(rows * 0.2),
                'maxRadius': int(rows * 0.49)
            },
            # Strategy 2: More sensitive detection
            {
                'name': 'More sensitive (param2=70)',
                'image': gray_filtered,
                'param1': 100,
                'param2': 70,
                'minRadius': int(rows * 0.2),
                'maxRadius': int(rows * 0.49)
            },
            # Strategy 3: Wider radius range with median blur
            {
                'name': 'Wider radius range (param2=75)',
                'image': gray_median,
                'param1': 100,
                'param2': 75,
                'minRadius': int(rows * 0.15),
                'maxRadius': int(rows * 0.55)
            },
            # Strategy 4: Very sensitive for difficult cases
            {
                'name': 'Very sensitive (param2=60)',
                'image': gray_filtered,
                'param1': 80,
                'param2': 60,
                'minRadius': int(rows * 0.15),
                'maxRadius': int(rows * 0.55)
            }
        ]

        # v0.00.07: Try each strategy and validate results
        best_circle = None
        best_strategy = None

        for strategy in strategies:
            circles = cv2.HoughCircles(
                strategy['image'],
                cv2.HOUGH_GRADIENT,
                1,
                rows / 8,
                param1=strategy['param1'],
                param2=strategy['param2'],
                minRadius=strategy['minRadius'],
                maxRadius=strategy['maxRadius']
            )

            if circles is not None:
                # v0.00.07: Validate detected circles
                for circle in circles[0]:
                    center_x, center_y, radius = circle[0], circle[1], circle[2]

                    # Check if circle is reasonably centered and sized
                    # Circle should be somewhat near the center of the image
                    center_offset_x = abs(center_x - cols / 2) / cols
                    center_offset_y = abs(center_y - rows / 2) / rows

                    # Allow up to 30% offset from center
                    if center_offset_x < 0.3 and center_offset_y < 0.3:
                        # Check if radius is reasonable (20% to 49% of image height)
                        radius_ratio = radius / rows
                        if 0.18 <= radius_ratio <= 0.52:
                            best_circle = circle
                            best_strategy = strategy['name']
                            if debug:
                                print(f"Circle detected using strategy: {best_strategy}")
                            break

                if best_circle is not None:
                    break

        # 2. If we found a valid circle, extract the label
        if best_circle is not None:
            center_x, center_y, r_large = int(best_circle[0]), int(best_circle[1]), int(best_circle[2])

            # Derive the inner hole based on a standard 45rpm ratio
            r_small = int(r_large * 0.43)

            # 3. Create Mask
            mask = np.zeros_like(gray_original)
            cv2.circle(mask, (center_x, center_y), r_large, 255, -1)
            cv2.circle(mask, (center_x, center_y), r_small, 0, -1)

            # 4. Apply Mask and Crop
            img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            img_rgba[:, :, 3] = mask

            x, y, w, h = cv2.boundingRect(mask)
            cropped_label = img_rgba[y:y+h, x:x+w]

            # 5. Convert back to Pygame surface
            cropped_label_rgb = cv2.cvtColor(cropped_label, cv2.COLOR_BGRA2RGBA)
            return pygame.image.frombuffer(cropped_label_rgb.tobytes(), cropped_label_rgb.shape[1::-1], "RGBA")
        else:
            raise ValueError("No valid circles detected after trying all strategies. Image may not contain a centered 45rpm label.")

    except Exception as e:
        import traceback
        print(f"Error in extract_label: {e}")
        traceback.print_exc()
        return None

class ResultViewer:
    def __init__(self, screen, result_data):
        self.screen = screen
        self.image_surface = result_data['label_image']
        self.data_bundle = result_data['data_bundle']
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.use_label_checkbox = Checkbox(150, 15, 20, 20, "")
        self.font = pygame.font.Font(None, 32)

        self.focusable_widgets = [self.back_button, self.use_label_checkbox]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

    def _save_label_image_to_disk(self, resized_surface):
        """Background worker: Only does file I/O, no pygame surface operations"""
        try:
            # Define the save path (local directory)
            save_path = 'new_cutout_label.png'

            # Save the surface as a transparent PNG
            pygame.image.save(resized_surface, save_path)
            print(f"Label saved to {save_path}")

        except Exception as e:
            print(f"Error saving label image: {e}")

    def handle_event(self, event):
        was_checked_before = self.use_label_checkbox.checked

        # Pass event to the checkbox first to handle its state
        self.use_label_checkbox.handle_event(event, [self.use_label_checkbox])

        # Check if the checkbox was just toggled to checked
        if self.use_label_checkbox.checked and not was_checked_before:
            if not self.image_surface:
                print("No image to save.")
                return None
            else:
                # Force immediate visual update to show the checkbox checked
                self.screen.fill((30, 30, 30))
                self.draw()
                pygame.display.flip()

                # v0.00.02: Save label and generate preview (Option B - pre-generate file)
                # Do pygame operations in main thread to avoid surface locking issues
                resized_surface = self.image_surface

                # Save new_cutout_label.png
                save_thread = threading.Thread(target=self._save_label_image_to_disk, args=(resized_surface,))
                save_thread.start()
                save_thread.join()  # Wait for save to complete

                # v0.00.05: Generate final_record.png at CORRECT size (420x420)
                print("Generating preview with adaptor (420x420)...")
                success = label_pressing_module.combine_pngs(
                    label_path='new_cutout_label.png',
                    adaptor_path='adaptor.png',
                    output_path='final_record.png',
                    size=(420, 420),
                    base_record_path='blank_record.png'
                )

                if not success:
                    print("ERROR: Failed to generate preview image")
                    return None

                # v0.00.08: Validate the final combined image before showing preview (structure)
                is_valid = validate_final_record('final_record.png', debug=True)

                if not is_valid:
                    print("ERROR: Final image failed validation (malformed label/adaptor)")
                    print("⚠ Please try a different label image using arrow keys on FileDisplay screen")
                    return None

                # v0.00.09: Validate label text contains artist/title using OCR
                # v0.00.10 FIX: Use ORIGINAL filename artist/title for validation
                artist_to_check = self.data_bundle.get('filename_artist', self.data_bundle['discogs_artist'])
                title_to_check = self.data_bundle.get('filename_title', self.data_bundle['discogs_title'])
                text_valid = validate_label_text('new_cutout_label.png',
                                                  artist_to_check,
                                                  title_to_check,
                                                  debug=True)

                if not text_valid:
                    print("ERROR: Final image failed OCR text validation (artist/title not found on label)")
                    print("⚠ Please try a different label image using arrow keys on FileDisplay screen")
                    return None

                # v0.00.02: Show preview comparison screen instead of confirmation (only if all validations passed)
                preview_data = {
                    'cropped_label_surface': self.image_surface,
                    'data_bundle': self.data_bundle
                }
                return "show_preview", preview_data

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
                return None

            focused_widget = self.focusable_widgets[self.focused_index]
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                if focused_widget == self.back_button or event.key == pygame.K_ESCAPE:
                    return "back_to_full_screen"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_full_screen"

        return None

    def draw(self):
        if self.image_surface:
            # Center the result on the screen
            screen_rect = self.screen.get_rect()
            img_rect = self.image_surface.get_rect(center=screen_rect.center)
            self.screen.blit(self.image_surface, img_rect)
        else:
            # Display an error message if no image was generated
            error_font = pygame.font.Font(None, 50)
            error_surf = error_font.render("Label Extraction Failed", True, (255, 100, 100))
            error_rect = error_surf.get_rect(center=self.screen.get_rect().center)
            self.screen.blit(error_surf, error_rect)

        self.back_button.draw(self.screen)
        self.use_label_checkbox.draw(self.screen)
        label_surf = self.font.render("Use This Label?", True, (255, 255, 255))
        self.screen.blit(label_surf, (self.use_label_checkbox.rect.x + 30, self.use_label_checkbox.rect.y - 4))


class PreviewComparisonScreen:
    """
    v0.00.02: Shows side-by-side comparison of original cropped label vs final label with adaptor
    Left: Original cropped Discogs label
    Right: Final result with adaptor (loaded from final_record.png)
    """
    def __init__(self, screen, preview_data):
        self.screen = screen
        self.cropped_label_surface = preview_data['cropped_label_surface']
        self.data_bundle = preview_data['data_bundle']

        # Load final_record.png (already generated by ResultViewer)
        try:
            self.final_record_surface = pygame.image.load('final_record.png')
            print("Loaded final_record.png for preview")
        except Exception as e:
            print(f"Error loading final_record.png: {e}")
            self.final_record_surface = None

        # Buttons
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.cancel_button = Button(screen.get_width() - 120, 10, 100, 32, "Cancel")
        self.are_you_sure_button = Button((screen.get_width() - 200) // 2, screen.get_height() - 60, 200, 40, "Are You Sure?")

        self.focusable_widgets = [self.back_button, self.cancel_button, self.are_you_sure_button]
        self.focused_index = 2  # Focus on "Are You Sure?" by default
        self.focusable_widgets[self.focused_index].focused = True

        # Fonts
        self.font_header = pygame.font.Font(None, 36)
        self.font_label = pygame.font.Font(None, 24)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
                return None

            focused_widget = self.focusable_widgets[self.focused_index]
            if event.key == pygame.K_RETURN:
                if focused_widget == self.are_you_sure_button:
                    # Proceed to confirmation screen (files already generated)
                    confirmation_data = {
                        'label_image': self.final_record_surface,
                        'data_bundle': self.data_bundle
                    }
                    return "show_confirmation", confirmation_data
                elif focused_widget == self.back_button or focused_widget == self.cancel_button:
                    return "back_to_result_viewer", None
            elif event.key == pygame.K_ESCAPE:
                return "back_to_result_viewer", None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos) or self.cancel_button.rect.collidepoint(event.pos):
                return "back_to_result_viewer", None
            if self.are_you_sure_button.rect.collidepoint(event.pos):
                # Proceed to confirmation screen
                confirmation_data = {
                    'label_image': self.final_record_surface,
                    'data_bundle': self.data_bundle
                }
                return "show_confirmation", confirmation_data

        return None

    def draw(self):
        # Header
        header = self.font_header.render("Preview Label Comparison", True, (255, 255, 255))
        header_x = (self.screen.get_width() - header.get_width()) // 2
        self.screen.blit(header, (header_x, 50))

        # Calculate layout for side-by-side images
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        image_size = 300  # Display size for each image
        spacing = 100  # Space between images

        # Left image position (Original cropped label)
        left_x = (screen_width // 2) - image_size - (spacing // 2)
        left_y = (screen_height - image_size) // 2

        # Right image position (Final with adaptor)
        right_x = (screen_width // 2) + (spacing // 2)
        right_y = left_y

        # Draw left side: Original cropped label
        if self.cropped_label_surface:
            scaled_left = pygame.transform.scale(self.cropped_label_surface, (image_size, image_size))
            self.screen.blit(scaled_left, (left_x, left_y))

            # Label below
            label_left = self.font_label.render("Original Label", True, (200, 200, 200))
            label_x = left_x + (image_size - label_left.get_width()) // 2
            self.screen.blit(label_left, (label_x, left_y + image_size + 10))

        # Draw right side: Final with adaptor
        if self.final_record_surface:
            scaled_right = pygame.transform.scale(self.final_record_surface, (image_size, image_size))
            self.screen.blit(scaled_right, (right_x, right_y))

            # Label below
            label_right = self.font_label.render("With Adaptor", True, (200, 200, 200))
            label_x = right_x + (image_size - label_right.get_width()) // 2
            self.screen.blit(label_right, (label_x, right_y + image_size + 10))
        else:
            # Error message if final_record.png failed to load
            error_surf = self.font_label.render("Error loading preview", True, (255, 100, 100))
            error_x = right_x + (image_size - error_surf.get_width()) // 2
            error_y = right_y + (image_size // 2)
            self.screen.blit(error_surf, (error_x, error_y))

        # Draw arrow between images
        arrow_surf = self.font_header.render("→", True, (255, 255, 0))
        arrow_x = (screen_width - arrow_surf.get_width()) // 2
        arrow_y = left_y + (image_size // 2) - (arrow_surf.get_height() // 2)
        self.screen.blit(arrow_surf, (arrow_x, arrow_y))

        # Draw buttons
        self.back_button.draw(self.screen)
        self.cancel_button.draw(self.screen)

        # Draw "Are You Sure?" button in green
        pygame.draw.rect(self.screen, (0, 200, 0), self.are_you_sure_button.rect)
        button_text = self.font_label.render(self.are_you_sure_button.text, True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=self.are_you_sure_button.rect.center)
        self.screen.blit(button_text, button_text_rect)

        # Draw focus indicator on "Are You Sure?" if focused
        if self.are_you_sure_button.focused:
            pygame.draw.rect(self.screen, (255, 255, 0), self.are_you_sure_button.rect, 3)


class FinalRecordViewer:
    """
    v0.00.06: Display final_record.png (420x420) with metadata and Use This Label functionality
    Opened when user clicks the adaptor preview thumbnail on FileDisplay
    """
    def __init__(self, screen, data_bundle):
        self.screen = screen
        self.data_bundle = data_bundle
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.use_label_checkbox = Checkbox(150, 15, 20, 20, "")
        self.font_header = pygame.font.Font(None, 32)
        self.font_metadata = pygame.font.Font(None, 24)

        # Load final_record.png (420x420)
        try:
            self.final_record_surface = pygame.image.load('final_record.png')
            print("Loaded final_record.png (420x420) for full-size viewing")
        except Exception as e:
            print(f"Error loading final_record.png: {e}")
            self.final_record_surface = None

        self.focusable_widgets = [self.back_button, self.use_label_checkbox]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

    def handle_event(self, event):
        # v0.00.06: Check back button FIRST before checkbox handles event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_file_display", None

        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
                return None
            elif event.key == pygame.K_RETURN:
                return "back_to_file_display", None
            elif event.key == pygame.K_ESCAPE:
                return "back_to_file_display", None

        # Handle checkbox toggle (after button checks)
        was_checked_before = self.use_label_checkbox.checked
        self.use_label_checkbox.handle_event(event, [self.use_label_checkbox])

        # Check if checkbox was just toggled to checked
        if self.use_label_checkbox.checked and not was_checked_before:
            # Files already generated (new_cutout_label.png and final_record.png exist)
            # Go directly to ConfirmationScreen
            confirmation_data = {
                'label_image': self.final_record_surface,
                'data_bundle': self.data_bundle
            }
            return "show_confirmation", confirmation_data

        return None

    def draw(self):
        # Header
        header = self.font_header.render("Final Record (420x420)", True, (255, 255, 255))
        header_x = (self.screen.get_width() - header.get_width()) // 2
        self.screen.blit(header, (header_x, 50))

        # Display final_record.png at its original size (420x420) centered
        if self.final_record_surface:
            # Center the 420x420 image on screen (slightly higher to make room for metadata)
            screen_center_x = self.screen.get_width() // 2
            image_x = screen_center_x - 210  # 420/2 = 210
            image_y = 100

            self.screen.blit(self.final_record_surface, (image_x, image_y))

            # v0.00.06: Display metadata below image
            metadata_y = image_y + 440
            metadata_x = 50

            # Artist
            artist = self.data_bundle.get('discogs_artist', 'N/A')
            artist_surf = self.font_metadata.render(f"Artist: {artist}", True, (255, 255, 255))
            self.screen.blit(artist_surf, (metadata_x, metadata_y))

            # Title
            title = self.data_bundle.get('discogs_title', 'N/A')
            title_surf = self.font_metadata.render(f"Title: {title}", True, (255, 255, 255))
            self.screen.blit(title_surf, (metadata_x, metadata_y + 30))

            # Year
            year = self.data_bundle.get('discogs_year', 'N/A')
            year_surf = self.font_metadata.render(f"Year: {year}", True, (255, 255, 255))
            self.screen.blit(year_surf, (metadata_x, metadata_y + 60))

            # Genre
            genres = self.data_bundle.get('discogs_genres', 'N/A')
            if isinstance(genres, list):
                genres = ', '.join(genres)
            genre_surf = self.font_metadata.render(f"Genre: {genres}", True, (255, 255, 255))
            self.screen.blit(genre_surf, (metadata_x, metadata_y + 90))

        else:
            # Error message
            error_surf = self.font_header.render("Error loading final_record.png", True, (255, 100, 100))
            error_x = (self.screen.get_width() - error_surf.get_width()) // 2
            error_y = self.screen.get_height() // 2
            self.screen.blit(error_surf, (error_x, error_y))

        # Draw back button and checkbox
        self.back_button.draw(self.screen)
        self.use_label_checkbox.draw(self.screen)
        label_surf = self.font_header.render("Use This Label?", True, (255, 255, 255))
        self.screen.blit(label_surf, (self.use_label_checkbox.rect.x + 30, self.use_label_checkbox.rect.y - 4))


class UpdatedTagsViewer:
    def __init__(self, screen, data):
        self.screen = screen
        self.filename = data['filename']
        self.updated_tags = data['updated_tags']

        self.font_header = pygame.font.Font(None, 32)
        self.font_label = pygame.font.Font(None, 22)
        self.font_data = pygame.font.Font(None, 22)

        # Load album art image if present
        self.album_art_surface = None
        if self.updated_tags and self.updated_tags.get('image_data'):
            try:
                image_file = io.BytesIO(self.updated_tags['image_data'])
                self.album_art_surface = pygame.image.load(image_file)
            except pygame.error as e:
                print(f"Error loading album art image: {e}")

        self.next_music_file_button = Button(screen.get_width() / 2 - 110, 600, 220, 32, "Next Music File")
        self.focusable_widgets = [self.next_music_file_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "continue", None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_music_file_button.rect.collidepoint(event.pos):
                return "continue", None

        return None, None

    def draw(self):
        # Header
        header = self.font_header.render("Updated ID3 Tags", True, (0, 255, 0))
        self.screen.blit(header, (50, 50))

        # Filename
        filename_label = self.font_label.render("File:", True, (200, 200, 200))
        filename_data = self.font_data.render(self.filename, True, (255, 255, 255))
        self.screen.blit(filename_label, (50, 100))
        self.screen.blit(filename_data, (50 + filename_label.get_width() + 10, 100))

        # Display album art image (right side)
        if self.album_art_surface:
            # Scale to 300x300 thumbnail
            thumb_size = 300
            scaled_image = pygame.transform.scale(self.album_art_surface, (thumb_size, thumb_size))
            image_x = self.screen.get_width() - thumb_size - 50
            image_y = 150
            self.screen.blit(scaled_image, (image_x, image_y))

            # Label under image
            art_label = self.font_label.render("Album Art (APIC)", True, (200, 200, 200))
            label_rect = art_label.get_rect(center=(image_x + thumb_size // 2, image_y + thumb_size + 10))
            self.screen.blit(art_label, label_rect)

        # Display updated tags in column format (left side)
        y_offset = 150
        x_pos = 50

        if self.updated_tags:
            tags_to_draw = [
                ("Artist Tag:", self.updated_tags.get('artist', 'N/A')),
                ("Title Tag:", self.updated_tags.get('title', 'N/A')),
                ("Album Tag:", self.updated_tags.get('album', 'N/A')),
                ("Genre Tag:", self.updated_tags.get('genre', 'N/A')),
                ("Year Tag:", self.updated_tags.get('year', 'N/A')),
                ("Comment:", self.updated_tags.get('comment', 'N/A')),
            ]

            for label, value in tags_to_draw:
                label_surf = self.font_label.render(label + " ", True, (200, 200, 200))
                self.screen.blit(label_surf, (x_pos, y_offset))

                value_text = str(value)
                if len(value_text) > 60:
                    value_text = value_text[:57] + '...'

                data_surf = self.font_data.render(value_text, True, (255, 255, 255))
                self.screen.blit(data_surf, (x_pos + label_surf.get_width(), y_offset))

                y_offset += 30
        else:
            error_surf = self.font_data.render("Failed to read updated tags", True, (255, 100, 100))
            self.screen.blit(error_surf, (x_pos, y_offset))

        # Button
        self.next_music_file_button.draw(self.screen)


class ID3EditScreen:
    def __init__(self, screen, data_bundle):
        self.screen = screen
        self.mutagen_tags = data_bundle.get('mutagen_tags', {})
        self.mutagen_image_surface = data_bundle.get('mutagen_image_surface')
        self.filename = data_bundle.get('filename', 'unknown.mp3')

        # Extract current tag values
        self.artist = str(self.mutagen_tags.get('artist', ''))
        self.title = str(self.mutagen_tags.get('title', ''))
        self.album = str(self.mutagen_tags.get('album', ''))
        self.genre = str(self.mutagen_tags.get('genre', ''))
        self.year = str(self.mutagen_tags.get('year', ''))
        existing_comment = str(self.mutagen_tags.get('comment', ''))
        self.comment = existing_comment + ' noimage' if existing_comment else 'noimage'

        # Buttons
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.write_to_file_button = Button(screen.get_width() - 180, 10, 170, 32, "Write To File")

        # Confirmation buttons (shown after Write To File is pressed)
        self.are_you_sure_button = Button(screen.get_width() - 180, 50, 170, 32, "Are You Sure")
        self.cancel_button = Button(screen.get_width() - 180, 90, 170, 32, "Cancel")
        self.show_confirmation_buttons = False

        self.font_header = pygame.font.Font(None, 36)
        self.font_label = pygame.font.Font(None, 28)
        self.font_data = pygame.font.Font(None, 26)

        # Create checkboxes and InputBoxes for each field
        # Layout: checkbox at x=120, label at x=150, input at x=250
        y_start = 380
        x_checkbox = 120
        x_input = 250
        input_width = 700

        self.artist_checkbox = ColoredCheckbox(x_checkbox, y_start, 20, 20)
        self.artist_input = InputBox(x_input, y_start - 5, input_width, 30, self.artist)

        self.title_checkbox = ColoredCheckbox(x_checkbox, y_start + 30, 20, 20)
        self.title_input = InputBox(x_input, y_start + 30 - 5, input_width, 30, self.title)

        self.album_checkbox = ColoredCheckbox(x_checkbox, y_start + 60, 20, 20)
        self.album_input = InputBox(x_input, y_start + 60 - 5, input_width, 30, self.album)

        self.genre_checkbox = ColoredCheckbox(x_checkbox, y_start + 90, 20, 20)
        self.genre_input = InputBox(x_input, y_start + 90 - 5, input_width, 30, self.genre)

        self.year_checkbox = ColoredCheckbox(x_checkbox, y_start + 120, 20, 20)
        self.year_input = InputBox(x_input, y_start + 120 - 5, input_width, 30, self.year)

        self.comment_checkbox = ColoredCheckbox(x_checkbox, y_start + 150, 20, 20)
        self.comment_input = InputBox(x_input, y_start + 150 - 5, input_width, 30, self.comment)

        # Store in lists for easy iteration
        self.checkboxes = [
            self.artist_checkbox, self.title_checkbox, self.album_checkbox,
            self.genre_checkbox, self.year_checkbox, self.comment_checkbox
        ]
        self.input_boxes = [
            self.artist_input, self.title_input, self.album_input,
            self.genre_input, self.year_input, self.comment_input
        ]

        self.focusable_widgets = [self.back_button, self.write_to_file_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

        # Image thumbnail rect
        self.mutagen_thumb_rect = pygame.Rect((screen.get_width() - 300) // 2, 80, 300, 300)

    def handle_event(self, event):
        # Store checkbox states before handling event
        checkbox_states_before = [cb.checked for cb in self.checkboxes]

        # Handle checkbox clicks first
        for checkbox in self.checkboxes:
            checkbox.handle_event(event)

        # Check if any checkbox toggled, and sync data
        for i, (was_checked, checkbox, input_box) in enumerate(zip(checkbox_states_before, self.checkboxes, self.input_boxes)):
            if was_checked != checkbox.checked:
                # Checkbox was toggled
                if was_checked and not checkbox.checked:
                    # Toggled from checked to unchecked
                    # Update InputBox text with current data value
                    if i == 0:  # Artist
                        input_box.text = self.artist
                    elif i == 1:  # Title
                        input_box.text = self.title
                    elif i == 2:  # Album
                        input_box.text = self.album
                    elif i == 3:  # Genre
                        input_box.text = self.genre
                    elif i == 4:  # Year
                        input_box.text = self.year
                    elif i == 5:  # Comment
                        input_box.text = self.comment
                elif not was_checked and checkbox.checked:
                    # Toggled from unchecked to checked
                    # Update the data field with the edited text from InputBox
                    if i == 0:  # Artist
                        self.artist = input_box.text
                    elif i == 1:  # Title
                        self.title = input_box.text
                    elif i == 2:  # Album
                        self.album = input_box.text
                    elif i == 3:  # Genre
                        self.genre = input_box.text
                    elif i == 4:  # Year
                        self.year = input_box.text
                    elif i == 5:  # Comment
                        self.comment = input_box.text

        # Handle input box events (only for unchecked fields)
        for checkbox, input_box in zip(self.checkboxes, self.input_boxes):
            if not checkbox.checked:
                input_box.handle_event(event)

        # Handle button navigation and actions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
                return None

            focused_widget = self.focusable_widgets[self.focused_index]
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                if focused_widget == self.back_button or event.key == pygame.K_ESCAPE:
                    return "back_to_file_display"
                elif focused_widget == self.write_to_file_button:
                    # Show confirmation buttons
                    self.show_confirmation_buttons = True
                    return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_file_display"
            if self.write_to_file_button.rect.collidepoint(event.pos):
                # Show confirmation buttons
                self.show_confirmation_buttons = True
                return None

            # Handle confirmation buttons (if shown)
            if self.show_confirmation_buttons:
                if self.are_you_sure_button.rect.collidepoint(event.pos):
                    # Get final values from checkboxes/inputs
                    final_artist = self.artist if self.artist_checkbox.checked else self.artist_input.text
                    final_title = self.title if self.title_checkbox.checked else self.title_input.text
                    final_album = self.album if self.album_checkbox.checked else self.album_input.text
                    final_genre = self.genre if self.genre_checkbox.checked else self.genre_input.text
                    final_year = self.year if self.year_checkbox.checked else self.year_input.text
                    final_comment = self.comment if self.comment_checkbox.checked else self.comment_input.text

                    print("\n=== WRITING ID3 TAGS (EDIT MODE) ===")
                    print(f"Artist: {final_artist}")
                    print(f"Title: {final_title}")
                    print(f"Album: {final_album}")
                    print(f"Genre: {final_genre}")
                    print(f"Year: {final_year}")
                    print(f"Comment: {final_comment}")
                    print("====================================\n")

                    # Preserve existing image - extract from current file
                    image_path = None
                    if self.mutagen_image_surface:
                        # Save the current image to a temporary file
                        try:
                            pygame.image.save(self.mutagen_image_surface, 'temp_id3_image.png')
                            image_path = 'temp_id3_image.png'
                        except Exception as e:
                            print(f"Warning: Could not save existing image: {e}")

                    # Write ID3 tags (preserving existing image)
                    write_success = id3_tag_writer_module.write_id3_tags(
                        self.filename,
                        final_title,
                        final_artist,
                        final_year,
                        final_genre,
                        final_comment,
                        image_path
                    )

                    if write_success:
                        # Read back the tags to verify
                        updated_tags = id3_tag_writer_module.read_id3_tags(self.filename)
                        return "show_updated_tags", {'filename': self.filename, 'updated_tags': updated_tags}
                    else:
                        print("ERROR: Failed to write ID3 tags.")
                        return None
                elif self.cancel_button.rect.collidepoint(event.pos):
                    # Hide confirmation buttons
                    self.show_confirmation_buttons = False
                    return None

        return None

    def draw(self):
        # Draw header
        header = self.font_header.render("Edit ID3 Tags", True, (255, 255, 255))
        header_x = (self.screen.get_width() - header.get_width()) // 2
        self.screen.blit(header, (header_x, 20))

        # Draw image if available
        if self.mutagen_image_surface:
            try:
                scaled_image = pygame.transform.scale(self.mutagen_image_surface, (self.mutagen_thumb_rect.width, self.mutagen_thumb_rect.height))
                self.screen.blit(scaled_image, (self.mutagen_thumb_rect.x, self.mutagen_thumb_rect.y))
            except pygame.error:
                pygame.draw.rect(self.screen, (50, 50, 50), self.mutagen_thumb_rect)
                text_surf = self.font_data.render("Bad Art", True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=self.mutagen_thumb_rect.center)
                self.screen.blit(text_surf, text_rect)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), self.mutagen_thumb_rect)
            text_surf = self.font_data.render("No Art", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.mutagen_thumb_rect.center)
            self.screen.blit(text_surf, text_rect)

        # Draw metadata with checkboxes and conditional InputBoxes
        y_offset = 380
        x_checkbox = 120
        x_label = 150
        x_data = 250

        # Field labels and default data
        field_data = [
            ("Artist:", self.artist, self.artist_checkbox, self.artist_input),
            ("Title:", self.title, self.title_checkbox, self.title_input),
            ("Album:", self.album, self.album_checkbox, self.album_input),
            ("Genre:", self.genre, self.genre_checkbox, self.genre_input),
            ("Year:", self.year, self.year_checkbox, self.year_input),
            ("Comment:", self.comment, self.comment_checkbox, self.comment_input),
        ]

        for label_text, default_data, checkbox, input_box in field_data:
            # Draw checkbox
            checkbox.draw(self.screen)

            # Draw label
            label_surf = self.font_label.render(label_text, True, (200, 200, 200))
            self.screen.blit(label_surf, (x_label, y_offset))

            # Draw either static data (checked) or InputBox (unchecked)
            if checkbox.checked:
                # Show default data
                display_text = str(default_data)
                if len(display_text) > 60:
                    display_text = display_text[:57] + '...'
                data_surf = self.font_data.render(display_text, True, (255, 255, 255))
                self.screen.blit(data_surf, (x_data, y_offset))
            else:
                # Show InputBox for editing
                input_box.draw(self.screen)

            y_offset += 30

        # Draw buttons
        self.back_button.draw(self.screen)
        self.write_to_file_button.draw(self.screen)

        # Draw confirmation buttons if shown
        if self.show_confirmation_buttons:
            # Draw Are You Sure button (green)
            pygame.draw.rect(self.screen, (0, 200, 0), self.are_you_sure_button.rect)
            text_surf = FONT.render(self.are_you_sure_button.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.are_you_sure_button.rect.center)
            self.screen.blit(text_surf, text_rect)

            # Draw Cancel button (red)
            pygame.draw.rect(self.screen, (200, 0, 0), self.cancel_button.rect)
            text_surf = FONT.render(self.cancel_button.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.cancel_button.rect.center)
            self.screen.blit(text_surf, text_rect)


class ConfirmationScreen:
    def __init__(self, screen, confirmation_data, show_image=True):
        self.screen = screen
        self.label_image = confirmation_data.get('label_image') if show_image else None
        self.data_bundle = confirmation_data['data_bundle']
        self.show_image = show_image
        self.filename = self.data_bundle.get('filename', 'unknown.mp3')

        # Process and sanitize data
        self.title = self._get_title()
        self.artist = self._get_artist()
        self.year = self._get_year()
        self.time = self.data_bundle['mutagen_tags'].get('time', 'N/A')
        self.genres = self._get_genres()
        self.comment = self._get_comment()

        # Buttons
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.write_to_file_button = Button(screen.get_width() - 180, 10, 170, 32, "Write To File")

        # Confirmation buttons (shown after Write To File is pressed)
        self.are_you_sure_button = Button(screen.get_width() - 180, 50, 170, 32, "Are You Sure")
        self.cancel_button = Button(screen.get_width() - 180, 90, 170, 32, "Cancel")
        self.show_confirmation_buttons = False

        self.font_label = pygame.font.Font(None, 28)
        self.font_data = pygame.font.Font(None, 26)

        # Create checkboxes and InputBoxes for each field
        # Layout: checkbox at x=120, label at x=150, input at x=250
        y_start = 480
        x_checkbox = 120
        x_input = 250
        input_width = 700

        self.title_checkbox = ColoredCheckbox(x_checkbox, y_start, 20, 20)
        self.title_input = InputBox(x_input, y_start - 5, input_width, 30, self.title)

        self.artist_checkbox = ColoredCheckbox(x_checkbox, y_start + 30, 20, 20)
        self.artist_input = InputBox(x_input, y_start + 30 - 5, input_width, 30, self.artist)

        self.year_checkbox = ColoredCheckbox(x_checkbox, y_start + 60, 20, 20)
        self.year_input = InputBox(x_input, y_start + 60 - 5, input_width, 30, self.year)

        self.time_checkbox = ColoredCheckbox(x_checkbox, y_start + 90, 20, 20)
        self.time_input = InputBox(x_input, y_start + 90 - 5, input_width, 30, self.time)

        self.genre_checkbox = ColoredCheckbox(x_checkbox, y_start + 120, 20, 20)
        self.genre_input = InputBox(x_input, y_start + 120 - 5, input_width, 30, self.genres)

        self.comment_checkbox = ColoredCheckbox(x_checkbox, y_start + 150, 20, 20)
        self.comment_input = InputBox(x_input, y_start + 150 - 5, input_width, 30, self.comment)

        # Store in lists for easy iteration
        self.checkboxes = [
            self.title_checkbox, self.artist_checkbox, self.year_checkbox,
            self.time_checkbox, self.genre_checkbox, self.comment_checkbox
        ]
        self.input_boxes = [
            self.title_input, self.artist_input, self.year_input,
            self.time_input, self.genre_input, self.comment_input
        ]

        self.focusable_widgets = [self.back_button, self.write_to_file_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

    def _sanitize_text(self, text):
        """Keep only A-Z, a-z, 0-9, and spaces"""
        if not text or text == 'N/A':
            return text
        # Keep only ASCII letters, numbers, and spaces
        sanitized = re.sub(r'[^A-Za-z0-9 ]', '', str(text))
        # Remove extra spaces
        sanitized = ' '.join(sanitized.split())
        return sanitized

    def _get_title(self):
        """Always use Discogs title, sanitized"""
        title = self.data_bundle['discogs_title']
        return self._sanitize_text(title)

    def _get_artist(self):
        """Always use Discogs artist, sanitized, with 'The ' removed from start (case-insensitive)"""
        artist = self.data_bundle['discogs_artist']
        sanitized = self._sanitize_text(artist)
        # Remove "The " from the start of artist name if present (case-insensitive)
        if sanitized and sanitized.lower().startswith('the '):
            sanitized = sanitized[4:]  # Remove "The " or "the " (4 characters)
        return sanitized

    def _get_year(self):
        """Use ID3 year if it contains 4 digits, otherwise use Discogs year"""
        import re

        # Try to find a 4-digit year in the ID3 tag
        id3_year = self.data_bundle['mutagen_tags'].get('year', 'N/A')
        if id3_year and id3_year != 'N/A':
            # Search for 4 consecutive digits
            match = re.search(r'\d{4}', str(id3_year))
            if match:
                return match.group(0)

        # Fall back to Discogs year
        discogs_year = self.data_bundle.get('discogs_year', 'N/A')
        if discogs_year and discogs_year != 'N/A':
            # Search for 4 consecutive digits in Discogs year
            match = re.search(r'\d{4}', str(discogs_year))
            if match:
                return match.group(0)
            return str(discogs_year)

        return 'N/A'

    def _get_genres(self):
        """Use Discogs genres, sanitized to A-Z, a-z, 0-9, and spaces"""
        genres = self.data_bundle['discogs_genres']
        if genres:
            genre_text = ", ".join(genres)
            # Sanitize to remove special characters
            return self._sanitize_text(genre_text)
        return "N/A"

    def _get_comment(self):
        """Use ID3 comment + ' image' or ' noimage' suffix, preventing doubling"""
        comment = self.data_bundle['mutagen_tags'].get('comment', '')

        # Strip existing "image" or "noimage" suffixes to prevent doubling
        if comment and comment != 'N/A':
            comment = comment.strip()
            # Remove trailing "image" or "noimage"
            if comment.endswith(' image'):
                comment = comment[:-6].strip()  # Remove " image"
            elif comment.endswith('image'):
                comment = comment[:-5].strip()  # Remove "image"
            elif comment.endswith(' noimage'):
                comment = comment[:-8].strip()  # Remove " noimage"
            elif comment.endswith('noimage'):
                comment = comment[:-7].strip()  # Remove "noimage"

        if self.show_image:
            if comment and comment != 'N/A' and comment.strip():
                return comment + " image"
            else:
                return "image"
        else:
            # No image mode
            if comment and comment != 'N/A' and comment.strip():
                return comment + " noimage"
            else:
                return "noimage"

    def handle_event(self, event):
        # Store checkbox states before handling event
        checkbox_states_before = [cb.checked for cb in self.checkboxes]

        # Handle checkbox clicks first
        for checkbox in self.checkboxes:
            checkbox.handle_event(event)

        # Check if any checkbox toggled, and sync data
        for i, (was_checked, checkbox, input_box) in enumerate(zip(checkbox_states_before, self.checkboxes, self.input_boxes)):
            if was_checked != checkbox.checked:
                # Checkbox was toggled
                if was_checked and not checkbox.checked:
                    # Toggled from checked to unchecked
                    # Update InputBox text with current data value
                    if i == 0:  # Title
                        input_box.text = self.title
                    elif i == 1:  # Artist
                        input_box.text = self.artist
                    elif i == 2:  # Year
                        input_box.text = self.year
                    elif i == 3:  # Time
                        input_box.text = self.time
                    elif i == 4:  # Genre
                        input_box.text = self.genres
                    elif i == 5:  # Comment
                        input_box.text = self.comment
                elif not was_checked and checkbox.checked:
                    # Toggled from unchecked to checked
                    # Update the data field with the edited text from InputBox
                    if i == 0:  # Title
                        self.title = input_box.text
                    elif i == 1:  # Artist
                        self.artist = input_box.text
                    elif i == 2:  # Year
                        self.year = input_box.text
                    elif i == 3:  # Time
                        self.time = input_box.text
                    elif i == 4:  # Genre
                        self.genres = input_box.text
                    elif i == 5:  # Comment
                        self.comment = input_box.text

        # Handle input box events (only for unchecked fields)
        for checkbox, input_box in zip(self.checkboxes, self.input_boxes):
            if not checkbox.checked:
                input_box.handle_event(event)

        # Handle button navigation and actions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
                return None

            focused_widget = self.focusable_widgets[self.focused_index]
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                if focused_widget == self.back_button or event.key == pygame.K_ESCAPE:
                    return "back_to_file_display" if not self.show_image else "back_to_result"
                elif focused_widget == self.write_to_file_button:
                    # Show confirmation buttons
                    self.show_confirmation_buttons = True
                    return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_file_display" if not self.show_image else "back_to_result"
            if self.write_to_file_button.rect.collidepoint(event.pos):
                # Show confirmation buttons
                self.show_confirmation_buttons = True
                return None

            # Handle confirmation buttons (if shown)
            if self.show_confirmation_buttons:
                if self.are_you_sure_button.rect.collidepoint(event.pos):
                    # Get final values from checkboxes/inputs
                    final_title = self.title if self.title_checkbox.checked else self.title_input.text
                    final_artist = self.artist if self.artist_checkbox.checked else self.artist_input.text
                    final_year = self.year if self.year_checkbox.checked else self.year_input.text
                    final_time = self.time if self.time_checkbox.checked else self.time_input.text
                    final_genre = self.genres if self.genre_checkbox.checked else self.genre_input.text
                    final_comment = self.comment if self.comment_checkbox.checked else self.comment_input.text

                    print("\n=== WRITING ID3 TAGS ===")
                    print(f"Title: {final_title}")
                    print(f"Artist: {final_artist}")
                    print(f"Year: {final_year}")
                    print(f"Genre: {final_genre}")
                    print(f"Comment: {final_comment}")
                    print("========================\n")

                    # Create image if in image mode
                    image_path = None
                    if self.show_image:
                        print("Creating final record label...")
                        success = label_pressing_module.combine_pngs(
                            'new_cutout_label.png',
                            'adaptor.png',
                            'final_record.png',
                            (420, 420)
                        )
                        if success:
                            print("Final record label created successfully.")
                            image_path = 'final_record.png'
                        else:
                            print("WARNING: Failed to create final record label. Proceeding without image.")

                    # Write ID3 tags (with or without image)
                    write_success = id3_tag_writer_module.write_id3_tags(
                        self.filename,
                        final_title,
                        final_artist,
                        final_year,
                        final_genre,
                        final_comment,
                        image_path
                    )

                    if write_success:
                        # Read back the tags to verify
                        updated_tags = id3_tag_writer_module.read_id3_tags(self.filename)
                        return "show_updated_tags", {'filename': self.filename, 'updated_tags': updated_tags}
                    else:
                        print("ERROR: Failed to write ID3 tags.")
                        return None
                elif self.cancel_button.rect.collidepoint(event.pos):
                    # Hide confirmation buttons
                    self.show_confirmation_buttons = False
                    return None

        return None

    def draw(self):
        # Draw label image centered at top (only if show_image is True)
        if self.show_image and self.label_image:
            scaled_image = pygame.transform.scale(self.label_image, (400, 400))
            image_x = (self.screen.get_width() - 400) // 2
            self.screen.blit(scaled_image, (image_x, 60))

        # Draw metadata with checkboxes and conditional InputBoxes
        y_offset = 480
        x_checkbox = 120
        x_label = 150
        x_data = 250

        # Field labels and default data
        field_data = [
            ("Title:", self.title, self.title_checkbox, self.title_input),
            ("Artist:", self.artist, self.artist_checkbox, self.artist_input),
            ("Year:", self.year, self.year_checkbox, self.year_input),
            ("Time:", self.time, self.time_checkbox, self.time_input),
            ("Genre:", self.genres, self.genre_checkbox, self.genre_input),
            ("Comment:", self.comment, self.comment_checkbox, self.comment_input),
        ]

        for label_text, default_data, checkbox, input_box in field_data:
            # Draw checkbox
            checkbox.draw(self.screen)

            # Draw label
            label_surf = self.font_label.render(label_text, True, (200, 200, 200))
            self.screen.blit(label_surf, (x_label, y_offset))

            # Draw either static data (checked) or InputBox (unchecked)
            if checkbox.checked:
                # Show default data
                display_text = str(default_data)
                if len(display_text) > 60:
                    display_text = display_text[:57] + '...'
                data_surf = self.font_data.render(display_text, True, (255, 255, 255))
                self.screen.blit(data_surf, (x_data, y_offset))
            else:
                # Show InputBox for editing
                input_box.draw(self.screen)

            y_offset += 30

        # Draw buttons
        self.back_button.draw(self.screen)
        self.write_to_file_button.draw(self.screen)

        # Draw confirmation buttons if shown
        if self.show_confirmation_buttons:
            # Draw Are You Sure button (green)
            pygame.draw.rect(self.screen, (0, 200, 0), self.are_you_sure_button.rect)
            text_surf = FONT.render(self.are_you_sure_button.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.are_you_sure_button.rect.center)
            self.screen.blit(text_surf, text_rect)

            # Draw Cancel button (red)
            pygame.draw.rect(self.screen, (200, 0, 0), self.cancel_button.rect)
            text_surf = FONT.render(self.cancel_button.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.cancel_button.rect.center)
            self.screen.blit(text_surf, text_rect)


class SearchOptionsScreen:
    def __init__(self, screen, music_files):
        self.screen = screen
        self.music_files = music_files
        self.font_header = pygame.font.Font(None, 40)
        self.font_label = pygame.font.Font(None, 28)

        # Five mutually exclusive checkboxes
        checkbox_x = 100
        y_start = 130
        self.option1_checkbox = Checkbox(checkbox_x, y_start, 20, 20)
        self.option2_checkbox = Checkbox(checkbox_x, y_start + 70, 20, 20)
        self.option3_checkbox = Checkbox(checkbox_x, y_start + 140, 20, 20)
        self.option4_checkbox = Checkbox(checkbox_x, y_start + 210, 20, 20)
        self.option5_checkbox = Checkbox(checkbox_x, y_start + 280, 20, 20)

        # Default: option 1 is checked
        self.option1_checkbox.checked = True

        # Input boxes for options 2, 3, and 5
        input_x = 300
        input_width = 600
        self.artist_input = InputBox(input_x, y_start + 100, input_width, 30, "Enter Artist Name")
        self.title_input = InputBox(input_x, y_start + 170, input_width, 30, "Enter Title")
        self.genre_input = InputBox(input_x, y_start + 310, input_width, 30, "Enter Genre")

        # Start button
        self.start_button = Button(screen.get_width() / 2 - 60, 520, 120, 40, "START")

        self.checkboxes = [self.option1_checkbox, self.option2_checkbox, self.option3_checkbox, self.option4_checkbox, self.option5_checkbox]
        self.focusable_widgets = [self.start_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

    def handle_event(self, event):
        # Handle checkbox clicks (make them mutually exclusive)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, checkbox in enumerate(self.checkboxes):
                if checkbox.rect.collidepoint(event.pos):
                    # Uncheck all others
                    for j, cb in enumerate(self.checkboxes):
                        cb.checked = (i == j)

            # Handle Start button
            if self.start_button.rect.collidepoint(event.pos):
                return self._create_search_config()

        # Handle keyboard input for Start button
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self._create_search_config()

        # Handle input boxes (only when their checkbox is selected)
        if self.option2_checkbox.checked:
            self.artist_input.handle_event(event)
        if self.option3_checkbox.checked:
            self.title_input.handle_event(event)
        if self.option5_checkbox.checked:
            self.genre_input.handle_event(event)

        return None

    def _create_search_config(self):
        """Create search configuration based on selected option"""
        if self.option1_checkbox.checked:
            # Option 1: From top
            return {
                'mode': 'from_top',
                'start_index': 0,
                'add_the_prefix': False
            }
        elif self.option2_checkbox.checked:
            # Option 2: From artist
            artist_name = self.artist_input.text
            print(f"DEBUG: Artist input text = '{artist_name}'")
            if artist_name == "Enter Artist Name" or not artist_name.strip():
                print("Please enter an artist name")
                return None

            print(f"DEBUG: Calling find_first_file_for_artist with '{artist_name.strip()}'")
            start_index, add_the_prefix = find_first_file_for_artist(self.music_files, artist_name.strip())
            print(f"DEBUG: Returned start_index={start_index}, add_the_prefix={add_the_prefix}")
            return {
                'mode': 'from_artist',
                'artist_name': artist_name.strip(),
                'start_index': start_index,
                'add_the_prefix': add_the_prefix
            }
        elif self.option3_checkbox.checked:
            # Option 3: By title
            title_search = self.title_input.text
            if title_search == "Enter Title" or not title_search.strip():
                print("Please enter a title")
                return None

            start_index = find_file_by_title(self.music_files, title_search.strip())
            return {
                'mode': 'by_title',
                'title_search': title_search.strip(),
                'start_index': start_index,
                'add_the_prefix': False
            }
        elif self.option4_checkbox.checked:
            # Option 4: From discogs text list
            try:
                with open('discogs_search_list.txt', 'r', encoding='latin-1') as f:
                    content = f.read()
                    song_list = [s.strip() for s in content.split(',') if s.strip()]
                print(f"Loaded {len(song_list)} songs from discogs_search_list.txt")
                return {
                    'mode': 'from_discogs_list',
                    'song_list': song_list,
                    'list_index': 0,
                    'start_index': 0,
                    'add_the_prefix': False
                }
            except FileNotFoundError:
                print("Error: discogs_search_list.txt not found")
                return None
            except Exception as e:
                print(f"Error loading discogs_search_list.txt: {e}")
                return None
        elif self.option5_checkbox.checked:
            # Option 5: By genre - transition to genre selection screen
            return {
                'mode': 'show_genre_selection'
            }

        return None

    def draw(self):
        # Header
        header = self.font_header.render("How Would You Like To Search Discogs", True, (255, 255, 255))
        header_rect = header.get_rect(center=(self.screen.get_width() / 2, 80))
        self.screen.blit(header, header_rect)

        # Option 1
        self.option1_checkbox.draw(self.screen)
        label1 = self.font_label.render("From The Top Of My Music Directory", True, (255, 255, 255))
        self.screen.blit(label1, (130, 125))

        # Option 2
        self.option2_checkbox.draw(self.screen)
        label2 = self.font_label.render("From The Top File For This Artist", True, (255, 255, 255))
        self.screen.blit(label2, (130, 195))

        # Artist input (only visible when option 2 is checked)
        if self.option2_checkbox.checked:
            artist_label = self.font_label.render("Artist:", True, (200, 200, 200))
            self.screen.blit(artist_label, (150, 230))
            self.artist_input.draw(self.screen)

        # Option 3
        self.option3_checkbox.draw(self.screen)
        label3 = self.font_label.render("For This Title", True, (255, 255, 255))
        self.screen.blit(label3, (130, 265))

        # Title input (only visible when option 3 is checked)
        if self.option3_checkbox.checked:
            title_label = self.font_label.render("Title:", True, (200, 200, 200))
            self.screen.blit(title_label, (150, 300))
            self.title_input.draw(self.screen)

        # Option 4
        self.option4_checkbox.draw(self.screen)
        label4 = self.font_label.render("Search From Discogs Text List", True, (255, 255, 255))
        self.screen.blit(label4, (130, 335))

        # Option 5
        self.option5_checkbox.draw(self.screen)
        label5 = self.font_label.render("Search By Genre (From Comment Tag)", True, (255, 255, 255))
        self.screen.blit(label5, (130, 405))

        # Genre input (only visible when option 5 is checked)
        if self.option5_checkbox.checked:
            genre_label = self.font_label.render("Genre:", True, (200, 200, 200))
            self.screen.blit(genre_label, (150, 440))
            self.genre_input.draw(self.screen)

        # Start button
        self.start_button.draw(self.screen)


class GenreSelectionScreen:
    """
    Screen that displays all unique genres found in Comment tags.
    User selects a genre by clicking a checkbox, which immediately triggers search.
    """
    def __init__(self, screen, music_files):
        self.screen = screen
        self.music_files = music_files
        self.font_header = pygame.font.Font(None, 40)
        self.font_label = pygame.font.Font(None, 24)

        # Scan all music files to collect unique genres (with progress bar)
        print("Scanning all music files for genres...")
        self.genres = scan_all_genres(music_files, screen)
        print(f"Found {len(self.genres)} unique genres")

        # Create checkboxes for each genre in 4 columns
        self.genre_checkboxes = []
        num_columns = 4
        column_width = 240  # Width of each column
        x_start = 50  # Start from left edge
        y_start = 120
        y_spacing = 30

        # Calculate rows per column
        total_genres = len(self.genres)
        rows_per_column = (total_genres + num_columns - 1) // num_columns  # Ceiling division

        for i, genre in enumerate(self.genres):
            # Calculate which column and row this genre should be in
            column = i // rows_per_column
            row = i % rows_per_column

            # Calculate x and y positions
            x_pos = x_start + (column * column_width)
            y_pos = y_start + (row * y_spacing)

            checkbox = Checkbox(x_pos, y_pos, 20, 20, genre)
            self.genre_checkboxes.append(checkbox)

        # Track selected genre
        self.selected_genre = None

    def handle_event(self, event):
        """Handle checkbox clicks - return selected genre immediately"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, checkbox in enumerate(self.genre_checkboxes):
                if checkbox.rect.collidepoint(event.pos):
                    # User clicked this genre - return it immediately
                    self.selected_genre = self.genres[i]
                    print(f"User selected genre: {self.selected_genre}")

                    # Find all files with this genre
                    genre_files = find_files_by_genre(self.music_files, self.selected_genre)

                    if not genre_files:
                        print(f"No files found with genre '{self.selected_genre}'")
                        return None

                    # v0.00.22: Check if genre_search.txt already exists
                    if os.path.exists('genre_search.txt'):
                        print("WARNING: genre_search.txt already exists")
                        overwrite = prompt_overwrite_genre_list(self.screen)
                        if not overwrite:
                            print("User cancelled genre selection")
                            return None  # User cancelled, stay on genre selection screen

                    # v0.00.22: Save genre list to file for persistence
                    save_genre_list('genre_search.txt', genre_files)
                    print(f"Saved {len(genre_files)} files to genre_search.txt")

                    # Return search config for this genre
                    return {
                        'mode': 'by_genre',
                        'genre_search': self.selected_genre,
                        'genre_files': genre_files,
                        'list_index': 0,
                        'start_index': 0,
                        'add_the_prefix': False
                    }

        return None

    def draw(self):
        # Header
        header = self.font_header.render("Select a Genre to Process", True, (255, 255, 255))
        header_rect = header.get_rect(center=(self.screen.get_width() / 2, 60))
        self.screen.blit(header, header_rect)

        # Instructions
        instructions = self.font_label.render("Click a genre to begin processing files", True, (200, 200, 200))
        inst_rect = instructions.get_rect(center=(self.screen.get_width() / 2, 90))
        self.screen.blit(instructions, inst_rect)

        # Draw all genre checkboxes and labels
        for i, checkbox in enumerate(self.genre_checkboxes):
            checkbox.draw(self.screen)
            genre_text = self.font_label.render(self.genres[i], True, (255, 255, 255))
            # Position label to the right of checkbox (checkbox.x + 30)
            self.screen.blit(genre_text, (checkbox.rect.x + 30, checkbox.rect.y - 3))


# === Helper Functions for Search Options ===

def is_artist_in_bands_file(artist_name, bands_file='the_bands.txt'):
    """
    Check if artist (without 'The ') exists in the_bands.txt.
    Returns: True if found, False otherwise
    """
    if not artist_name or artist_name == 'N/A':
        return False

    artist_lower = artist_name.lower().strip()

    try:
        if os.path.exists(bands_file):
            with open(bands_file, 'r', encoding='utf-8') as f:
                content = f.read()
                bands_list = [band.strip().lower() for band in content.split(',')]
                return artist_lower in bands_list
    except Exception as e:
        print(f"Error reading {bands_file}: {e}")

    return False


def find_first_file_for_artist(music_files, artist_name, bands_file='the_bands.txt'):
    """
    Find the index of the first file matching the artist name.

    Logic:
    1. Check if artist_name (lowercase) is in the_bands.txt
    2. If found, search files for both "[artist_name] - " and "The [artist_name] - "
    3. If not in the_bands.txt, only search for "[artist_name] - "
    4. Return (index, add_the_prefix_flag)
    """
    if not artist_name:
        return 0, False

    artist_lower = artist_name.lower().strip()
    in_bands_file = is_artist_in_bands_file(artist_lower, bands_file)

    # Search patterns
    patterns = [artist_name + " - "]
    if in_bands_file:
        patterns.append("The " + artist_name + " - ")

    for i, music_file in enumerate(music_files):
        for pattern in patterns:
            if music_file.lower().startswith(pattern.lower()):
                print(f"Found first file for '{artist_name}' at index {i}: {music_file}")
                return i, in_bands_file

    print(f"No files found for artist '{artist_name}', starting from top")
    return 0, in_bands_file


def find_file_by_title(music_files, title_search):
    """
    Find the index of the first file containing the title.

    Logic:
    1. Search through all filenames
    2. Extract title portion (after " - ")
    3. Case-insensitive partial match
    4. Return index of first match, or 0 if not found
    """
    if not title_search:
        return 0

    title_lower = title_search.lower().strip()

    for i, music_file in enumerate(music_files):
        # Try to extract title from "Artist - Title.mp3" format
        if ' - ' in music_file:
            title_portion = music_file.split(' - ', 1)[1].replace('.mp3', '')
            if title_lower in title_portion.lower():
                print(f"Found file with title '{title_search}' at index {i}: {music_file}")
                return i

    print(f"No files found with title '{title_search}', starting from top")
    return 0


def draw_progress_bar(screen, current, total, message="Processing..."):
    """
    Draw a progress bar on the screen during long operations.

    Args:
        screen: pygame screen surface
        current: current item number (0-based or 1-based)
        total: total number of items
        message: message to display above progress bar
    """
    # Clear screen
    screen.fill((30, 30, 30))

    # Font
    font_large = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 28)

    # Calculate progress percentage
    if total > 0:
        progress = current / total
    else:
        progress = 0

    # Draw message
    msg_surf = font_large.render(message, True, (255, 255, 255))
    msg_rect = msg_surf.get_rect(center=(screen.get_width() / 2, 200))
    screen.blit(msg_surf, msg_rect)

    # Draw progress text
    progress_text = f"{current} of {total} files scanned ({int(progress * 100)}%)"
    progress_surf = font_small.render(progress_text, True, (200, 200, 200))
    progress_rect = progress_surf.get_rect(center=(screen.get_width() / 2, 250))
    screen.blit(progress_surf, progress_rect)

    # Draw progress bar background
    bar_width = 600
    bar_height = 40
    bar_x = (screen.get_width() - bar_width) / 2
    bar_y = 300

    # Background (gray)
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))

    # Progress fill (blue)
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        pygame.draw.rect(screen, (50, 150, 255), (bar_x, bar_y, fill_width, bar_height))

    # Border (white)
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    # Update display
    pygame.display.flip()


def scan_all_genres(music_files, screen=None):
    """
    Scan all music files and extract unique genres from Comment tags.

    Logic:
    1. Loop through all music files
    2. Read Comment tag from each file
    3. Extract genre names (assumes Comment format like "Rock", "Jazz Soul", etc.)
    4. Collect all unique genres
    5. Return sorted list of unique genres
    6. Display progress bar if screen is provided

    Args:
        music_files: List of music filenames
        screen: Optional pygame screen surface for progress bar

    Returns:
        Sorted list of unique genre names found in Comment tags
    """
    unique_genres = set()
    total_files = len(music_files)

    print(f"Scanning {total_files} files to collect unique genres...")

    for i, music_file in enumerate(music_files):
        # Update progress bar for EVERY file for better visual feedback
        if screen:
            draw_progress_bar(screen, i, total_files, "Scanning music files for genres...")
            # Process pygame events to prevent "not responding" on Windows
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return []

        try:
            # Construct full path to music file
            file_path = os.path.join('Music', music_file)

            # Read ID3 tags using mutagen (raw mode, not easy mode)
            audio = mutagen.File(file_path)
            if audio is None:
                continue

            # Get Comment tag (COMM) - try COMM::eng first, then COMM
            comment = ''
            if 'COMM::eng' in audio:
                comment_tag = audio.get('COMM::eng')
                if comment_tag and hasattr(comment_tag, 'text'):
                    comment = str(comment_tag.text[0]) if comment_tag.text else ''
            elif 'COMM' in audio:
                comment_tag = audio.get('COMM')
                if comment_tag and hasattr(comment_tag, 'text'):
                    comment = str(comment_tag.text[0]) if comment_tag.text else ''

            # Extract genre from comment (strip "image" and "noimage" suffixes)
            if comment:
                # Remove " image" or " noimage" suffix
                genre_text = comment.strip()
                if genre_text.endswith(' image'):
                    genre_text = genre_text[:-6].strip()
                elif genre_text.endswith('image'):
                    genre_text = genre_text[:-5].strip()
                elif genre_text.endswith(' noimage'):
                    genre_text = genre_text[:-8].strip()
                elif genre_text.endswith('noimage'):
                    genre_text = genre_text[:-7].strip()

                # Split genre text by spaces to get individual genres
                # Example: "Rock Soul Blues" becomes ["Rock", "Soul", "Blues"]
                if genre_text and genre_text != 'N/A':
                    genre_words = genre_text.split()
                    for genre_word in genre_words:
                        genre_word = genre_word.strip()
                        if genre_word:  # Only add non-empty words
                            unique_genres.add(genre_word)

        except Exception as e:
            # Skip files that can't be read
            continue

    # Show 100% complete
    if screen:
        draw_progress_bar(screen, total_files, total_files, "Scanning complete!")
        pygame.time.wait(500)  # Brief pause to show completion

    # Convert to sorted list
    sorted_genres = sorted(list(unique_genres))
    print(f"Found {len(sorted_genres)} unique genres: {sorted_genres}")

    return sorted_genres


def find_files_by_genre(music_files, genre_search):
    """
    Find all files that contain the genre keyword in their ID3 Comment tag.

    Logic:
    1. Search through all music files in the Music directory
    2. Read each file's ID3 Comment tag using mutagen
    3. Case-insensitive partial match for genre keyword
    4. Return list of all matching filenames

    Args:
        music_files: List of music filenames
        genre_search: Genre keyword to search for

    Returns:
        List of filenames that match the genre (empty list if none found)
    """
    if not genre_search:
        return []

    genre_lower = genre_search.lower().strip()
    matching_files = []

    print(f"Searching {len(music_files)} files for genre '{genre_search}' in Comment tag...")

    for music_file in music_files:
        try:
            # Construct full path to music file
            file_path = os.path.join('Music', music_file)

            # Read ID3 tags using mutagen (raw mode, not easy mode)
            audio = mutagen.File(file_path)
            if audio is None:
                continue

            # Get Comment tag (COMM) - try COMM::eng first, then COMM
            comment = ''
            if 'COMM::eng' in audio:
                comment_tag = audio.get('COMM::eng')
                if comment_tag and hasattr(comment_tag, 'text'):
                    comment = str(comment_tag.text[0]) if comment_tag.text else ''
            elif 'COMM' in audio:
                comment_tag = audio.get('COMM')
                if comment_tag and hasattr(comment_tag, 'text'):
                    comment = str(comment_tag.text[0]) if comment_tag.text else ''

            # Check if genre keyword is in comment (case-insensitive)
            if comment and genre_lower in comment.lower():
                matching_files.append(music_file)
                print(f"  ✓ Found: {music_file} (Comment: {comment})")

        except Exception as e:
            # Skip files that can't be read
            continue

    print(f"Found {len(matching_files)} files matching genre '{genre_search}'")
    return matching_files


def find_music_file_index(music_files, filename):
    """
    Find the exact index of a filename in the music_files list.

    Args:
        music_files: List of music filenames
        filename: Exact filename to search for (e.g., "Eagles - Hotel California.mp3")

    Returns:
        Index of the file if found, -1 if not found
    """
    if not filename:
        return -1

    filename_stripped = filename.strip()

    for i, music_file in enumerate(music_files):
        if music_file == filename_stripped:
            print(f"Found '{filename}' at index {i}")
            return i

    print(f"File '{filename}' not found in Music directory")
    return -1


def save_genre_list(filename, file_list):
    """
    Save a list of filenames to genre_search.txt for persistence.

    Args:
        filename: Path to genre_search.txt
        file_list: List of music filenames to save

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(file_list))
        return True
    except Exception as e:
        print(f"Error saving genre list: {e}")
        return False


def load_genre_list(filename):
    """
    Load a list of filenames from genre_search.txt.

    Args:
        filename: Path to genre_search.txt

    Returns:
        List of filenames, or None if file doesn't exist or is corrupted
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.literal_eval(content)  # Safely parse string to list
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error loading genre list (corrupted file): {e}")
        # Edge case: Corrupted file - delete and return None
        try:
            os.remove(filename)
            print(f"Deleted corrupted {filename}")
        except:
            pass
        return None


def remove_from_genre_list(filename, genre_file):
    """
    Remove a single file from genre_search.txt after processing/skipping.
    Deletes the file if the list becomes empty.

    Args:
        filename: Path to genre_search.txt
        genre_file: Music filename to remove from the list

    Returns:
        True if successful, False otherwise
    """
    try:
        genre_list = load_genre_list(filename)
        if genre_list is None:
            return False

        if genre_file in genre_list:
            genre_list.remove(genre_file)
            print(f"Removed '{genre_file}' from {filename}")

        if len(genre_list) == 0:
            # List empty, delete file
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Deleted {filename} - all files processed")
            return True
        else:
            # Save updated list
            save_genre_list(filename, genre_list)
            return True
    except Exception as e:
        print(f"Error removing from genre list: {e}")
        return False


def prompt_resume_genre_search(screen):
    """
    Display a dialog asking if user wants to resume the existing genre search.

    Args:
        screen: Pygame screen surface

    Returns:
        True to resume, False to start fresh
    """
    font_header = pygame.font.Font(None, 50)
    font_button = pygame.font.Font(None, 40)

    # Create buttons
    resume_button = Button(300, 300, 150, 60, "Resume")
    fresh_button = Button(574, 300, 200, 60, "Start Fresh")

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Default to start fresh
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False  # ESC = start fresh
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.rect.collidepoint(event.pos):
                    return True
                if fresh_button.rect.collidepoint(event.pos):
                    return False

        screen.fill((0, 0, 0))

        # Header
        header = font_header.render("Genre Search In Progress", True, (255, 255, 255))
        header_rect = header.get_rect(center=(screen.get_width() / 2, 150))
        screen.blit(header, header_rect)

        # Instruction
        instruction = font_button.render("Resume previous search or start fresh?", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(screen.get_width() / 2, 220))
        screen.blit(instruction, instruction_rect)

        # Buttons
        resume_button.draw(screen)
        fresh_button.draw(screen)

        pygame.display.flip()

    return False  # Should never reach here


def prompt_overwrite_genre_list(screen):
    """
    Display a dialog asking if user wants to overwrite existing genre_search.txt.

    Args:
        screen: Pygame screen surface

    Returns:
        True to overwrite, False to cancel
    """
    font_header = pygame.font.Font(None, 50)
    font_button = pygame.font.Font(None, 40)
    font_warning = pygame.font.Font(None, 30)

    # Create buttons
    overwrite_button = Button(270, 320, 200, 60, "Overwrite")
    cancel_button = Button(554, 320, 150, 60, "Cancel")

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Default to cancel
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False  # ESC = cancel
            if event.type == pygame.MOUSEBUTTONDOWN:
                if overwrite_button.rect.collidepoint(event.pos):
                    return True
                if cancel_button.rect.collidepoint(event.pos):
                    return False

        screen.fill((0, 0, 0))

        # Header
        header = font_header.render("Genre Search Already Exists", True, (255, 200, 0))
        header_rect = header.get_rect(center=(screen.get_width() / 2, 130))
        screen.blit(header, header_rect)

        # Warning
        warning1 = font_warning.render("A genre search is already in progress.", True, (255, 255, 255))
        warning1_rect = warning1.get_rect(center=(screen.get_width() / 2, 200))
        screen.blit(warning1, warning1_rect)

        warning2 = font_warning.render("Overwrite it with the new genre selection?", True, (255, 255, 255))
        warning2_rect = warning2.get_rect(center=(screen.get_width() / 2, 240))
        screen.blit(warning2, warning2_rect)

        # Buttons
        overwrite_button.draw(screen)
        cancel_button.draw(screen)

        pygame.display.flip()

    return False  # Should never reach here


def main():
    screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Music File Cleaner v0.00.22")

    music_files = os.listdir('Music')
    if not music_files:
        print("No music files found in the 'Music' directory.")
        return

    current_file_index = 0

    # State variables
    search_options_screen = None
    genre_selection_screen = None  # v0.00.14
    file_display = None
    full_screen_viewer = None
    result_viewer = None
    preview_comparison_screen = None  # v0.00.02
    final_record_viewer = None  # v0.00.04
    confirmation_screen = None
    updated_tags_viewer = None
    id3_edit_screen = None
    app_state = "search_options"  # Start with search options screen

    # Search configuration from SearchOptionsScreen
    search_config = None

    # v0.00.22: Check if genre_search.txt exists from previous session
    if os.path.exists('genre_search.txt'):
        resume = prompt_resume_genre_search(screen)
        if resume:
            # Load existing list and jump directly to processing
            genre_files = load_genre_list('genre_search.txt')
            if genre_files:
                print(f"Resuming genre search with {len(genre_files)} files remaining")
                search_config = {
                    'mode': 'by_genre',
                    'genre_search': 'Resumed',
                    'genre_files': genre_files,
                    'list_index': 0,
                    'start_index': 0,
                    'add_the_prefix': False
                }
                app_state = "searching_music_file"
                search_options_screen = None  # Skip search options screen
            else:
                # load_genre_list already deleted corrupted file
                print("Could not load genre list, starting fresh")
        else:
            # User wants fresh start, delete existing file
            os.remove('genre_search.txt')
            print("Deleted existing genre_search.txt - starting fresh")

    # Threading variables
    search_thread = None
    search_result = {} # Use a dictionary to pass results from the thread
    load_more_thread = None  # For loading additional results (v0.00.70)
    load_more_result = {}    # Results from load more operation (v0.00.70)

    done = False
    while not done:
        # --- Event Handling (Always Runs) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Make ESC always quit for simplicity and robustness
                    done = True
                    continue

            # --- State-specific Event Handlers ---
            if app_state == "search_options" and search_options_screen:
                config = search_options_screen.handle_event(event)
                if config:
                    # Check if user wants to see genre selection screen
                    if config.get('mode') == 'show_genre_selection':
                        # Transition to genre selection screen
                        genre_selection_screen = GenreSelectionScreen(screen, music_files)
                        app_state = "genre_selection"
                        search_options_screen = None
                    else:
                        # User clicked START, save config and move to searching
                        search_config = config
                        current_file_index = config['start_index']
                        print(f"Search config: {search_config}")
                        app_state = "searching_music_file"

            elif app_state == "genre_selection" and genre_selection_screen:
                config = genre_selection_screen.handle_event(event)
                if config:
                    # User selected a genre, save config and move to searching
                    search_config = config
                    current_file_index = config['start_index']
                    print(f"Genre search config: {search_config}")
                    app_state = "searching_music_file"
                    genre_selection_screen = None

            elif app_state == "file_display" and file_display:
                action, data = file_display.handle_event(event)
                if action == "continue":
                    if search_config and search_config['mode'] in ['from_discogs_list', 'by_genre']:
                        # v0.00.22: Remove completed file from genre_search.txt
                        if search_config['mode'] == 'by_genre':
                            current_filename = search_config['genre_files'][search_config['list_index']]
                            remove_from_genre_list('genre_search.txt', current_filename)

                            # Reload the list to keep search_config in sync
                            updated_list = load_genre_list('genre_search.txt')
                            if updated_list:
                                search_config['genre_files'] = updated_list
                            else:
                                search_config['genre_files'] = []  # List is empty or deleted
                            # Don't increment list_index since we removed current item
                        else:
                            search_config['list_index'] += 1
                    else:
                        current_file_index += 1
                    file_display = None
                    app_state = "searching_music_file"
                elif action == "view_full_screen_image":
                    full_screen_viewer = FullScreenImageViewer(screen, data)
                    app_state = "full_screen_image"
                elif action == "show_confirmation_no_image":
                    confirmation_screen = ConfirmationScreen(screen, data, show_image=False)
                    app_state = "confirmation"
                elif action == "edit_id3_tags":
                    id3_edit_screen = ID3EditScreen(screen, data)
                    app_state = "edit_id3_tags"
                elif action == "view_final_record":
                    # v0.00.06: View full-size final_record.png with metadata and Use This Label
                    final_record_viewer = FinalRecordViewer(screen, data)
                    app_state = "final_record_viewer"
                elif action == "load_more_results":
                    # Increase limit and re-search (v0.00.70)
                    file_display.max_results_limit += 10
                    file_display.is_loading_more = True
                    app_state = "loading_more_results"

            elif app_state == "final_record_viewer" and final_record_viewer:
                # v0.00.06: Handle final record viewer events (with Use This Label)
                result = final_record_viewer.handle_event(event)
                if result:
                    action, data = result if isinstance(result, tuple) else (result, None)
                    if action == "back_to_file_display":
                        app_state = "file_display"
                        final_record_viewer = None
                    elif action == "show_confirmation":
                        # v0.00.06: Use This Label was checked, go to ConfirmationScreen
                        confirmation_screen = ConfirmationScreen(screen, data)
                        app_state = "confirmation"
                        final_record_viewer = None

            elif app_state == "full_screen_image" and full_screen_viewer:
                action, data = full_screen_viewer.handle_event(event)
                if action == "back_to_file_display":
                    app_state = "file_display"
                    full_screen_viewer = None
                elif action == "show_result":
                    result_viewer = ResultViewer(screen, data)
                    app_state = "result_display"

            elif app_state == "result_display" and result_viewer:
                result = result_viewer.handle_event(event)
                if result:
                    action, data = result if isinstance(result, tuple) else (result, None)
                    if action == "back_to_full_screen":
                        app_state = "full_screen_image"
                        result_viewer = None
                    elif action == "show_preview":
                        # v0.00.02: Show preview comparison screen
                        preview_comparison_screen = PreviewComparisonScreen(screen, data)
                        app_state = "preview_comparison"
                        result_viewer = None
                    elif action == "show_confirmation":
                        confirmation_screen = ConfirmationScreen(screen, data)
                        app_state = "confirmation"

            elif app_state == "preview_comparison" and preview_comparison_screen:
                # v0.00.02: Handle preview comparison screen
                result = preview_comparison_screen.handle_event(event)
                if result:
                    action, data = result if isinstance(result, tuple) else (result, None)
                    if action == "back_to_result_viewer":
                        app_state = "result_display"
                        preview_comparison_screen = None
                    elif action == "show_confirmation":
                        confirmation_screen = ConfirmationScreen(screen, data)
                        app_state = "confirmation"
                        preview_comparison_screen = None

            elif app_state == "confirmation" and confirmation_screen:
                result = confirmation_screen.handle_event(event)
                if result:
                    action, data = result if isinstance(result, tuple) else (result, None)
                    if action == "back_to_result":
                        app_state = "result_display"
                        confirmation_screen = None
                    elif action == "back_to_file_display":
                        app_state = "file_display"
                        confirmation_screen = None
                    elif action == "show_updated_tags":
                        updated_tags_viewer = UpdatedTagsViewer(screen, data)
                        app_state = "updated_tags"
                        confirmation_screen = None

            elif app_state == "updated_tags" and updated_tags_viewer:
                action, data = updated_tags_viewer.handle_event(event)
                if action == "continue":
                    if search_config and search_config['mode'] in ['from_discogs_list', 'by_genre']:
                        # v0.00.22: Remove completed file from genre_search.txt
                        if search_config['mode'] == 'by_genre':
                            current_filename = search_config['genre_files'][search_config['list_index']]
                            remove_from_genre_list('genre_search.txt', current_filename)

                            # Reload the list to keep search_config in sync
                            updated_list = load_genre_list('genre_search.txt')
                            if updated_list:
                                search_config['genre_files'] = updated_list
                            else:
                                search_config['genre_files'] = []  # List is empty or deleted
                            # Don't increment list_index since we removed current item
                        else:
                            search_config['list_index'] += 1
                    else:
                        current_file_index += 1
                    updated_tags_viewer = None
                    app_state = "searching_music_file"

            elif app_state == "edit_id3_tags" and id3_edit_screen:
                result = id3_edit_screen.handle_event(event)
                if result:
                    action, data = result if isinstance(result, tuple) else (result, None)
                    if action == "back_to_file_display":
                        app_state = "file_display"
                        id3_edit_screen = None
                    elif action == "show_updated_tags":
                        updated_tags_viewer = UpdatedTagsViewer(screen, data)
                        app_state = "updated_tags"
                        id3_edit_screen = None

        # --- Update Logic ---
        if app_state == "file_display" and file_display:
            file_display.update()

        # --- Drawing and State Logic ---
        screen.fill((30, 30, 30))

        if app_state == "search_options":
            if search_options_screen is None:
                search_options_screen = SearchOptionsScreen(screen, music_files)
            search_options_screen.draw()

        elif app_state == "genre_selection":
            if genre_selection_screen:
                genre_selection_screen.draw()

        elif app_state == "searching_music_file":
            if search_thread is None:
                if current_file_index >= len(music_files):
                    print("Finished all files.")
                    done = True
                else:
                    def search_worker(music_file, bypass_skip=False):
                        fetched_data = {'mutagen_tags': {}, 'discogs_results': [], 'full_release': None, 'mutagen_image_data': None, 'label_image_data': None}
                        should_query_discogs = False  # v0.00.73 - Flag to prevent Discogs queries for processed files

                        try:
                            audio = mutagen.File(os.path.join('Music', music_file))
                            if audio is None: raise ValueError("Could not load audio file")

                            tags = {}
                            tags['time'] = str(datetime.timedelta(seconds=int(audio.info.length)))
                            def get_tag_text(tag_key, default='N/A'):
                                return audio.get(tag_key, [default])[0] if hasattr(audio.get(tag_key), 'text') else default

                            tags['artist'] = get_tag_text('TPE1')
                            tags['title'] = get_tag_text('TIT2')
                            tags['album'] = get_tag_text('TALB')
                            tags['genre'] = get_tag_text('TCON')
                            tags['year'] = get_tag_text('TDRC', get_tag_text('TYER'))  # Try TDRC (ID3v2.4), fall back to TYER (ID3v2.3)
                            tags['comment'] = get_tag_text('COMM::eng', get_tag_text('COMM'))

                            # Skip files that have already been processed (v0.00.60)
                            # UNLESS bypass_skip is True (artist/title search modes) (v0.00.63)
                            if not bypass_skip:
                                # Check if comment contains "image" or "noimage" - indicates file was already updated
                                comment = tags.get('comment', '').lower()
                                if 'image' in comment or 'noimage' in comment:
                                    print(f"Skipping {music_file} - already processed (comment: {tags.get('comment')})")
                                    return  # Exit early without setting search_result data
                            else:
                                print(f"Processing {music_file} (skip logic bypassed - artist/title search mode)")

                            # v0.00.73 - Only set flag to True if we passed the skip check
                            should_query_discogs = True
                            fetched_data['mutagen_tags'] = tags

                            for key in audio.keys():
                                if key.startswith('APIC'):
                                    fetched_data['mutagen_image_data'] = audio[key].data
                                    break
                        except Exception as e:
                            print(f"Error reading mutagen data for {music_file}: {e}")
                            should_query_discogs = False  # v0.00.73 - Don't query if error reading tags

                        # v0.00.73 - ONLY query Discogs if flag is True (skip check passed and no errors)
                        if should_query_discogs:
                            try:
                                artist, title = music_file.replace('.mp3', '').rsplit(' - ', 1)
                            except ValueError:
                                artist, title = "Unknown Artist", music_file.replace('.mp3', '')

                            # Check if we need to add "The " prefix based on search_config
                            search_artist = artist
                            if search_config and search_config.get('mode') == 'from_artist' and search_config.get('add_the_prefix'):
                                # Artist is in the_bands.txt, check if filename already has "The "
                                if not artist.lower().startswith('the '):
                                    search_artist = "The " + artist
                                    print(f"Adding 'The ' prefix for Discogs search: '{search_artist}'")

                            results = search_discogs(f"{search_artist} - {title}")
                            fetched_data['discogs_results'] = results

                            if results:
                                try:
                                    release = d.release(results[0].id)
                                    fetched_data['full_release'] = release

                                    # v0.00.12: Download ALL images and filter in parallel with EARLY OCR validation
                                    # Use original filename artist/title (not search_artist) for OCR validation
                                    filtered_images = download_and_filter_images_parallel(release, artist_name=artist, song_title=title, max_workers=5)
                                    fetched_data['label_images_data'] = [img_bytes for img_bytes, circle_data in filtered_images]
                                except Exception as e:
                                    print(f"Error fetching full release or image: {e}")

                            search_result['data'] = fetched_data

                    # Handle discogs list mode and genre search mode
                    if search_config and search_config['mode'] == 'from_discogs_list':
                        # Get next song from the list
                        if search_config['list_index'] >= len(search_config['song_list']):
                            print("Finished processing all songs in discogs_search_list.txt")
                            app_state = "search_options"
                            search_options_screen = SearchOptionsScreen(screen, music_files)
                            search_config = None  # Clear search config
                        else:
                            filename = search_config['song_list'][search_config['list_index']]
                            current_num = search_config['list_index'] + 1
                            total_num = len(search_config['song_list'])
                            print(f"Processing song {current_num} of {total_num}: {filename}")
                            current_file_index = find_music_file_index(music_files, filename)
                            if current_file_index == -1:
                                print(f"Skipping '{filename}' - not found in Music directory")
                                search_config['list_index'] += 1
                            else:
                                current_file = music_files[current_file_index]
                                search_result.clear()
                                bypass = False  # Use skip logic for already-processed files
                                search_thread = threading.Thread(target=search_worker, args=(current_file, bypass))
                                search_thread.start()
                    elif search_config and search_config['mode'] == 'by_genre':
                        # Get next file from genre search results
                        if search_config['list_index'] >= len(search_config['genre_files']):
                            print(f"Finished processing all files with genre '{search_config['genre_search']}'")

                            # v0.00.22: Delete genre_search.txt when complete
                            if os.path.exists('genre_search.txt'):
                                os.remove('genre_search.txt')
                                print("Deleted genre_search.txt - processing complete")

                            app_state = "search_options"
                            search_options_screen = SearchOptionsScreen(screen, music_files)
                            genre_selection_screen = None  # Clear genre screen
                            search_config = None  # Clear search config
                        else:
                            filename = search_config['genre_files'][search_config['list_index']]
                            current_num = search_config['list_index'] + 1
                            total_num = len(search_config['genre_files'])
                            print(f"Processing genre file {current_num} of {total_num}: {filename}")
                            current_file_index = find_music_file_index(music_files, filename)
                            if current_file_index == -1:
                                # v0.00.22: File not found - remove from genre_search.txt
                                print(f"Skipping '{filename}' - not found in Music directory")
                                remove_from_genre_list('genre_search.txt', filename)

                                # Reload the genre list since we just modified it
                                updated_list = load_genre_list('genre_search.txt')
                                if updated_list:
                                    search_config['genre_files'] = updated_list
                                else:
                                    # List is now empty or deleted, we're done
                                    search_config['genre_files'] = []
                                # Don't increment list_index since we removed current item
                            else:
                                current_file = music_files[current_file_index]
                                search_result.clear()
                                bypass = False  # Use skip logic for genre search (skip already processed files)
                                search_thread = threading.Thread(target=search_worker, args=(current_file, bypass))
                                search_thread.start()
                    else:
                        current_file = music_files[current_file_index]
                        search_result.clear()
                        # Bypass skip logic if using artist/title search mode
                        bypass = search_config and search_config['mode'] != 'from_top'
                        search_thread = threading.Thread(target=search_worker, args=(current_file, bypass))
                        search_thread.start()

            searching_text = FONT.render("Searching...", True, (255, 255, 255))
            text_rect = searching_text.get_rect(center=screen.get_rect().center)
            screen.blit(searching_text, text_rect)

            if search_thread is not None and not search_thread.is_alive():
                fetched_data = search_result.get('data')
                search_thread = None

                if fetched_data and fetched_data.get('discogs_results'):
                    try:
                        artist, title = music_files[current_file_index].replace('.mp3', '').rsplit(' - ', 1)
                    except ValueError:
                        artist, title = "Unknown Artist", music_files[current_file_index].replace('.mp3', '')

                    file_display = FileDisplay(screen, music_files[current_file_index], artist, title, fetched_data)
                    app_state = "file_display"
                else:
                    print(f"No Discogs results for {music_files[current_file_index]}, skipping.")
                    if search_config and search_config['mode'] in ['from_discogs_list', 'by_genre']:
                        # v0.00.22: Remove skipped file from genre_search.txt
                        if search_config['mode'] == 'by_genre':
                            current_filename = search_config['genre_files'][search_config['list_index']]
                            remove_from_genre_list('genre_search.txt', current_filename)

                            # Reload the list to keep search_config in sync
                            updated_list = load_genre_list('genre_search.txt')
                            if updated_list:
                                search_config['genre_files'] = updated_list
                            else:
                                search_config['genre_files'] = []  # List is empty or deleted
                            # Don't increment list_index since we removed current item
                        else:
                            search_config['list_index'] += 1
                    else:
                        current_file_index += 1
                    file_display = None

        elif app_state == "loading_more_results":
            # Re-search with increased limit (v0.00.70)
            if load_more_thread is None:
                def load_more_worker():
                    try:
                        artist, title = music_files[current_file_index].replace('.mp3', '').rsplit(' - ', 1)
                    except ValueError:
                        artist, title = "Unknown Artist", music_files[current_file_index].replace('.mp3', '')

                    # Check if we need to add "The " prefix
                    search_artist = artist
                    if search_config and search_config.get('mode') == 'from_artist' and search_config.get('add_the_prefix'):
                        if not artist.lower().startswith('the '):
                            search_artist = "The " + artist

                    # Re-search with new limit
                    results = search_discogs(f"{search_artist} - {title}", max_results=file_display.max_results_limit)
                    load_more_result['results'] = results

                load_more_result.clear()
                load_more_thread = threading.Thread(target=load_more_worker)
                load_more_thread.start()

            loading_text = FONT.render(f"Loading {file_display.max_results_limit - 10} more results...", True, (255, 255, 255))
            text_rect = loading_text.get_rect(center=screen.get_rect().center)
            screen.blit(loading_text, text_rect)

            if load_more_thread is not None and not load_more_thread.is_alive():
                new_results = load_more_result.get('results', [])
                if new_results:
                    # Update file_display with new results
                    file_display.discogs_results = new_results
                    print(f"Loaded {len(new_results)} total results (was {file_display.max_results_limit - 10}, now {len(new_results)})")
                    # Fetch the first new result's full data
                    if len(new_results) > file_display.discogs_result_index:
                        file_display._update_with_current_discogs_result()
                load_more_thread = None
                file_display.is_loading_more = False
                app_state = "file_display"

        elif app_state == "file_display":
            if file_display:
                file_display.draw(screen)

        elif app_state == "full_screen_image":
            if full_screen_viewer:
                full_screen_viewer.draw()

        elif app_state == "result_display":
            if result_viewer:
                result_viewer.draw()

        elif app_state == "preview_comparison":
            # v0.00.02: Draw preview comparison screen
            if preview_comparison_screen:
                preview_comparison_screen.draw()

        elif app_state == "final_record_viewer":
            # v0.00.05: Draw final record viewer (420x420)
            if final_record_viewer:
                final_record_viewer.draw()

        elif app_state == "confirmation":
            if confirmation_screen:
                confirmation_screen.draw()

        elif app_state == "updated_tags":
            if updated_tags_viewer:
                updated_tags_viewer.draw()

        elif app_state == "edit_id3_tags":
            if id3_edit_screen:
                id3_edit_screen.draw()

        pygame.display.flip()

    if search_thread and search_thread.is_alive():
        search_thread.join()

    pygame.quit()

if __name__ == '__main__':
    main()
