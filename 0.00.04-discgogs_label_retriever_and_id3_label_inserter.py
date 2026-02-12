"""
Music File Cleaner v0.00.04
Generate final_record.png to original specs (250x250), show thumbnail, make clickable to view full-size

CHANGELOG v0.00.04:
- Generate final_record.png using original specifications (250x250 size)
- Show thumbnail of final_record.png on FileDisplay browsing screen
- Click thumbnail to view full-size final_record.png (250x250) in dedicated viewer
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
import mutagen
import cv2
import numpy as np
import time
import logging
import threading
import re
import label_pressing_module # Local Module: Label Image Generation
import id3_tag_writer_module # Local Module: ID3 Tag Writer

# Configure logging to write to a file
logging.basicConfig(filename='clean_up_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s', filemode='w')


# Initialize Pygame and global variables
pygame.init()
FONT = pygame.font.Font(None, 32)
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

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

    def _generate_adaptor_preview(self):
        """
        v0.00.04: Generate final_record.png at original specs (250x250)
        and load it as thumbnail for FileDisplay browsing screen
        """
        try:
            print("Generating final_record.png with adaptor (250x250)...")

            # Step 1: Extract label using circle detection
            cropped_label_surface = extract_label(self.label_image_surface)

            if not cropped_label_surface:
                print("Could not extract label - no circles detected")
                self.adaptor_preview_surface = None
                return

            # Step 2: Save cropped label to new_cutout_label.png
            pygame.image.save(cropped_label_surface, 'new_cutout_label.png')

            # Step 3: Generate final_record.png using original specifications (250x250)
            success = label_pressing_module.combine_pngs(
                label_path='new_cutout_label.png',
                adaptor_path='adaptor.png',
                output_path='final_record.png',
                size=(250, 250),
                base_record_path='blank_record.png'
            )

            if not success:
                print("Failed to generate final_record.png")
                self.adaptor_preview_surface = None
                return

            # Step 4: Load final_record.png as thumbnail surface
            self.adaptor_preview_surface = pygame.image.load('final_record.png')
            print("✓ final_record.png generated successfully (250x250)")

        except Exception as e:
            print(f"Error generating adaptor preview: {e}")
            self.adaptor_preview_surface = None

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

                # v0.00.01: Download ALL images and filter using circle detection
                if release.images:
                    print(f"Found {len(release.images)} images, filtering for labels...")
                    filtered_count = 0
                    for idx, img_info in enumerate(release.images):
                        try:
                            img_response = requests.get(img_info['uri'], headers={'User-Agent': 'YourApp/1.0'})
                            img_response.raise_for_status()
                            img_bytes = img_response.content

                            # Check if image contains circular patterns (45rpm label)
                            if detect_circular_label(img_bytes):
                                fetched['images_data'].append(img_bytes)
                                filtered_count += 1
                                print(f"  Image {idx+1}/{len(release.images)}: LABEL DETECTED ✓")
                            else:
                                print(f"  Image {idx+1}/{len(release.images)}: No circles, skipping")
                        except Exception as e:
                            print(f"  Image {idx+1}: Error downloading - {e}")

                    print(f"Filtered {filtered_count} label images out of {len(release.images)} total images")
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
                    'filename': self.filename
                }
                return "view_full_screen_image", data_bundle
            # v0.00.04: Click on adaptor preview thumbnail to view full-size final_record.png
            if self.adaptor_preview_rect.collidepoint(event.pos) and self.adaptor_preview_surface:
                return "view_final_record", None
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
    v0.00.01: Quick check if image contains circular patterns (45rpm label).
    Returns True if circles are detected, False otherwise.
    Takes raw image bytes as input (from HTTP response).
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False

        # Convert to grayscale and apply blur
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # Detect circles
        rows = gray.shape[0]
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                   param1=100, param2=85,
                                   minRadius=int(rows * 0.2), maxRadius=int(rows * 0.49))

        # Return True if at least one circle was detected
        return circles is not None
    except Exception as e:
        print(f"Error in detect_circular_label: {e}")
        return False

def extract_label(pygame_surface, debug=False):
    """
    Takes a pygame surface, finds the 45rpm label using circle detection,
    and returns a new cropped pygame surface of just the label.
    """
    try:
        # 1. Convert Pygame surface to OpenCV image
        view = pygame.surfarray.pixels3d(pygame_surface)
        img = cv2.cvtColor(view.transpose([1, 0, 2]), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # 2. Detect Circles, with a higher accumulator threshold for more accuracy
        rows = gray.shape[0]
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                   param1=100, param2=85, # Increased param2 to 85 for stricter detection
                                   minRadius=int(rows * 0.2), maxRadius=int(rows * 0.49)) # Increased maxRadius to 0.49

        if circles is not None:
            # Take the first and most prominent circle found
            c = circles[0][0]
            center_x, center_y, r_large = int(c[0]), int(c[1]), int(c[2])

            # Derive the inner hole based on a standard 45rpm ratio
            r_small = int(r_large * 0.43)

            # 3. Create Mask
            mask = np.zeros_like(gray)
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
            raise ValueError("No circles were detected by HoughCircles with the new parameters.")

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

                # Generate final_record.png for preview
                print("Generating preview with adaptor...")
                success = label_pressing_module.combine_pngs(
                    label_path='new_cutout_label.png',
                    adaptor_path='adaptor.png',
                    output_path='final_record.png',
                    size=(250, 250),
                    base_record_path='blank_record.png'
                )

                if not success:
                    print("ERROR: Failed to generate preview image")
                    return None

                # v0.00.02: Show preview comparison screen instead of confirmation
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
    v0.00.04: Simple viewer to display final_record.png at its original size (250x250)
    Opened when user clicks the adaptor preview thumbnail on FileDisplay
    """
    def __init__(self, screen):
        self.screen = screen
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.font_header = pygame.font.Font(None, 32)

        # Load final_record.png
        try:
            self.final_record_surface = pygame.image.load('final_record.png')
            print("Loaded final_record.png for full-size viewing")
        except Exception as e:
            print(f"Error loading final_record.png: {e}")
            self.final_record_surface = None

        self.focusable_widgets = [self.back_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "back_to_file_display", None
            elif event.key == pygame.K_ESCAPE:
                return "back_to_file_display", None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_file_display", None

        return None

    def draw(self):
        # Header
        header = self.font_header.render("Final Record (250x250)", True, (255, 255, 255))
        header_x = (self.screen.get_width() - header.get_width()) // 2
        self.screen.blit(header, (header_x, 50))

        # Display final_record.png at its original size (250x250) centered
        if self.final_record_surface:
            # Center the 250x250 image on screen
            screen_center_x = self.screen.get_width() // 2
            screen_center_y = self.screen.get_height() // 2
            image_x = screen_center_x - 125  # 250/2 = 125
            image_y = screen_center_y - 125

            self.screen.blit(self.final_record_surface, (image_x, image_y))

            # Show size info below image
            size_text = self.font_header.render("(Actual size: 250x250)", True, (200, 200, 200))
            size_x = (self.screen.get_width() - size_text.get_width()) // 2
            self.screen.blit(size_text, (size_x, image_y + 270))
        else:
            # Error message
            error_surf = self.font_header.render("Error loading final_record.png", True, (255, 100, 100))
            error_x = (self.screen.get_width() - error_surf.get_width()) // 2
            error_y = self.screen.get_height() // 2
            self.screen.blit(error_surf, (error_x, error_y))

        # Draw back button
        self.back_button.draw(self.screen)


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
        # Check and update the_bands.txt file
        self._check_and_update_bands_file(sanitized)
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

    def _check_and_update_bands_file(self, artist_name):
        """Check if artist (without 'The ') is in the_bands.txt file, add if missing"""
        if not artist_name or artist_name == 'N/A':
            return

        bands_file_path = 'the_bands.txt'
        artist_lower = artist_name.lower()

        try:
            # Read existing bands
            if os.path.exists(bands_file_path):
                with open(bands_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    bands_list = [band.strip().lower() for band in content.split(',')]
            else:
                bands_list = []
                content = ''

            # Check if artist is already in the list
            if artist_lower not in bands_list:
                # Add artist to file
                if content and not content.endswith(','):
                    # File has content but doesn't end with comma
                    new_content = content + ',' + artist_name.lower()
                elif content:
                    # File ends with comma
                    new_content = content + artist_name.lower()
                else:
                    # File is empty
                    new_content = artist_name.lower()

                with open(bands_file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Added '{artist_name.lower()}' to {bands_file_path}")
            else:
                print(f"'{artist_name.lower()}' already in {bands_file_path}")
        except Exception as e:
            print(f"Error updating {bands_file_path}: {e}")

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

        # Four mutually exclusive checkboxes
        checkbox_x = 100
        y_start = 150
        self.option1_checkbox = Checkbox(checkbox_x, y_start, 20, 20)
        self.option2_checkbox = Checkbox(checkbox_x, y_start + 80, 20, 20)
        self.option3_checkbox = Checkbox(checkbox_x, y_start + 160, 20, 20)
        self.option4_checkbox = Checkbox(checkbox_x, y_start + 240, 20, 20)

        # Default: option 1 is checked
        self.option1_checkbox.checked = True

        # Input boxes for options 2 and 3
        input_x = 300
        input_width = 600
        self.artist_input = InputBox(input_x, y_start + 110, input_width, 30, "Enter Artist Name")
        self.title_input = InputBox(input_x, y_start + 190, input_width, 30, "Enter Title")

        # Start button
        self.start_button = Button(screen.get_width() / 2 - 60, 500, 120, 40, "START")

        self.checkboxes = [self.option1_checkbox, self.option2_checkbox, self.option3_checkbox, self.option4_checkbox]
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

        return None

    def draw(self):
        # Header
        header = self.font_header.render("How Would You Like To Search Discogs", True, (255, 255, 255))
        header_rect = header.get_rect(center=(self.screen.get_width() / 2, 80))
        self.screen.blit(header, header_rect)

        # Option 1
        self.option1_checkbox.draw(self.screen)
        label1 = self.font_label.render("From The Top Of My Music Directory", True, (255, 255, 255))
        self.screen.blit(label1, (130, 145))

        # Option 2
        self.option2_checkbox.draw(self.screen)
        label2 = self.font_label.render("From The Top File For This Artist", True, (255, 255, 255))
        self.screen.blit(label2, (130, 225))

        # Artist input (only visible when option 2 is checked)
        if self.option2_checkbox.checked:
            artist_label = self.font_label.render("Artist:", True, (200, 200, 200))
            self.screen.blit(artist_label, (150, 260))
            self.artist_input.draw(self.screen)

        # Option 3
        self.option3_checkbox.draw(self.screen)
        label3 = self.font_label.render("For This Title", True, (255, 255, 255))
        self.screen.blit(label3, (130, 305))

        # Title input (only visible when option 3 is checked)
        if self.option3_checkbox.checked:
            title_label = self.font_label.render("Title:", True, (200, 200, 200))
            self.screen.blit(title_label, (150, 340))
            self.title_input.draw(self.screen)

        # Option 4
        self.option4_checkbox.draw(self.screen)
        label4 = self.font_label.render("Search From Discogs Text List", True, (255, 255, 255))
        self.screen.blit(label4, (130, 385))

        # Start button
        self.start_button.draw(self.screen)


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


def main():
    screen = pygame.display.set_mode((1024, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Music File Cleaner v0.00.81")

    music_files = os.listdir('Music')
    if not music_files:
        print("No music files found in the 'Music' directory.")
        return

    current_file_index = 0

    # State variables
    search_options_screen = None
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
                    # User clicked START, save config and move to searching
                    search_config = config
                    current_file_index = config['start_index']
                    print(f"Search config: {search_config}")
                    app_state = "searching_music_file"

            elif app_state == "file_display" and file_display:
                action, data = file_display.handle_event(event)
                if action == "continue":
                    if search_config and search_config['mode'] == 'from_discogs_list':
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
                    # v0.00.04: View full-size final_record.png (250x250)
                    final_record_viewer = FinalRecordViewer(screen)
                    app_state = "final_record_viewer"
                elif action == "load_more_results":
                    # Increase limit and re-search (v0.00.70)
                    file_display.max_results_limit += 10
                    file_display.is_loading_more = True
                    app_state = "loading_more_results"

            elif app_state == "final_record_viewer" and final_record_viewer:
                # v0.00.04: Handle final record viewer events
                result = final_record_viewer.handle_event(event)
                if result:
                    action, data = result if isinstance(result, tuple) else (result, None)
                    if action == "back_to_file_display":
                        app_state = "file_display"
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
                    if search_config and search_config['mode'] == 'from_discogs_list':
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

                                    # v0.00.01: Download ALL images and filter using circle detection
                                    fetched_data['label_images_data'] = []
                                    if release.images:
                                        print(f"Found {len(release.images)} images, filtering for labels...")
                                        filtered_count = 0
                                        for idx, img_info in enumerate(release.images):
                                            try:
                                                img_response = requests.get(img_info['uri'], headers={'User-Agent': 'YourApp/1.0'})
                                                img_response.raise_for_status()
                                                img_bytes = img_response.content

                                                # Check if image contains circular patterns (45rpm label)
                                                if detect_circular_label(img_bytes):
                                                    fetched_data['label_images_data'].append(img_bytes)
                                                    filtered_count += 1
                                                    print(f"  Image {idx+1}/{len(release.images)}: LABEL DETECTED ✓")
                                                else:
                                                    print(f"  Image {idx+1}/{len(release.images)}: No circles, skipping")
                                            except Exception as e:
                                                print(f"  Image {idx+1}: Error downloading - {e}")

                                        print(f"Filtered {filtered_count} label images out of {len(release.images)} total images")
                                except Exception as e:
                                    print(f"Error fetching full release or image: {e}")

                            search_result['data'] = fetched_data

                    # Handle discogs list mode
                    if search_config and search_config['mode'] == 'from_discogs_list':
                        # Get next song from the list
                        if search_config['list_index'] >= len(search_config['song_list']):
                            print("Finished processing all songs in discogs_search_list.txt")
                            app_state = "search_options"
                            search_options = SearchOptionsScreen(screen, music_files)
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
                    if search_config and search_config['mode'] == 'from_discogs_list':
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
            # v0.00.04: Draw final record viewer (250x250)
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
