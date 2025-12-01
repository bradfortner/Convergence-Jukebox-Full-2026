import pygame
import discogs_client
import config
import json

# Initialize Discogs client
# The user token is now imported from config.py
d = discogs_client.Client('YourApp/1.0', user_token=config.DISCOGS_USER_TOKEN)

def search_discogs(query, search_type='release'):
    """
    Searches the Discogs database for releases, artists, or masters.
    """
    print(f"\nSearching Discogs for '{query}' (type: {search_type})...")
    try:
        results = d.search(query, type=search_type)
        if results:
            print(f"Found {results.count} results. Filtering for 45rpm releases. Showing up to 20 matches:")
            found_count = 0
            for result in results.page(1):
                if found_count >= 20: # Limit to first 20 results
                    break
                if isinstance(result, discogs_client.models.Release):
                    # Check for 45rpm format
                    is_45rpm = False
                    if result.formats:
                        for format in result.formats:
                            if format.get('name') == 'Vinyl' and '7"' in format.get('descriptions', []) and '45 RPM' in format.get('descriptions', []):
                                is_45rpm = True
                                break
                    
                    if is_45rpm:
                        found_count += 1
                        print(f"\n--- Found 45rpm release ---")
                        print(f"    Title: {result.title}")
                        print(f"    Artist: {result.artists[0].name if result.artists else 'N/A'}")
                        print(f"    Year: {result.year}")
                        print(f"    Labels: {', '.join([l.name for l in result.labels])}")
                        if result.images:
                            print("    Images:")
                            for image in result.images:
                                print(f"      - {image.get('uri')}")
                        else:
                            print("    No images found for this release.")

            if found_count == 0:
                print("No 45rpm releases found in the first page of results.")
        else:
            print(f"  No {search_type} results found for '{query}'.")
    except json.JSONDecodeError:
        print("\nError: Could not decode the response from Discogs.")
        print("This might be due to an invalid API token, rate limiting, or network issues.")
        print("Please check your API token in config.py and your internet connection.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.placeholder_text = text # Store original placeholder
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                was_active = self.active
                self.active = not self.active
                if self.active and self.text == self.placeholder_text:
                    self.text = '' # Clear placeholder on activation
            else:
                if not self.text:
                    self.text = self.placeholder_text # Restore placeholder if empty
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            self.txt_surface = FONT.render(self.text, True, (255, 255, 255) if self.active or self.text != self.placeholder_text else self.color)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    # Don't clear text on enter unless specified, let user keep it
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = FONT.render(self.text, True, (255, 255, 255))

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


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

    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
            for box in input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if search_button.collidepoint(event.pos):
                    search_query = f"{artist_box.text} - {title_box.text}"
                    search_discogs(search_query)


        screen.fill((30, 30, 30))
        for box in input_boxes:
            box.draw(screen)

        pygame.draw.rect(screen, COLOR_INACTIVE, search_button)
        search_text = FONT.render("Search", True, (255, 255, 255))
        screen.blit(search_text, (search_button.x + 30, search_button.y + 5))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
