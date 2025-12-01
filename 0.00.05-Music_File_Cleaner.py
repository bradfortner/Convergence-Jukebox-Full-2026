import pygame
import discogs_client
import jukebox_config
import json
import requests
import io
import datetime # Import datetime for time calculations
import os

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
        self.font = pygame.font.Font(None, 32)
        self.continue_button = Button(screen.get_width() // 2 - 70, 500, 140, 32, "Continue")
        self.focusable_widgets = [self.continue_button]
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

        self._fetch_discogs_data()

    def _clean_string(self, text):
        cleaned_text = text.lower().replace("'", "").replace(",", "")
        if cleaned_text.startswith("the "):
            cleaned_text = cleaned_text[4:]
        return cleaned_text

    def _fetch_discogs_data(self):
        search_query = f"{self.artist} - {self.title}"
        results = search_discogs(search_query)
        if results:
            first_result = results[0]
            self.full_release = d.release(first_result.id)
            if self.full_release.artists:
                self.discogs_artist = self.full_release.artists[0].name
            self.discogs_title = self.full_release.title
            self.year = getattr(self.full_release, 'year', 'N/A')
            self.song_length, self.genres = self._get_song_length_and_genres()

            cleaned_artist_filename = self._clean_string(self.artist)
            cleaned_artist_discogs = self._clean_string(self.discogs_artist)
            cleaned_title_filename = self._clean_string(self.title)
            cleaned_title_discogs = self._clean_string(self.discogs_title)

            self.artist_match = cleaned_artist_filename == cleaned_artist_discogs
            self.title_match = cleaned_title_filename == cleaned_title_discogs

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

    def _draw_match_indicator(self, x, y, is_match):
        box_rect = pygame.Rect(x, y, 20, 20)
        if is_match:
            pygame.draw.rect(self.screen, (0, 255, 0), box_rect)
            pygame.draw.line(self.screen, (0, 0, 0), (x + 5, y + 10), (x + 8, y + 13), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x + 8, y + 13), (x + 15, y + 6), 2)
        else:
            pygame.draw.rect(self.screen, (255, 0, 0), box_rect)
            pygame.draw.line(self.screen, (0, 0, 0), (x + 5, y + 5), (x + 15, y + 15), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x + 5, y + 15), (x + 15, y + 5), 2)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focusable_widgets[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.focusable_widgets)
                self.focusable_widgets[self.focused_index].focused = True
            elif event.key == pygame.K_RETURN:
                if self.focusable_widgets[self.focused_index] == self.continue_button:
                    return "continue"
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_button.rect.collidepoint(event.pos):
                return "continue"
        return None

    def draw(self, screen):
        filename_surface = self.font.render(f"Filename: {self.filename}", True, (255, 255, 255))
        artist_surface = self.font.render(f"Artist: {self.artist}", True, (255, 255, 255))
        title_surface = self.font.render(f"Title: {self.title}", True, (255, 255, 255))
        
        screen.blit(filename_surface, (100, 100))
        screen.blit(artist_surface, (100, 150))
        screen.blit(title_surface, (100, 200))

        discogs_artist_surface = self.font.render(f"Discogs Artist: {self.discogs_artist}", True, (255, 255, 255))
        discogs_title_surface = self.font.render(f"Discogs Title: {self.discogs_title}", True, (255, 255, 255))
        screen.blit(discogs_artist_surface, (600, 150))
        screen.blit(discogs_title_surface, (600, 200))
        
        self._draw_match_indicator(560, 155, self.artist_match)
        self._draw_match_indicator(560, 205, self.title_match)

        genres_text = ", ".join(self.genres) if self.genres else "N/A"
        year_surface = self.font.render(f"Year: {self.year}", True, (255, 255, 255))
        length_surface = self.font.render(f"Length: {self.song_length}", True, (255, 255, 255))
        genre_surface = self.font.render(f"Genre: {genres_text}", True, (255, 255, 255))
        
        screen.blit(year_surface, (100, 250))
        screen.blit(length_surface, (100, 300))
        screen.blit(genre_surface, (100, 350))

        self.continue_button.draw(screen)

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

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

            if app_state == "file_display":
                action = file_display.handle_event(event)
                if action == "continue":
                    current_file_index = (current_file_index + 1) % len(music_files)
                    file_display = None  # Force re-creation
            
            elif app_state == "input":
                focused_widget = focusable_widgets_input[focused_widget_index_input]
                
                for widget in focusable_widgets_input:
                    widget.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        focused_widget.focused = False
                        focused_widget_index_input = (focused_widget_index_input + 1) % len(focusable_widgets_input)
                        focusable_widgets_input[focused_widget_index_input].focused = True
                    elif event.key == pygame.K_RETURN:
                        if focused_widget == search_button:
                            current_page = 1
                            search_query = f"{artist_box.text} - {title_box.text}"
                            app_state = "searching"
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, widget in enumerate(focusable_widgets_input):
                        if widget.rect.collidepoint(event.pos):
                            focusable_widgets_input[focused_widget_index_input].focused = False
                            focused_widget_index_input = i
                            widget.focused = True
                            if widget == search_button:
                                current_page = 1
                                search_query = f"{artist_box.text} - {title_box.text}"
                                app_state = "searching"
            
            elif app_state == "results":
                if results_viewer:
                    action, data = results_viewer.handle_event(event)
                    if action == "back":
                        app_state = "input"
                    elif action == "view_details":
                        details_viewer = DetailsViewer(screen, data)
                        app_state = "details"
                    elif action == "next_page":
                        app_state = "searching_next_page"

            elif app_state == "details":
                if details_viewer:
                    action = details_viewer.handle_event(event)
                    if action == "back_to_results":
                        app_state = "results"

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

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()