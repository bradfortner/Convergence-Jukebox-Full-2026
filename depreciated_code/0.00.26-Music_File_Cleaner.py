import pygame
import discogs_client
import jukebox_config
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

# Configure logging to write to a file
logging.basicConfig(filename='clean_up_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s', filemode='w')


# Initialize Pygame and global variables
pygame.init()
FONT = pygame.font.Font(None, 32)
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

# Initialize Discogs client
d = discogs_client.Client('YourApp/1.0', user_token=jukebox_config.DISCOGS_USER_TOKEN)

def search_discogs(query, page=1, search_type='release'):
    """
    Searches the Discogs database for releases and returns a list of 45rpm releases for a given page.
    """
    print(f"\nSearching Discogs for '{query}' (page: {page}, type: {search_type})...")
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
                if len(release_list) >= 10:
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
            elif event.key not in (pygame.K_TAB, pygame.K_RETURN):
                if self.text == self.placeholder_text:
                    self.text = ''
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

        button_y_start = 620
        self.next_discogs_file_button = Button(screen.get_width() / 2 - 110, button_y_start, 220, 32, "Next Discogs File")
        self.next_music_file_button = Button(screen.get_width() / 2 - 110, button_y_start + 50, 220, 32, "Next Music File")
        self.focusable_widgets = [self.next_discogs_file_button, self.next_music_file_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

        self.thumb_rect = pygame.Rect(450, 100, 200, 200)
        self.mutagen_thumb_rect = pygame.Rect(950, 100, 150, 150)

        # --- Populate Data from Prefetched Dictionary ---
        self.mutagen_tags = fetched_data.get('mutagen_tags', {})
        self.discogs_results = fetched_data.get('discogs_results', [])
        self.full_release = fetched_data.get('full_release', None)

        mutagen_image_data = fetched_data.get('mutagen_image_data')
        label_image_data = fetched_data.get('label_image_data')

        self.mutagen_image_surface = None
        if mutagen_image_data:
            try:
                image_file = io.BytesIO(mutagen_image_data)
                self.mutagen_image_surface = pygame.image.load(image_file)
            except pygame.error as e:
                print(f"Error loading mutagen image data: {e}")

        self.label_image_surface = None
        if label_image_data:
            try:
                image_file = io.BytesIO(label_image_data)
                self.label_image_surface = pygame.image.load(image_file)
            except pygame.error as e:
                print(f"Error loading discogs image data: {e}")

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

        # --- Threading for cycling through results ---
        self.fetch_thread = None
        self.fetch_result = {}

        # --- Process Prefetched Discogs Data ---
        if self.full_release:
            self._process_discogs_release(self.full_release, label_image_data)

    def _process_discogs_release(self, release, image_data=None):
        """Process a Discogs release and update all display data"""
        if release.artists:
            self.discogs_artist = release.artists[0].name
        self.discogs_title = release.title
        self.year = getattr(release, 'year', 'N/A')
        self.song_length, self.genres = self._get_song_length_and_genres(release)

        # Update label image if provided
        if image_data:
            try:
                image_file = io.BytesIO(image_data)
                self.label_image_surface = pygame.image.load(image_file)
            except pygame.error as e:
                print(f"Error loading discogs image data: {e}")

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

    def _update_with_current_discogs_result(self):
        """Cycle to the next Discogs result and fetch its full details"""
        if not self.discogs_results:
            print("No Discogs results to cycle through.")
            return

        if self.is_fetching_discogs_data:
            print("Already fetching data, please wait...")
            return

        # Increment index with wraparound
        self.discogs_result_index = (self.discogs_result_index + 1) % len(self.discogs_results)
        print(f"Cycling to Discogs result {self.discogs_result_index + 1} of {len(self.discogs_results)}")

        # Start fetching in background thread
        def fetch_worker():
            fetched = {'full_release': None, 'image_data': None}
            try:
                result = self.discogs_results[self.discogs_result_index]
                release = d.release(result.id)
                fetched['full_release'] = release

                if release.images:
                    img_response = requests.get(release.images[0]['uri'], headers={'User-Agent': 'YourApp/1.0'})
                    img_response.raise_for_status()
                    fetched['image_data'] = img_response.content
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

    def update(self):
        """Check if background fetch is complete and process results"""
        if self.fetch_thread and not self.fetch_thread.is_alive():
            self.fetch_thread = None
            self.is_fetching_discogs_data = False

            release = self.fetch_result.get('full_release')
            image_data = self.fetch_result.get('image_data')

            if release:
                self.full_release = release
                self._process_discogs_release(release, image_data)
                print(f"Updated to: {self.discogs_artist} - {self.discogs_title}")
            else:
                print("Failed to fetch Discogs data")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
            elif event.key == pygame.K_RETURN:
                focused_widget = self.focusable_widgets[self.focused_index]
                if focused_widget == self.next_music_file_button:
                    return "continue", None
                elif focused_widget == self.next_discogs_file_button:
                    self._update_with_current_discogs_result()

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
                    'year_match': self.year_match
                }
                return "view_full_screen_image", data_bundle
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
                    'year_match': self.year_match
                }
                return "view_full_screen_image", data_bundle
            if self.next_music_file_button.rect.collidepoint(event.pos):
                return "continue", None
            if self.next_discogs_file_button.rect.collidepoint(event.pos):
                self._update_with_current_discogs_result()
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
        else:
            pygame.draw.rect(screen, (50, 50, 50), self.thumb_rect)
            text_surf = self.font_label.render("No Label Image", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.thumb_rect.center)
            screen.blit(text_surf, text_rect)

        # Result counter
        if self.discogs_results:
            counter_text = f"Result {self.discogs_result_index + 1} of {len(self.discogs_results)}"
            counter_surf = self.font_id3_label.render(counter_text, True, (200, 200, 200))
            screen.blit(counter_surf, (450, 305))

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
        self.debug_button = Button(screen.get_width() - 300, 10, 140, 32, "Debug")
        self.focusable_widgets = [self.back_button, self.create_label_button, self.debug_button]
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
                elif focused_widget == self.debug_button:
                    processed_image = extract_label(self.image_surface, debug=True)
                    result_data = {'label_image': processed_image, 'data_bundle': self.data_bundle}
                    return "show_result", result_data

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_file_display", None
            if self.create_label_button.rect.collidepoint(event.pos):
                processed_image = extract_label(self.image_surface)
                result_data = {'label_image': processed_image, 'data_bundle': self.data_bundle}
                return "show_result", result_data
            if self.debug_button.rect.collidepoint(event.pos):
                processed_image = extract_label(self.image_surface, debug=True)
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
            # Define the save path and ensure the directory exists
            save_path = os.path.join('images', 'new_cutout_label.png')
            os.makedirs('images', exist_ok=True)

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
                # Do pygame operations in main thread to avoid surface locking issues
                resized_surface = pygame.transform.scale(self.image_surface, (1000, 1000))
                # Only file I/O runs in background thread
                save_thread = threading.Thread(target=self._save_label_image_to_disk, args=(resized_surface,))
                save_thread.start()
                # Show confirmation screen with label and data
                confirmation_data = {
                    'label_image': self.image_surface,
                    'data_bundle': self.data_bundle
                }
                return "show_confirmation", confirmation_data

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


