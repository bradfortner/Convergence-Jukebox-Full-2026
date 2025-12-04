"""
Mutagen Testing Program
Version 0.00.05
Tests the mutagen library for reading audio file metadata and extracting/displaying artwork
Uses pygame to display artwork and metadata side-by-side
Allows updating artwork by selecting an image and embedding it at 1000x1000
"""

import os
import pygame
from mutagen import File
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TDRC
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from PIL import Image
from tkinter import Tk, filedialog


# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Default music directory (parent directory + "music")
MUSIC_DIRECTORY = os.path.join(os.path.dirname(SCRIPT_DIR), "music")

# Directory for saving extracted artwork (same directory as script + "mutagen_images")
ARTWORK_DIRECTORY = os.path.join(SCRIPT_DIR, "mutagen_images")

# Pygame display settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (100, 200, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)


def extract_artwork(audio, file_path, file_index):
    """
    Extract and save album artwork from audio file
    Returns the filename if artwork was found, None otherwise
    """
    artwork_filename = None
    image_data = None

    # Create artwork directory if it doesn't exist
    if not os.path.exists(ARTWORK_DIRECTORY):
        os.makedirs(ARTWORK_DIRECTORY)
        print(f"Created directory: {ARTWORK_DIRECTORY}")

    try:
        # For MP3 files with ID3 tags
        if hasattr(audio, 'tags') and audio.tags:
            # Check for APIC (Attached Picture) frames
            for key in audio.tags.keys():
                if key.startswith('APIC'):
                    apic = audio.tags[key]
                    image_data = apic.data
                    mime_type = apic.mime

                    # Determine file extension from MIME type
                    ext = 'jpg'
                    if 'png' in mime_type.lower():
                        ext = 'png'
                    elif 'jpeg' in mime_type.lower() or 'jpg' in mime_type.lower():
                        ext = 'jpg'
                    elif 'gif' in mime_type.lower():
                        ext = 'gif'

                    # Save artwork to file in mutagen_images directory
                    artwork_filename = os.path.join(ARTWORK_DIRECTORY, f"artwork_{file_index}.{ext}")
                    with open(artwork_filename, 'wb') as img_file:
                        img_file.write(image_data)

                    print(f"Extracted artwork: {artwork_filename}")
                    break

            # For FLAC files
            if not artwork_filename and hasattr(audio, 'pictures') and audio.pictures:
                picture = audio.pictures[0]
                image_data = picture.data
                mime_type = picture.mime

                ext = 'jpg'
                if 'png' in mime_type.lower():
                    ext = 'png'

                artwork_filename = os.path.join(ARTWORK_DIRECTORY, f"artwork_{file_index}.{ext}")
                with open(artwork_filename, 'wb') as img_file:
                    img_file.write(image_data)

                print(f"Extracted artwork: {artwork_filename}")

            # For MP4/M4A files
            if not artwork_filename and 'covr' in audio.tags:
                cover = audio.tags['covr'][0]
                image_data = bytes(cover)

                # MP4 covers are usually JPEG or PNG
                ext = 'jpg'
                if image_data[:4] == b'\x89PNG':
                    ext = 'png'

                artwork_filename = os.path.join(ARTWORK_DIRECTORY, f"artwork_{file_index}.{ext}")
                with open(artwork_filename, 'wb') as img_file:
                    img_file.write(image_data)

                print(f"Extracted artwork: {artwork_filename}")

    except Exception as e:
        print(f"Error extracting artwork: {e}")

    return artwork_filename


