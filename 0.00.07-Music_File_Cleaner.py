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
        results = d.search(query, type=search_type)
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

class FileDisplay:
    def __init__(self, screen, filename, artist, title):
        self.screen = screen
        self.filename = filename
        self.artist = artist
        self.title = title
        self.font_header = pygame.font.Font(None, 32)
        self.font_label = pygame.font.Font(None, 28)
        self.font_data = pygame.font.Font(None, 26)
        self.font_id3_data = pygame.font.Font(None, 20)
        
        button_y_start = 620
        self.next_discogs_file_button = Button(screen.get_width() / 2 - 110, button_y_start, 220, 32, "Next Discogs File")
        self.next_music_file_button = Button(screen.get_width() / 2 - 110, button_y_start + 50, 220, 32, "Next Music File")
        self.focusable_widgets = [self.next_discogs_file_button, self.next_music_file_button]
        self.focused_index = 0
        self.focusable_widgets[self.focused_index].focused = True

        self.discogs_artist = "N/A"
        self.discogs_title = "N/A"
        self.year = "N/A"
        self.genres = []
        self.song_length = "N/A"
        self.full_release = None
        self.artist_match = False
        self.title_match = False
        self.artist_case_mismatch = False
        self.title_case_mismatch = False
        self.label_image_surface = None
        self.discogs_results = []
        self.discogs_result_index = 0
        self.is_fetching_discogs_data = False
        self.thumb_rect = pygame.Rect(450, 100, 200, 200)
        self.mutagen_thumb_rect = pygame.Rect(950, 100, 150, 150)

        self.mutagen_tags = {}
        self.mutagen_image_surface = None
        try:
            audio = mutagen.File(os.path.join('music', self.filename))
            if audio is None:
                raise ValueError("Could not load audio file with Mutagen.")

            # Time/Duration from info attribute
            self.mutagen_tags['time'] = str(datetime.timedelta(seconds=int(audio.info.length)))

            # Helper to safely get text from a tag
            def get_tag_text(tag_key, default_text='N/A'):
                if tag_key in audio:
                    tag = audio[tag_key]
                    if hasattr(tag, 'text') and tag.text:
                        return tag.text[0]
                return default_text

            # Text-based tags using standard ID3 keys
            self.mutagen_tags['artist'] = get_tag_text('TPE1')
            self.mutagen_tags['title'] = get_tag_text('TIT2')
            self.mutagen_tags['album'] = get_tag_text('TALB')
            self.mutagen_tags['genre'] = get_tag_text('TCON')
            self.mutagen_tags['year'] = get_tag_text('TDRC')
            
            # Comment needs to check multiple keys
            self.mutagen_tags['comment'] = get_tag_text('COMM::eng')
            if self.mutagen_tags['comment'] == 'N/A':
                self.mutagen_tags['comment'] = get_tag_text('COMM')


            # Image data - search for any APIC tag
            for key in audio.keys():
                if key.startswith('APIC'):
                    image_data = audio[key].data
                    image_file = io.BytesIO(image_data)
                    self.mutagen_image_surface = pygame.image.load(image_file)
                    break # Use the first one found

        except Exception as e:
            print(f"Error reading mutagen data for {self.filename}: {e}")
            self.mutagen_tags = {k: 'Error' for k in ['artist', 'title', 'album', 'genre', 'comment', 'time']}
            self.mutagen_image_surface = None
        
        self._fetch_discogs_data()

    def _clean_string(self, text):
        cleaned_text = text.replace("'", "").replace(",", "")
        if cleaned_text.lower().startswith("the "):
            cleaned_text = cleaned_text[4:]
        return cleaned_text

    def _fetch_discogs_data(self):
        search_query = f"{self.artist} - {self.title}"
        self.discogs_results = search_discogs(search_query)
        self.discogs_result_index = 0
        self._update_with_current_discogs_result()

    def _update_with_current_discogs_result(self):
        # Reset fields before populating
        self.discogs_artist = "N/A"
        self.discogs_title = "N/A"
        self.year = "N/A"
        self.genres = []
        self.song_length = "N/A"
        self.full_release = None
        self.artist_match = False
        self.title_match = False
        self.artist_case_mismatch = False
        self.title_case_mismatch = False
        self.label_image_surface = None

        if self.discogs_results and self.discogs_result_index < len(self.discogs_results):
            current_result = self.discogs_results[self.discogs_result_index]
            self.full_release = d.release(current_result.id)
            if self.full_release.artists:
                self.discogs_artist = self.full_release.artists[0].name
            self.discogs_title = self.full_release.title
            self.year = getattr(self.full_release, 'year', 'N/A')
            self.song_length, self.genres = self._get_song_length_and_genres()

            cleaned_artist_filename = self._clean_string(self.artist)
            cleaned_artist_discogs = self._clean_string(self.discogs_artist)
            cleaned_title_filename = self._clean_string(self.title)
            cleaned_title_discogs = self._clean_string(self.discogs_title)

            self.artist_match = cleaned_artist_filename.lower() == cleaned_artist_discogs.lower()
            self.title_match = cleaned_title_filename.lower() == cleaned_title_discogs.lower()

            if self.artist_match and cleaned_artist_filename != cleaned_artist_discogs:
                self.artist_case_mismatch = True

            if self.title_match and cleaned_title_filename != cleaned_title_discogs:
                self.title_case_mismatch = True

            # Fetch release image (which should be the label for a 45rpm)
            if self.full_release.images:
                image_url = self.full_release.images[0]['uri']
                try:
                    headers = {'User-Agent': 'YourApp/1.0'}
                    response = requests.get(image_url, headers=headers)
                    response.raise_for_status()
                    image_data = response.content
                    image_file = io.BytesIO(image_data)
                    self.label_image_surface = pygame.image.load(image_file)
                except Exception as e:
                    print(f"Error loading release image: {e}")

    def _display_searching_state(self):
        self.is_fetching_discogs_data = True
        self.screen.fill((30, 30, 30))
        self.draw(self.screen) # Calls draw, which will render "Searching..."
        pygame.display.flip()

    def _get_song_length_and_genres(self):
        total_duration_seconds = 0
        genres = []

        if hasattr(self.full_release, 'tracklist') and self.full_release.tracklist:
            for track in self.full_release.tracklist:
                if track.duration:
                    try:
                        minutes, seconds = map(int, track.duration.split(':'))
                        total_duration_seconds += (minutes * 60) + seconds
                    except ValueError:
                        pass
        
        if hasattr(self.full_release, 'genres') and self.full_release.genres:
            genres = self.full_release.genres

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
                    if self.discogs_results:
                        self.discogs_result_index = (self.discogs_result_index + 1) % len(self.discogs_results)
                        self._display_searching_state()
                        self._update_with_current_discogs_result()
                        self.is_fetching_discogs_data = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.thumb_rect.collidepoint(event.pos) and self.label_image_surface:
                return "view_full_screen_image", self.label_image_surface
            if self.mutagen_thumb_rect.collidepoint(event.pos) and self.mutagen_image_surface:
                return "view_full_screen_image", self.mutagen_image_surface
            if self.next_music_file_button.rect.collidepoint(event.pos):
                return "continue", None
            if self.next_discogs_file_button.rect.collidepoint(event.pos):
                if self.discogs_results:
                    self.discogs_result_index = (self.discogs_result_index + 1) % len(self.discogs_results)
                    self._display_searching_state()
                    self._update_with_current_discogs_result()
                    self.is_fetching_discogs_data = False
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

        # Filename
        label_surf = self.font_id3_data.render("Filename:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        filename_surf = self.font_id3_data.render(self.filename, True, (255, 255, 255))
        screen.blit(filename_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25

        # Artist
        label_surf = self.font_id3_data.render("Artist:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        artist_surf = self.font_id3_data.render(self.artist, True, (255, 255, 255))
        screen.blit(artist_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25

        # Title
        label_surf = self.font_id3_data.render("Title:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        title_surf = self.font_id3_data.render(self.title, True, (255, 255, 255))
        screen.blit(title_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25

    def _draw_discogs_info_column(self, screen):
        # Column 2: Discogs Data
        # Thumbnail
        if self.is_fetching_discogs_data:
            pygame.draw.rect(screen, (50, 50, 50), self.thumb_rect)
            text_surf = self.font_label.render("Searching...", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.thumb_rect.center)
            screen.blit(text_surf, text_rect)
        elif self.label_image_surface:
            screen.blit(pygame.transform.scale(self.label_image_surface, (self.thumb_rect.width, self.thumb_rect.height)), (self.thumb_rect.x, self.thumb_rect.y))
        else:
            pygame.draw.rect(screen, (50, 50, 50), self.thumb_rect)
            text_surf = self.font_label.render("No Label Image", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.thumb_rect.center)
            screen.blit(text_surf, text_rect)

        # Details below thumbnail
        y_offset = 320
        x_pos = 475 # Starting x-position for text

        # Result Counter
        if self.discogs_results:
            result_count_text = f"Result: {self.discogs_result_index + 1} of {len(self.discogs_results)}"
            result_count_surf = self.font_id3_data.render(result_count_text, True, (200, 200, 200))
            screen.blit(result_count_surf, (x_pos, y_offset))
            y_offset += 25
        
        # Artist
        label_surf = self.font_id3_data.render("Discogs Artist:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        self._draw_match_indicator(x_pos - 25, y_offset + 5, self.artist_match, self.artist_case_mismatch) # Adjust indicator x
        artist_surf = self.font_id3_data.render(self.discogs_artist, True, (255, 255, 255))
        screen.blit(artist_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25
        
        # Title
        label_surf = self.font_id3_data.render("Discogs Title:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        self._draw_match_indicator(x_pos - 25, y_offset + 5, self.title_match, self.title_case_mismatch) # Adjust indicator x
        title_surf = self.font_id3_data.render(self.discogs_title, True, (255, 255, 255))
        screen.blit(title_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25

        # Year
        label_surf = self.font_id3_data.render("Year:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        year_surf = self.font_id3_data.render(self.year, True, (255, 255, 255))
        screen.blit(year_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25
        
        # Genre
        label_surf = self.font_id3_data.render("Genre:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        genres_text = ", ".join(self.genres) if self.genres else "N/A"
        genre_surf = self.font_id3_data.render(genres_text, True, (255, 255, 255))
        screen.blit(genre_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25

        # Length
        label_surf = self.font_id3_data.render("Length:", True, (200, 200, 200))
        screen.blit(label_surf, (x_pos, y_offset))
        length_surf = self.font_id3_data.render(self.song_length, True, (255, 255, 255))
        screen.blit(length_surf, (x_pos + label_surf.get_width() + 10, y_offset))
        y_offset += 25 # Final increment for the last item

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
            ("Time:", 'time'),
            ("Year:", 'year'),
            ("Comment:", 'comment'),
        ]

        for label, key in tags_to_draw:
            label_surf = self.font_id3_data.render(label, True, (200, 200, 200))
            screen.blit(label_surf, (x_pos, y_offset))

            tag_text = str(self.mutagen_tags.get(key, 'N/A')) # Ensure text is string
            if len(tag_text) > 30: # Truncate long text, adjusted for smaller font and side-by-side
                tag_text = tag_text[:27] + '...'
            
            data_surf = self.font_id3_data.render(tag_text, True, (255, 255, 255))
            # Place data next to the label, with a small gap
            screen.blit(data_surf, (x_pos + label_surf.get_width() + 10, y_offset))
            y_offset += 25 # Smaller increment for each line

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
    def __init__(self, screen, image_surface):
        self.screen = screen
        self.image_surface = image_surface
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
                    return "show_result", processed_image
                elif focused_widget == self.debug_button:
                    processed_image = extract_label(self.image_surface, debug=True)
                    return "show_result", processed_image

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back_to_file_display", None
            if self.create_label_button.rect.collidepoint(event.pos):
                processed_image = extract_label(self.image_surface)
                return "show_result", processed_image
            if self.debug_button.rect.collidepoint(event.pos):
                processed_image = extract_label(self.image_surface, debug=True)
                return "show_result", processed_image
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
    def __init__(self, screen, image_surface):
        self.screen = screen
        self.image_surface = image_surface
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.back_button.focused = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.back_button.rect.collidepoint(event.pos):
            return "back_to_full_screen"
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
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



def main():
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Music File Cleaner")

    music_files = os.listdir('music')
    if not music_files:
        print("No music files found in the 'music' directory.")
        return

    current_file_index = 0

    artist_box = InputBox(100, 100, 140, 32, 'Artist')
    title_box = InputBox(100, 200, 140, 32, 'Title')
    search_button = Button(100, 300, 140, 32, 'Search')
    
    focusable_widgets_input = [artist_box, title_box, search_button]
    focused_widget_index_input = 0
    focusable_widgets_input[focused_widget_index_input].focused = True

    results_viewer = None
    details_viewer = None
    file_display = None
    full_screen_viewer = None
    result_viewer = None
    app_state = "file_display"
    search_query = ""
    current_page = 1

    done = False
    while not done:
        if app_state == "file_display" and file_display is None:
            current_file = music_files[current_file_index]
            try:
                artist, title = current_file.replace('.mp3', '').rsplit(' - ', 1)
            except ValueError:
                artist, title = "Unknown Artist", current_file.replace('.mp3', '')
            file_display = FileDisplay(screen, current_file, artist, title)

            if not file_display.discogs_results:
                print(f"No Discogs results for {current_file}, skipping.")
                current_file_index = (current_file_index + 1) % len(music_files)
                file_display = None
                continue

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if app_state == "full_screen_image":
                        app_state = "file_display"
                        full_screen_viewer = None
                    elif app_state == "result_display":
                        app_state = "full_screen_image"
                        result_viewer = None
                    else:
                        done = True

            if app_state == "file_display":
                action, data = file_display.handle_event(event)
                if action:
                    if action == "continue":
                        current_file_index = (current_file_index + 1) % len(music_files)
                        file_display = None
                    elif action == "view_full_screen_image":
                        full_screen_viewer = FullScreenImageViewer(screen, data)
                        app_state = "full_screen_image"
            
            elif app_state == "input":
                # ... (existing input state logic is correct)
                pass # This block is unchanged but shown for context
            
            elif app_state == "results":
                # ... (existing results state logic is correct)
                pass # This block is unchanged but shown for context

            elif app_state == "details":
                # ... (existing details state logic is correct)
                pass # This block is unchanged but shown for context
            
            elif app_state == "full_screen_image":
                if full_screen_viewer:
                    action, data = full_screen_viewer.handle_event(event)
                    if action == "back_to_file_display":
                        app_state = "file_display"
                        full_screen_viewer = None
                    elif action == "show_result":
                        result_viewer = ResultViewer(screen, data)
                        app_state = "result_display"
            
            elif app_state == "result_display":
                if result_viewer:
                    action = result_viewer.handle_event(event)
                    if action == "back_to_full_screen":
                        app_state = "full_screen_image"
                        result_viewer = None


        screen.fill((30, 30, 30))

        if app_state == "file_display":
            if file_display:
                file_display.draw(screen)

        elif app_state == "input":
            for widget in focusable_widgets_input:
                widget.draw(screen)
        
        elif app_state == "searching" or app_state == "searching_next_page":
            searching_text = FONT.render("Searching...", True, (255, 255, 255))
            text_rect = searching_text.get_rect(center=screen.get_rect().center)
            screen.blit(searching_text, text_rect)
            pygame.display.flip() 
            
            if app_state == "searching_next_page":
                current_page += 1
            
            results = search_discogs(search_query, page=current_page)
            results_viewer = ResultsViewer(screen, results)
            app_state = "results"

        elif app_state == "results":
            if results_viewer:
                results_viewer.draw()

        elif app_state == "details":
            if details_viewer:
                details_viewer.draw()

        elif app_state == "full_screen_image":
            if full_screen_viewer:
                full_screen_viewer.draw()
        
        elif app_state == "result_display":
            if result_viewer:
                result_viewer.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