class ConfirmationScreen:
    def __init__(self, screen, confirmation_data):
        self.screen = screen
        self.label_image = confirmation_data['label_image']
        self.data_bundle = confirmation_data['data_bundle']

        # Process and sanitize data
        self.title = self._get_title()
        self.artist = self._get_artist()
        self.year = self._get_year()
        self.time = self.data_bundle['mutagen_tags'].get('time', 'N/A')
        self.genres = self._get_genres()
        self.comment = self._get_comment()

        # Buttons
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.confirm_button = Button(screen.get_width() - 150, 10, 130, 32, "Confirm")

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

        self.focusable_widgets = [self.back_button, self.confirm_button]
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
        """Always use Discogs artist, sanitized"""
        artist = self.data_bundle['discogs_artist']
        return self._sanitize_text(artist)

    def _get_year(self):
        """Always use ID3 year"""
        year = self.data_bundle['mutagen_tags'].get('year', 'N/A')
        # Extract just the year part (handles formats like "2024-01-01" -> "2024")
        if year and year != 'N/A' and len(str(year)) >= 4:
            return str(year)[:4]
        return str(year)

    def _get_genres(self):
        """Use Discogs genres"""
        genres = self.data_bundle['discogs_genres']
        return ", ".join(genres) if genres else "N/A"

    def _get_comment(self):
        """Use ID3 comment + ' image'"""
        comment = self.data_bundle['mutagen_tags'].get('comment', '')
        if comment and comment != 'N/A' and comment.strip():
            return comment + " image"
        else:
            return "image"

    def handle_event(self, event):
        # Handle checkbox clicks first
        for checkbox in self.checkboxes:
            checkbox.handle_event(event)

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
                    return "back_to_result"
                elif focused_widget == self.confirm_button:
                    # Print final values from checkboxes and InputBoxes
                    print("\n=== CONFIRMATION SCREEN - FINAL VALUES ===")
                    print(f"Title: {self.title if self.title_checkbox.checked else self.title_input.text}")
                    print(f"Artist: {self.artist if self.artist_checkbox.checked else self.artist_input.text}")
                    print(f"Year: {self.year if self.year_checkbox.checked else self.year_input.text}")
                    print(f"Time: {self.time if self.time_checkbox.checked else self.time_input.text}")
                    print(f"Genre: {self.genres if self.genre_checkbox.checked else self.genre_input.text}")
                    print(f"Comment: {self.comment if self.comment_checkbox.checked else self.comment_input.text}")
                    print("==========================================\n")
                    return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_result"
            if self.confirm_button.rect.collidepoint(event.pos):
                # Print final values from checkboxes and InputBoxes
                print("\n=== CONFIRMATION SCREEN - FINAL VALUES ===")
                print(f"Title: {self.title if self.title_checkbox.checked else self.title_input.text}")
                print(f"Artist: {self.artist if self.artist_checkbox.checked else self.artist_input.text}")
                print(f"Year: {self.year if self.year_checkbox.checked else self.year_input.text}")
                print(f"Time: {self.time if self.time_checkbox.checked else self.time_input.text}")
                print(f"Genre: {self.genres if self.genre_checkbox.checked else self.genre_input.text}")
                print(f"Comment: {self.comment if self.comment_checkbox.checked else self.comment_input.text}")
                print("==========================================\n")
                return None

        return None

    def draw(self):
        # Draw label image centered at top
        if self.label_image:
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
        self.confirm_button.draw(self.screen)


