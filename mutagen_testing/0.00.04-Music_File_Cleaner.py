import pygame
import discogs_client
import config
import json
import requests
import io

# Initialize Discogs client
d = discogs_client.Client('YourApp/1.0', user_token=config.DISCOGS_USER_TOKEN)

def search_discogs(query, search_type='release'):
    """
    Searches the Discogs database for releases and returns a list of 45rpm releases.
    """
    print(f"\nSearching Discogs for '{query}' (type: {search_type})...")
    release_list = []
    try:
        results = d.search(query, type=search_type)
        if results:
            print(f"Found {results.count} results. Filtering for 45rpm releases.")
            for result in results.page(1):
                if len(release_list) >= 20:
                    break
                if isinstance(result, discogs_client.models.Release):
                    is_45rpm = any(
                        format_entry.get('name') == 'Vinyl' and '7"' in format_entry.get('descriptions', []) and '45 RPM' in format_entry.get('descriptions', [])
                        for format_entry in result.formats or []
                    )
                    if is_45rpm:
                        release_list.append(result)

            if not release_list:
                print("No 45rpm releases found in the first page of results.")
        else:
            print(f"  No {search_type} results found for '{query}'.")
    except Exception as e:
        print(f"An unexpected error occurred during search: {e}")
    return release_list

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.placeholder_text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                if self.active and self.text == self.placeholder_text:
                    self.text = ''
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return "search"
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        self.txt_surface = FONT.render(self.text, True, (255,255,255))
        return None

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

class ResultsViewer:
    def __init__(self, screen, results):
        self.screen = screen
        self.results = results
        self.current_result_index = 0
        self.image_surface = None
        self.font = pygame.font.Font(None, 24)
        self.back_button = pygame.Rect(10, 10, 100, 32)
        self.load_current_result()

    def load_current_result(self):
        self.image_surface = None
        if not self.results:
            return
            
        result = self.results[self.current_result_index]
        if result.images:
            image_url = result.images[0]['uri']
            try:
                headers = {'User-Agent': 'YourApp/1.0'}
                response = requests.get(image_url, headers=headers)
                response.raise_for_status()
                image_data = response.content
                image_file = io.BytesIO(image_data)
                self.image_surface = pygame.image.load(image_file)
            except Exception as e:
                print(f"Error loading image: {e}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_UP):
                if self.results: self.current_result_index = (self.current_result_index + 1) % len(self.results)
                self.load_current_result()
            elif event.key in (pygame.K_LEFT, pygame.K_DOWN):
                if self.results: self.current_result_index = (self.current_result_index - 1) % len(self.results)
                self.load_current_result()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.collidepoint(event.pos):
                return "back"
        return None

    def draw(self):
        if not self.results:
            text_surface = self.font.render("No results found.", True, (255, 255, 255))
            self.screen.blit(text_surface, (50, 50))
        else:
            result = self.results[self.current_result_index]
            
            if self.image_surface:
                self.screen.blit(pygame.transform.scale(self.image_surface, (300, 300)), (50, 50))
            else:
                pygame.draw.rect(self.screen, (50,50,50), (50, 50, 300, 300))
                error_text = self.font.render("Image not available", True, (255,255,255))
                self.screen.blit(error_text, (100, 200))

            title_surface = self.font.render(f"Title: {result.title}", True, (255, 255, 255))
            artist_surface = self.font.render(f"Artist: {result.artists[0].name if result.artists else 'N/A'}", True, (255, 255, 255))
            year_surface = self.font.render(f"Year: {result.year if result.year else 'N/A'}", True, (255, 255, 255))
            self.screen.blit(title_surface, (370, 50))
            self.screen.blit(artist_surface, (370, 80))
            self.screen.blit(year_surface, (370, 110))
            
            page_text = self.font.render(f"Result {self.current_result_index + 1} of {len(self.results)}", True, (255, 255, 255))
            self.screen.blit(page_text, (50, 400))

        pygame.draw.rect(self.screen, COLOR_INACTIVE, self.back_button)
        back_text = FONT.render("Back", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button.x + 30, self.back_button.y + 5))

def main():
    global FONT, COLOR_INACTIVE, COLOR_ACTIVE
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    FONT = pygame.font.Font(None, 32)
    COLOR_INACTIVE = pygame.Color('lightskyblue3')
    COLOR_ACTIVE = pygame.Color('dodgerblue2')
    pygame.display.set_caption("Music File Cleaner")

    artist_box = InputBox(100, 100, 140, 32, 'Artist')
    title_box = InputBox(100, 200, 140, 32, 'Title')
    input_boxes = [artist_box, title_box]
    search_button = pygame.Rect(100, 300, 140, 32)
    
    results_viewer = None
    app_state = "input"

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
            
            if app_state == "input":
                for box in input_boxes:
                    box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if search_button.collidepoint(event.pos):
                        search_query = f"{artist_box.text} - {title_box.text}"
                        results = search_discogs(search_query)
                        results_viewer = ResultsViewer(screen, results)
                        app_state = "results"
            elif app_state == "results":
                if results_viewer:
                    action = results_viewer.handle_event(event)
                    if action == "back":
                        app_state = "input"

        screen.fill((30, 30, 30))

        if app_state == "input":
            for box in input_boxes:
                box.draw(screen)
            pygame.draw.rect(screen, COLOR_INACTIVE, search_button)
            search_text = FONT.render("Search", True, (255, 255, 255))
            screen.blit(search_text, (search_button.x + 30, search_button.y + 5))
        elif app_state == "results":
            if results_viewer:
                results_viewer.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