def resize_image_to_1000x1000(input_path, output_path):
    """
    Resize an image to 1000x1000 and save it
    """
    try:
        img = Image.open(input_path)
        img_resized = img.resize((1000, 1000), Image.LANCZOS)
        img_resized.save(output_path, quality=90)
        print(f"Resized image saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False


def embed_artwork_in_file(audio_file_path, image_path):
    """
    Embed artwork into an audio file at 1000x1000 resolution
    """
    try:
        # Create temp resized image
        temp_resized = os.path.join(ARTWORK_DIRECTORY, "temp_resized_1000x1000.jpg")
        if not resize_image_to_1000x1000(image_path, temp_resized):
            return False

        # Read the resized image data
        with open(temp_resized, 'rb') as img_file:
            image_data = img_file.read()

        # Determine file type and embed artwork
        file_ext = os.path.splitext(audio_file_path)[1].lower()

        if file_ext == '.mp3':
            # MP3 file - use ID3 tags
            try:
                audio = MP3(audio_file_path, ID3=ID3)
            except:
                # If no ID3 tag exists, add one
                audio = MP3(audio_file_path)
                audio.add_tags()

            # Remove existing artwork
            audio.tags.delall('APIC')

            # Add new artwork
            audio.tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime='image/jpeg',
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=image_data
                )
            )
            audio.save()
            print(f"✓ Artwork embedded in MP3: {audio_file_path}")

        elif file_ext == '.flac':
            # FLAC file
            audio = FLAC(audio_file_path)
            audio.clear_pictures()

            picture = Picture()
            picture.data = image_data
            picture.type = 3  # Cover (front)
            picture.mime = 'image/jpeg'
            picture.width = 1000
            picture.height = 1000

            audio.add_picture(picture)
            audio.save()
            print(f"✓ Artwork embedded in FLAC: {audio_file_path}")

        elif file_ext in ['.m4a', '.mp4']:
            # MP4/M4A file
            audio = MP4(audio_file_path)
            audio.tags['covr'] = [MP4Cover(image_data, imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()
            print(f"✓ Artwork embedded in MP4/M4A: {audio_file_path}")

        else:
            print(f"✗ Unsupported file format: {file_ext}")
            return False

        # Clean up temp file
        if os.path.exists(temp_resized):
            os.remove(temp_resized)

        return True

    except Exception as e:
        print(f"Error embedding artwork: {e}")
        import traceback
        traceback.print_exc()
        return False


def select_image_file():
    """
    Open file dialog to select an image from mutagen_images directory
    """
    root = Tk()
    root.withdraw()  # Hide the main tkinter window
    root.attributes('-topmost', True)  # Bring dialog to front

    file_path = filedialog.askopenfilename(
        initialdir=ARTWORK_DIRECTORY,
        title="Select Album Artwork",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
    )

    root.destroy()
    return file_path if file_path else None


def get_audio_metadata(file_path):
    """
    Extracts common metadata from various audio file types.
    Returns a dictionary with normalized keys.
    """
    metadata = {
        'title': 'Unknown',
        'artist': 'Unknown',
        'album': 'Unknown',
        'genre': 'Unknown',
        'year': 'Unknown',
        'length': 'Unknown',
        'bitrate': 'Unknown',
        'sample_rate': 'Unknown'
    }

    try:
        audio = File(file_path)

        if audio is None:
            return metadata

        # General metadata extraction for MP3/ID3
        if isinstance(audio, (MP3, ID3)):
            if audio.tags:
                metadata['title'] = str(audio.tags.get('TIT2', ['Unknown'])[0]) if audio.tags.get('TIT2') else 'Unknown'
                metadata['artist'] = str(audio.tags.get('TPE1', ['Unknown'])[0]) if audio.tags.get('TPE1') else 'Unknown'
                metadata['album'] = str(audio.tags.get('TALB', ['Unknown'])[0]) if audio.tags.get('TALB') else 'Unknown'
                metadata['genre'] = str(audio.tags.get('TCON', ['Unknown'])[0]) if audio.tags.get('TCON') else 'Unknown'
                metadata['year'] = str(audio.tags.get('TDRC', ['Unknown'])[0]) if audio.tags.get('TDRC') else 'Unknown'
        
        # General metadata extraction for FLAC
        elif isinstance(audio, FLAC):
            if audio.tags:
                metadata['title'] = str(audio.tags.get('title', ['Unknown'])[0]) if audio.tags.get('title') else 'Unknown'
                metadata['artist'] = str(audio.tags.get('artist', ['Unknown'])[0]) if audio.tags.get('artist') else 'Unknown'
                metadata['album'] = str(audio.tags.get('album', ['Unknown'])[0]) if audio.tags.get('album') else 'Unknown'
                metadata['genre'] = str(audio.tags.get('genre', ['Unknown'])[0]) if audio.tags.get('genre') else 'Unknown'
                metadata['year'] = str(audio.tags.get('date', ['Unknown'])[0]) if audio.tags.get('date') else 'Unknown'
        
        # General metadata extraction for MP4/M4A
        elif isinstance(audio, MP4):
            if audio.tags:
                metadata['title'] = str(audio.tags.get('\xa9nam', ['Unknown'])[0]) if audio.tags.get('\xa9nam') else 'Unknown'
                metadata['artist'] = str(audio.tags.get('\xa9ART', ['Unknown'])[0]) if audio.tags.get('\xa9ART') else 'Unknown'
                metadata['album'] = str(audio.tags.get('\xa9alb', ['Unknown'])[0]) if audio.tags.get('\xa9alb') else 'Unknown'
                metadata['genre'] = str(audio.tags.get('\xa9gen', ['Unknown'])[0]) if audio.tags.get('\xa9gen') else 'Unknown'
                metadata['year'] = str(audio.tags.get('\xa9day', ['Unknown'])[0]) if audio.tags.get('\xa9day') else 'Unknown'

        # Audio info (length, bitrate, sample rate)
        if hasattr(audio, 'info'):
            if audio.info.length:
                metadata['length'] = f"{audio.info.length:.2f} seconds ({audio.info.length/60:.2f} minutes)"
            if hasattr(audio.info, 'bitrate') and audio.info.bitrate:
                metadata['bitrate'] = f"{audio.info.bitrate/1000:.0f} kbps"
            if hasattr(audio.info, 'sample_rate') and audio.info.sample_rate:
                metadata['sample_rate'] = f"{audio.info.sample_rate} Hz"

    except Exception as e:
        print(f"Error extracting metadata from {file_path}: {e}")

    return metadata


def set_audio_metadata(file_path, metadata):
    """
    Updates metadata for various audio file types.
    """
    try:
        audio = File(file_path)

        if audio is None:
            print(f"✗ Could not open file: {file_path}")
            return False

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.mp3':
            # Add tags if they don't exist
            if not audio.tags:
                audio.add_tags()
            
            # Update MP3 tags
            if 'title' in metadata:
                audio.tags['TIT2'] = TIT2(encoding=3, text=metadata['title'])
            if 'artist' in metadata:
                audio.tags['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
            if 'album' in metadata:
                audio.tags['TALB'] = TALB(encoding=3, text=metadata['album'])
            if 'genre' in metadata:
                audio.tags['TCON'] = TCON(encoding=3, text=metadata['genre'])
            if 'year' in metadata:
                audio.tags['TDRC'] = TDRC(encoding=3, text=str(metadata['year']))

        elif file_ext == '.flac':
            # Update FLAC tags (Vorbis comments)
            if 'title' in metadata:
                audio['title'] = metadata['title']
            if 'artist' in metadata:
                audio['artist'] = metadata['artist']
            if 'album' in metadata:
                audio['album'] = metadata['album']
            if 'genre' in metadata:
                audio['genre'] = metadata['genre']
            if 'year' in metadata:
                audio['date'] = str(metadata['year'])

        elif file_ext in ['.m4a', '.mp4']:
            # Update MP4 tags
            if 'title' in metadata:
                audio.tags['\xa9nam'] = metadata['title']
            if 'artist' in metadata:
                audio.tags['\xa9ART'] = metadata['artist']
            if 'album' in metadata:
                audio.tags['\xa9alb'] = metadata['album']
            if 'genre' in metadata:
                audio.tags['\xa9gen'] = metadata['genre']
            if 'year' in metadata:
                audio.tags['\xa9day'] = str(metadata['year'])
        
        else:
            print(f"✗ Unsupported file type for metadata update: {file_ext}")
            return False
        
        audio.save()
        print(f"✓ Metadata updated for: {os.path.basename(file_path)}")
        return True

    except Exception as e:
        print(f"✗ Error updating metadata for {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_with_pygame(file_path, audio, artwork_filename, file_index):
    """
    Display artwork and metadata in a pygame window with a button to change artwork
    Returns "next" for next file, "prev" for previous file, "quit" to exit program
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mutagen Audio File Viewer")

    # Fonts
    font_title = pygame.font.SysFont('Arial', 28, bold=True)
    font_normal = pygame.font.SysFont('Arial', 20)
    font_small = pygame.font.SysFont('Arial', 16)
    font_button = pygame.font.SysFont('Arial', 18, bold=True)

    # Button definition
    button_rect = pygame.Rect(200, 650, 200, 50)

    def load_and_display():
        """Load audio data and artwork for display"""
        # Reload audio file to get latest data
        current_audio = File(file_path)

        # Re-extract artwork
        current_artwork = extract_artwork(current_audio, file_path, file_index)

        # Load and scale artwork if available
        artwork_surface = None
        if current_artwork and os.path.exists(current_artwork):
            try:
                artwork_surface = pygame.image.load(current_artwork)
                # Scale to fit (max 500x500)
                img_rect = artwork_surface.get_rect()
                max_size = 500
                if img_rect.width > max_size or img_rect.height > max_size:
                    scale_factor = min(max_size / img_rect.width, max_size / img_rect.height)
                    new_width = int(img_rect.width * scale_factor)
                    new_height = int(img_rect.height * scale_factor)
                    artwork_surface = pygame.transform.scale(artwork_surface, (new_width, new_height))
            except Exception as e:
                print(f"Error loading artwork with pygame: {e}")

        # Extract metadata
        metadata = get_audio_metadata(file_path)

        return artwork_surface, metadata

    # Initial load
    artwork_surface, metadata = load_and_display()

    # Main display loop
    running = True
    clock = pygame.time.Clock()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = button_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"  # Quit program
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return "quit"  # Quit program
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return "next"  # Continue to next file
                elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    return "prev"  # Go to previous file
                elif event.key == pygame.K_u:
                    print("\nUpdating metadata (test)...")
                    test_metadata = {
                        'title': 'Test Title',
                        'artist': 'Test Artist',
                        'album': 'Test Album',
                        'genre': 'Test Genre',
                        'year': '2025'
                    }
                    if set_audio_metadata(file_path, test_metadata):
                        print("✓ Metadata updated successfully for testing!")
                        artwork_surface, metadata = load_and_display()
                    else:
                        print("✗ Failed to update metadata for testing.")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    # Button clicked - open file dialog
                    print("\nOpening file dialog...")
                    selected_image = select_image_file()
                    if selected_image:
                        print(f"Selected image: {selected_image}")
                        print("Embedding artwork into audio file...")
                        if embed_artwork_in_file(file_path, selected_image):
                            print("✓ Artwork updated successfully!")
                            # Reload display
                            artwork_surface, metadata = load_and_display()
                        else:
                            print("✗ Failed to update artwork")
                    else:
                        print("No image selected")

        # Fill background
        screen.fill(BACKGROUND_COLOR)

        # Draw artwork on left side
        if artwork_surface:
            artwork_rect = artwork_surface.get_rect()
            artwork_rect.centerx = 300
            artwork_rect.centery = 350
            screen.blit(artwork_surface, artwork_rect)
        else:
            # Draw "No Artwork" message
            no_art_text = font_normal.render("No Artwork Available", True, (150, 150, 150))
            no_art_rect = no_art_text.get_rect(center=(300, 350))
            screen.blit(no_art_text, no_art_rect)

        # Draw "Change Artwork" button
        button_color = BUTTON_HOVER_COLOR if button_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, button_rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, button_rect, 2, border_radius=5)
        button_text = font_button.render("Change Artwork", True, TEXT_COLOR)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

        # Draw metadata on right side
        x_start = 650
        y_start = 50

        # File name at top
        filename_text = font_small.render(f"File: {os.path.basename(file_path)}", True, (180, 180, 180))
        screen.blit(filename_text, (x_start, y_start))
        y_start += 50

        # Title
        title_label = font_normal.render("Title:", True, HIGHLIGHT_COLOR)
        screen.blit(title_label, (x_start, y_start))
        title_value = font_normal.render(metadata.get('title', 'Unknown'), True, TEXT_COLOR)
        screen.blit(title_value, (x_start, y_start + 30))
        y_start += 80

        # Artist
        artist_label = font_normal.render("Artist:", True, HIGHLIGHT_COLOR)
        screen.blit(artist_label, (x_start, y_start))
        artist_value = font_normal.render(metadata.get('artist', 'Unknown'), True, TEXT_COLOR)
        screen.blit(artist_value, (x_start, y_start + 30))
        y_start += 80

        # Album
        album_label = font_normal.render("Album:", True, HIGHLIGHT_COLOR)
        screen.blit(album_label, (x_start, y_start))
        album_value = font_normal.render(metadata.get('album', 'Unknown'), True, TEXT_COLOR)
        screen.blit(album_value, (x_start, y_start + 30))
        y_start += 80

        # Genre
        genre_label = font_normal.render("Genre:", True, HIGHLIGHT_COLOR)
        screen.blit(genre_label, (x_start, y_start))
        genre_value = font_normal.render(metadata.get('genre', 'Unknown'), True, TEXT_COLOR)
        screen.blit(genre_value, (x_start, y_start + 30))
        y_start += 80

        # Year
        year_label = font_normal.render("Year:", True, HIGHLIGHT_COLOR)
        screen.blit(year_label, (x_start, y_start))
        year_value = font_normal.render(metadata.get('year', 'Unknown'), True, TEXT_COLOR)
        screen.blit(year_value, (x_start, y_start + 30))
        y_start += 80

        # Audio properties
        if 'length' in metadata:
            length_text = font_small.render(f"Length: {metadata['length']}", True, (200, 200, 200))
            screen.blit(length_text, (x_start, y_start))
            y_start += 30

        if 'bitrate' in metadata:
            bitrate_text = font_small.render(f"Bitrate: {metadata['bitrate']}", True, (200, 200, 200))
            screen.blit(bitrate_text, (x_start, y_start))
            y_start += 30

        if 'sample_rate' in metadata:
            sample_text = font_small.render(f"Sample Rate: {metadata['sample_rate']}", True, (200, 200, 200))
            screen.blit(sample_text, (x_start, y_start))
            y_start += 30

        # Instructions at bottom
        instruction_text = font_small.render("RIGHT/DOWN ARROW: Next | LEFT/UP ARROW: Previous | SPACE/ENTER: Next | ESC: Quit | Click button to change artwork", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(instruction_text, instruction_rect)

        pygame.display.flip()
        clock.tick(30)

    return "quit"


def scan_music_directory(directory, extensions=('.mp3', '.flac', '.ogg', '.m4a', '.wma')):
    """
    Scan a directory for audio files and display metadata for first 10 files
    """
    print(f"\n{'='*80}")
    print(f"Scanning directory: {directory}")
    print(f"{'='*80}")

    if not os.path.exists(directory):
        print(f"ERROR: Directory not found: {directory}")
        return

    # Find all audio files
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                audio_files.append(os.path.join(root, file))

    print(f"\nFound {len(audio_files)} audio files")
    print(f"Displaying first 10 files...\n")

    # Process first 10 files with arrow key navigation
    current_index = 0
    max_files = min(10, len(audio_files))

    while 0 <= current_index < max_files:
        i = current_index + 1  # Display number (1-based)
        file_path = audio_files[current_index]

        print(f"\n{'='*80}")
        print(f"File {i}: {os.path.basename(file_path)}")
        print(f"{'='*80}")

        try:
            audio = File(file_path)

            if audio is None:
                print("ERROR: File format not recognized")
                current_index += 1
                continue

            # Extract artwork
            artwork_filename = extract_artwork(audio, file_path, i)

            # Display in pygame window
            navigation = display_with_pygame(file_path, audio, artwork_filename, i)

            if navigation == "quit":
                print("\nExiting viewer...")
                break
            elif navigation == "next":
                current_index += 1
            elif navigation == "prev":
                current_index -= 1
                # Don't go before first file
                if current_index < 0:
                    current_index = 0

        except Exception as e:
            print(f"ERROR reading file: {e}")
            import traceback
            traceback.print_exc()
            current_index += 1

    if len(audio_files) > 10:
        print(f"\n{'='*80}")
        print(f"NOTE: {len(audio_files) - 10} additional files not displayed")
        print(f"{'='*80}")


def main():
    """
    Main function
    """
    print("Mutagen Testing Program")
    print("Version 0.00.05")
    print("Tests audio file metadata reading with pygame display")
    print("Allows embedding artwork at 1000x1000 resolution\n")
    print(f"Artwork will be saved to: {ARTWORK_DIRECTORY}\n")

    # Use default music directory
    print(f"Using default music directory: {MUSIC_DIRECTORY}\n")

    if os.path.exists(MUSIC_DIRECTORY):
        scan_music_directory(MUSIC_DIRECTORY)
    else:
        print(f"ERROR: Default music directory not found: {MUSIC_DIRECTORY}")

    print("\n\nTesting complete!")


if __name__ == "__main__":
    main()