def main():
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Music File Cleaner")

    music_files = os.listdir('music')
    if not music_files:
        print("No music files found in the 'music' directory.")
        return

    current_file_index = 0

    # State variables
    file_display = None
    full_screen_viewer = None
    result_viewer = None
    confirmation_screen = None
    app_state = "searching_music_file"

    # Threading variables
    search_thread = None
    search_result = {} # Use a dictionary to pass results from the thread

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
            if app_state == "file_display" and file_display:
                action, data = file_display.handle_event(event)
                if action == "continue":
                    current_file_index += 1
                    file_display = None
                    app_state = "searching_music_file"
                elif action == "view_full_screen_image":
                    full_screen_viewer = FullScreenImageViewer(screen, data)
                    app_state = "full_screen_image"

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
                    elif action == "show_confirmation":
                        confirmation_screen = ConfirmationScreen(screen, data)
                        app_state = "confirmation"

            elif app_state == "confirmation" and confirmation_screen:
                action = confirmation_screen.handle_event(event)
                if action == "back_to_result":
                    app_state = "result_display"
                    confirmation_screen = None

        # --- Update Logic ---
        if app_state == "file_display" and file_display:
            file_display.update()

        # --- Drawing and State Logic ---
        screen.fill((30, 30, 30))

        if app_state == "searching_music_file":
            if search_thread is None:
                if current_file_index >= len(music_files):
                    print("Finished all files.")
                    done = True
                else:
                    def search_worker(music_file):
                        fetched_data = {'mutagen_tags': {}, 'discogs_results': [], 'full_release': None, 'mutagen_image_data': None, 'label_image_data': None}
                        try:
                            audio = mutagen.File(os.path.join('music', music_file))
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
                            fetched_data['mutagen_tags'] = tags

                            for key in audio.keys():
                                if key.startswith('APIC'):
                                    fetched_data['mutagen_image_data'] = audio[key].data
                                    break
                        except Exception as e:
                            print(f"Error reading mutagen data for {music_file}: {e}")

                        try:
                            artist, title = music_file.replace('.mp3', '').rsplit(' - ', 1)
                        except ValueError:
                            artist, title = "Unknown Artist", music_file.replace('.mp3', '')

                        results = search_discogs(f"{artist} - {title}")
                        fetched_data['discogs_results'] = results

                        if results:
                            try:
                                release = d.release(results[0].id)
                                fetched_data['full_release'] = release
                                if release.images:
                                    img_response = requests.get(release.images[0]['uri'], headers={'User-Agent': 'YourApp/1.0'})
                                    img_response.raise_for_status()
                                    fetched_data['label_image_data'] = img_response.content
                            except Exception as e:
                                print(f"Error fetching full release or image: {e}")

                        search_result['data'] = fetched_data

                    current_file = music_files[current_file_index]
                    search_result.clear()
                    search_thread = threading.Thread(target=search_worker, args=(current_file,))
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
                    current_file_index += 1
                    file_display = None

        elif app_state == "file_display":
            if file_display:
                file_display.draw(screen)

        elif app_state == "full_screen_image":
            if full_screen_viewer:
                full_screen_viewer.draw()

        elif app_state == "result_display":
            if result_viewer:
                result_viewer.draw()

        elif app_state == "confirmation":
            if confirmation_screen:
                confirmation_screen.draw()

        pygame.display.flip()

    if search_thread and search_thread.is_alive():
        search_thread.join()

    pygame.quit()

if __name__ == '__main__':
    main()
