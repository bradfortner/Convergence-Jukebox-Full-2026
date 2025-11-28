"""
Discogs Database Testing Program
Version 0.00.08
- Filters for 45rpm singles only
- Uses OpenCV ORB feature matching with MULTIPLE reference images
- Automatically loads ALL images from reference_labels directory
- Uses OCR to verify A-side labels
- Displays only matching A-side label images
- NEW: Automatically skips releases with no images

IMPORTANT: You MUST have a Discogs personal access token!
Get it from: https://www.discogs.com/settings/developers

REQUIREMENTS:
1. pip install pytesseract pillow opencv-python numpy
2. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract
   Windows: Download installer from releases page
   Set TESSERACT_PATH below after installation
3. Reference images: Place sample record labels in images/reference_labels/
   (Just drop images in the folder - they'll be loaded automatically!)
"""

import discogs_client
import pygame
import os
import requests
from io import BytesIO
from PIL import Image
import pytesseract
import tkinter as tk
from tkinter import simpledialog
import cv2
import numpy as np
import glob

# Initialize Discogs client
USER_AGENT = 'ConvergenceJukeboxTestApp/0.1'

# REQUIRED: Add your Discogs personal access token here
DISCOGS_TOKEN = "bGCHwaTOwBtZehtDSevHRNAeduBMWndweNelliBP"  # <--- PASTE YOUR TOKEN BETWEEN THE QUOTES

# REQUIRED: Set path to tesseract.exe after installation
# Example: r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # <--- UPDATE THIS PATH

# Reference images directory - automatically loads all images from this folder
REFERENCE_LABELS_DIR = r"images\reference_labels"

# Supported image formats
SUPPORTED_FORMATS = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff']

# Pygame display settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (100, 200, 255)
MATCH_COLOR = (100, 255, 100)  # Green for matching labels
NO_MATCH_COLOR = (255, 100, 100)  # Red for non-matching labels

# Global reference image features (loaded once at startup)
reference_features = []  # List of (name, keypoints, descriptors)
orb_detector = None


def load_reference_images():
    """
    Automatically load ALL images from the reference_labels directory
    Returns True if at least one reference loaded successfully
    """
    global reference_features, orb_detector

    print(f"\n{'='*80}")
    print(f"LOADING REFERENCE IMAGES")
    print(f"{'='*80}")
    print(f"Scanning directory: {REFERENCE_LABELS_DIR}")

    # Check if directory exists
    if not os.path.exists(REFERENCE_LABELS_DIR):
        print(f"\n✗ Reference directory does not exist!")
        print(f"  Please create: {REFERENCE_LABELS_DIR}")
        print(f"  And add sample record label images to it")
        return False

    # Find all image files in the directory
    image_files = []
    for format_pattern in SUPPORTED_FORMATS:
        pattern = os.path.join(REFERENCE_LABELS_DIR, format_pattern)
        image_files.extend(glob.glob(pattern))

    if not image_files:
        print(f"\n✗ No images found in reference directory!")
        print(f"  Please add sample record label images to: {REFERENCE_LABELS_DIR}")
        print(f"  Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        return False

    print(f"\n✓ Found {len(image_files)} image file(s) to load")

    # Create ORB detector
    # nfeatures: Maximum number of features to retain (higher = more detailed matching)
    orb_detector = cv2.ORB_create(nfeatures=1000)

    loaded_count = 0

    for i, ref_path in enumerate(image_files, 1):
        try:
            ref_name = os.path.basename(ref_path)
            print(f"\nReference Image {i}: {ref_name}")

            # Load reference image
            ref_image = cv2.imread(ref_path)
            if ref_image is None:
                print(f"  ✗ Failed to load image - SKIPPING")
                continue

            print(f"  ✓ Loaded: {ref_image.shape[1]}x{ref_image.shape[0]}")

            # Convert to grayscale
            ref_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

            # Detect keypoints and compute descriptors
            keypoints, descriptors = orb_detector.detectAndCompute(ref_gray, None)

            if descriptors is None or len(keypoints) == 0:
                print(f"  ✗ No features found - SKIPPING")
                continue

            # Store features
            reference_features.append((ref_name, keypoints, descriptors))
            loaded_count += 1

            print(f"  ✓ Extracted {len(keypoints)} ORB features")

        except Exception as e:
            print(f"  ✗ Error loading reference: {e}")
            continue

    print(f"\n{'='*80}")
    print(f"REFERENCE LOADING COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Successfully loaded {loaded_count} reference image(s)")
    print(f"✗ Failed to load {len(image_files) - loaded_count} reference image(s)")

    return loaded_count > 0


def is_similar_to_reference_label(image_surface):
    """
    Use ORB feature matching to compare image against ALL reference labels
    Returns (is_label, confidence, match_count, best_reference_name)
    """
    global reference_features, orb_detector

    try:
        # Convert pygame surface to numpy array for OpenCV
        width, height = image_surface.get_size()
        raw_str = pygame.image.tostring(image_surface, 'RGB')

        # Convert to numpy array
        img_array = np.frombuffer(raw_str, dtype=np.uint8)
        img_array = img_array.reshape((height, width, 3))

        # Convert RGB to BGR (OpenCV uses BGR)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # Convert to grayscale for feature detection
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Detect keypoints and compute descriptors for this image
        keypoints, descriptors = orb_detector.detectAndCompute(gray, None)

        if descriptors is None or len(keypoints) == 0:
            print(f"  Feature matching: No features found in test image")
            return False, 0, 0, None

        print(f"  Feature matching: Found {len(keypoints)} features in test image")

        # Create BFMatcher (Brute Force Matcher)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

        # Compare against ALL reference images
        best_match_count = 0
        best_reference_name = None
        best_confidence = 0

        for ref_name, ref_keypoints, ref_descriptors in reference_features:
            # Match descriptors using KNN (K-Nearest Neighbors, k=2)
            matches = bf.knnMatch(ref_descriptors, descriptors, k=2)

            # Apply Lowe's ratio test to filter good matches
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    # If best match is significantly better than second-best match (0.75 ratio)
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)

            match_count = len(good_matches)

            # Calculate confidence for this reference
            if match_count >= 30:
                confidence = 100
            elif match_count >= 15:
                confidence = int((match_count / 30) * 100)
            else:
                confidence = int((match_count / 15) * 50)

            print(f"    vs {ref_name}: {match_count} matches ({confidence}% confidence)")

            # Keep track of best match
            if match_count > best_match_count:
                best_match_count = match_count
                best_reference_name = ref_name
                best_confidence = confidence

        # Consider it a label if we have at least 15 good feature matches with ANY reference
        is_label = best_match_count >= 15

        if is_label:
            print(f"  ✓ LABEL DETECTED! Best match: {best_reference_name} ({best_match_count} matches, {best_confidence}% confidence)")
        else:
            print(f"  ✗ Not a label (best: {best_match_count} matches with {best_reference_name}, need 15+)")

        return is_label, best_confidence, best_match_count, best_reference_name

    except Exception as e:
        print(f"  ✗ Feature matching error: {e}")
        import traceback
        traceback.print_exc()
        return False, 0, 0, None


def extract_text_from_image(image_surface, song_title):
    """
    Use OCR to extract text from image and check if it matches the song title
    Returns (text_found, match_score, extracted_text)
    """
    try:
        # Set tesseract path
        if os.path.exists(TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        else:
            print(f"  ⚠ Tesseract not found at: {TESSERACT_PATH}")
            print(f"  Skipping OCR for this image")
            return False, 0, ""

        # Convert pygame surface to PIL Image
        width, height = image_surface.get_size()
        raw_str = pygame.image.tostring(image_surface, 'RGB')
        pil_image = Image.frombytes('RGB', (width, height), raw_str)

        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(pil_image)

        # Clean up text for matching - remove extra whitespace and normalize
        extracted_text_clean = ' '.join(extracted_text.lower().split())
        song_title_clean = song_title.lower().strip()

        print(f"  OCR extracted: {extracted_text_clean[:100]}...")  # Debug: show extracted text

        # STRICT MATCHING: Require the full song title to be present
        if song_title_clean in extracted_text_clean:
            match_score = 100
            text_found = True
            print(f"  ✓ Exact match found!")
        else:
            # Check for partial matches (each word) - REQUIRE 90% match
            words = song_title_clean.split()
            # Only count words longer than 2 characters (skip "i", "to", "a", etc.)
            significant_words = [w for w in words if len(w) > 2]

            if significant_words:
                matches = sum(1 for word in significant_words if word in extracted_text_clean)
                match_score = int((matches / len(significant_words)) * 100)
                # STRICT: Require 90% of significant words to match
                text_found = match_score >= 90
                print(f"  Partial match: {matches}/{len(significant_words)} significant words = {match_score}%")
            else:
                match_score = 0
                text_found = False

        return text_found, match_score, extracted_text.strip()

    except Exception as e:
        print(f"  ✗ OCR Error: {e}")
        return False, 0, ""


def download_image(url):
    """
    Download an image from URL and return as pygame surface
    """
    try:
        print(f"  Downloading: {url[:80]}...")

        # Add browser-like headers to avoid 403 Forbidden
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.discogs.com/',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        print(f"  ✓ Download complete ({len(response.content)} bytes)")

        image_data = BytesIO(response.content)
        image_surface = pygame.image.load(image_data)

        print(f"  ✓ Image loaded: {image_surface.get_width()}x{image_surface.get_height()}")
        return image_surface
    except Exception as e:
        print(f"  ✗ Error downloading image: {e}")
        return None


def display_with_pygame(release_data, label_images, other_images, current_num, total_results, song_title):
    """
    Display label images and metadata side-by-side using pygame
    Uses ORB feature matching + OCR to find and verify A-side labels
    Returns "next" for next result, "prev" for previous result, "quit" to exit
    """
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Discogs Release Viewer - Auto-Load Multi-Reference ORB + OCR")

    # Fonts
    font_title = pygame.font.SysFont('Arial', 24, bold=True)
    font_normal = pygame.font.SysFont('Arial', 18)
    font_small = pygame.font.SysFont('Arial', 14)
    font_tiny = pygame.font.SysFont('Arial', 12)

    # Download and analyze images - TRIPLE FILTER:
    # 1. Must be a "label" type image from Discogs
    # 2. Must match ANY reference label features (detected by ORB)
    # 3. Must match song title via OCR (A-side)
    image_data_list = []  # List of (surface, is_match, match_score, extracted_text, feature_count, ref_name)
    total_labels_checked = 0
    matching_label_found = False

    if label_images:
        print(f"\nDownloading and analyzing {len(label_images)} label images...")
        for i, img in enumerate(label_images, 1):
            # Stop after finding the first match
            if matching_label_found:
                print(f"\nLabel Image {i}: Skipping (already found A-side)")
                continue

            print(f"\nLabel Image {i}:")
            surface = download_image(img['uri'])
            if surface:
                total_labels_checked += 1

                # FILTER 1: ORB Feature Matching - Does this match ANY reference label?
                print(f"  Running ORB feature matching against {len(reference_features)} reference(s)...")
                is_similar, feature_confidence, match_count, ref_name = is_similar_to_reference_label(surface)

                if not is_similar:
                    print(f"  ✗ Not similar to any reference label - SKIPPING (likely a cover/sleeve)")
                    continue

                print(f"  ✓ Label detected! Matched: {ref_name}")

                # FILTER 2: OCR - Does it match the song title?
                print(f"  Running OCR...")
                is_match, match_score, extracted_text = extract_text_from_image(surface, song_title)

                if is_match:
                    print(f"  ✓ MATCH! Score: {match_score}% - This is the A-side! KEEPING THIS IMAGE")
                    print(f"  >>> STOPPING - Found the A-side label, ignoring all other images")
                    matching_label_found = True
                    image_data_list.append((surface, is_match, match_score, extracted_text, match_count, ref_name))
                else:
                    print(f"  ✗ No OCR match (Score: {match_score}%) - B-side, SKIPPING")

        if matching_label_found:
            print(f"\n  Summary: Found 1 A-side label out of {total_labels_checked} checked (stopped after first match)")
        else:
            print(f"\n  Summary: No A-side labels found out of {total_labels_checked} checked")

    # If no matching labels found, download and check "other" images
    if len(image_data_list) == 0 and other_images:
        print(f"\nNo matching A-side labels found. Checking other images for similar labels...")
        images_to_check = min(5, len(other_images))

        for i, img in enumerate(other_images[:images_to_check], 1):
            if matching_label_found:
                break

            print(f"\nOther Image {i}:")
            surface = download_image(img['uri'])
            if surface:
                # Check if it matches ANY reference features
                print(f"  Running ORB feature matching against {len(reference_features)} reference(s)...")
                is_similar, feature_confidence, match_count, ref_name = is_similar_to_reference_label(surface)

                if is_similar:
                    print(f"  ✓ Label found in 'other' images! Matched: {ref_name}")
                    # Don't do OCR fallback - if it's not marked as a label, skip OCR
                    image_data_list.append((surface, None, 0, "", match_count, ref_name))
                    break
                else:
                    print(f"  ✗ Not similar to any reference - SKIPPING")

    print(f"\n✓ Loaded {len(image_data_list)} images for display")

    # Main display loop
    running = True
    clock = pygame.time.Clock()
    show_ocr_text = False  # Toggle to show/hide extracted text

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return "quit"
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return "next"
                elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    return "prev"
                elif event.key == pygame.K_o:  # Press 'O' to toggle OCR text display
                    show_ocr_text = not show_ocr_text

        # Fill background
        screen.fill(BACKGROUND_COLOR)

        # Top: Result counter
        counter_text = font_normal.render(f"Result {current_num} of {total_results}", True, HIGHLIGHT_COLOR)
        counter_rect = counter_text.get_rect(center=(WINDOW_WIDTH // 2, 20))
        screen.blit(counter_text, counter_rect)

        # Left side: Display images
        current_y = 50

        # Debug: Show how many images we have
        if len(image_data_list) > 0:
            debug_text = font_small.render(f"Displaying {len(image_data_list)} image(s)", True, (100, 255, 100))
            screen.blit(debug_text, (10, 30))
        else:
            debug_text = font_small.render("No matching labels found", True, (255, 100, 100))
            screen.blit(debug_text, (10, 30))

        # ONLY DISPLAY THE FIRST IMAGE (A-side label only)
        for i, (img_surface, is_match, match_score, extracted_text, feature_count, ref_name) in enumerate(image_data_list[:1], 1):
            # Scale image to fit
            img_rect = img_surface.get_rect()
            max_size = 400  # Larger display for single label
            if img_rect.width > max_size or img_rect.height > max_size:
                scale_factor = min(max_size / img_rect.width, max_size / img_rect.height)
                new_width = int(img_rect.width * scale_factor)
                new_height = int(img_rect.height * scale_factor)
                scaled_surface = pygame.transform.scale(img_surface, (new_width, new_height))
            else:
                scaled_surface = img_surface

            # Center image on left side
            img_x = 200 - scaled_surface.get_width() // 2
            screen.blit(scaled_surface, (img_x, current_y))

            # Image label with OCR result
            if is_match is not None:  # This was a label image with OCR
                if is_match:
                    label_color = MATCH_COLOR
                    label_str = f"✓ A-SIDE LABEL (OCR: {match_score}%)"
                else:
                    label_color = NO_MATCH_COLOR
                    label_str = f"B-side (OCR: {match_score}%)"
            else:
                label_color = (180, 180, 180)
                label_str = f"Similar Label ({feature_count} matches)"

            label_text = font_small.render(label_str, True, label_color)
            screen.blit(label_text, (img_x, current_y + scaled_surface.get_height() + 5))

            # Show which reference matched
            if ref_name:
                ref_text = font_tiny.render(f"Matched: {ref_name}", True, (150, 150, 150))
                screen.blit(ref_text, (img_x, current_y + scaled_surface.get_height() + 25))

            # Show extracted text if enabled and available
            if show_ocr_text and extracted_text and is_match is not None:
                y_offset = current_y + scaled_surface.get_height() + 45
                ocr_lines = extracted_text.split('\n')[:3]  # Show first 3 lines
                for line in ocr_lines:
                    if line.strip():
                        ocr_text = font_tiny.render(line[:30], True, (150, 150, 150))
                        screen.blit(ocr_text, (img_x, y_offset))
                        y_offset += 15

        if not image_data_list:
            # No images message
            no_img_text = font_normal.render("No Matching Labels Found", True, (150, 150, 150))
            screen.blit(no_img_text, (100, 200))
            hint_text = font_small.render("This release may not have label images", True, (120, 120, 120))
            screen.blit(hint_text, (100, 230))

        # Right side: Display metadata
        x_start = 450
        y_start = 50

        # Title
        title_text = font_title.render("Release Information", True, HIGHLIGHT_COLOR)
        screen.blit(title_text, (x_start, y_start))
        y_start += 50

        # Searching for (song title)
        search_label = font_normal.render("Searching for:", True, HIGHLIGHT_COLOR)
        screen.blit(search_label, (x_start, y_start))
        search_value = font_normal.render(song_title[:40], True, MATCH_COLOR)
        screen.blit(search_value, (x_start, y_start + 25))
        y_start += 65

        # Title
        if 'title' in release_data:
            label = font_normal.render("Title:", True, HIGHLIGHT_COLOR)
            screen.blit(label, (x_start, y_start))
            value = font_normal.render(str(release_data['title'])[:50], True, TEXT_COLOR)
            screen.blit(value, (x_start, y_start + 25))
            y_start += 65

        # Artists
        if 'artists' in release_data and release_data['artists']:
            artist_names = ', '.join([a['name'] for a in release_data['artists']])
            label = font_normal.render("Artist(s):", True, HIGHLIGHT_COLOR)
            screen.blit(label, (x_start, y_start))
            value = font_normal.render(artist_names[:50], True, TEXT_COLOR)
            screen.blit(value, (x_start, y_start + 25))
            y_start += 65

        # Year
        if 'year' in release_data:
            label = font_normal.render("Year:", True, HIGHLIGHT_COLOR)
            screen.blit(label, (x_start, y_start))
            value = font_normal.render(str(release_data['year']), True, TEXT_COLOR)
            screen.blit(value, (x_start, y_start + 25))
            y_start += 65

        # Labels
        if 'labels' in release_data and release_data['labels']:
            label_names = ', '.join([lbl['name'] for lbl in release_data['labels']])
            label = font_normal.render("Label(s):", True, HIGHLIGHT_COLOR)
            screen.blit(label, (x_start, y_start))
            value = font_normal.render(label_names[:50], True, TEXT_COLOR)
            screen.blit(value, (x_start, y_start + 25))

            # Catalog number
            if 'catno' in release_data['labels'][0]:
                catno = font_small.render(f"Cat #: {release_data['labels'][0]['catno']}", True, (200, 200, 200))
                screen.blit(catno, (x_start, y_start + 50))
            y_start += 90

        # Country
        if 'country' in release_data:
            label = font_normal.render("Country:", True, HIGHLIGHT_COLOR)
            screen.blit(label, (x_start, y_start))
            value = font_normal.render(str(release_data['country']), True, TEXT_COLOR)
            screen.blit(value, (x_start, y_start + 25))
            y_start += 65

        # Format
        if 'formats' in release_data and release_data['formats']:
            fmt = release_data['formats'][0]
            format_name = fmt.get('name', 'Unknown')
            label = font_normal.render("Format:", True, HIGHLIGHT_COLOR)
            screen.blit(label, (x_start, y_start))
            value = font_normal.render(format_name, True, TEXT_COLOR)
            screen.blit(value, (x_start, y_start + 25))

            # Format descriptions
            if 'descriptions' in fmt:
                desc_str = ', '.join(fmt['descriptions'])
                desc_text = font_small.render(desc_str[:60], True, (200, 200, 200))
                screen.blit(desc_text, (x_start, y_start + 50))
            y_start += 90

        # Instructions at bottom
        instruction_text = font_small.render("RIGHT/DOWN: Next | LEFT/UP: Previous | O: Toggle OCR Text | ESC: Quit", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(instruction_text, instruction_rect)

        pygame.display.flip()
        clock.tick(30)


def main():
    """
    Main function - Search, download images, perform auto-loaded multi-reference ORB matching + OCR, and display
    """
    print("="*80)
    print("Discogs Image Viewer - Auto-Load Multi-Reference ORB Matching + OCR")
    print("="*80)

    # Check if token is provided
    if not DISCOGS_TOKEN or DISCOGS_TOKEN.strip() == "":
        print("\n" + "="*80)
        print("ERROR: Discogs API token is required!")
        print("="*80)
        print("\nPlease add your token to line 30 of this file.")
        print("Get it from: https://www.discogs.com/settings/developers")
        return

    # Load reference images and extract features (auto-loads from directory)
    if not load_reference_images():
        print("\n" + "="*80)
        print("ERROR: Failed to load any reference images!")
        print("="*80)
        print(f"\nPlease add sample record label images to:")
        print(f"{REFERENCE_LABELS_DIR}")
        print(f"\nSupported formats: {', '.join(SUPPORTED_FORMATS)}")
        return

    # Check if Tesseract is installed
    if not os.path.exists(TESSERACT_PATH):
        print("\n" + "="*80)
        print("WARNING: Tesseract OCR not found!")
        print("="*80)
        print(f"Expected location: {TESSERACT_PATH}")
        print("\nTo use OCR features:")
        print("1. Download Tesseract: https://github.com/tesseract-ocr/tesseract")
        print("2. Install it")
        print("3. Update TESSERACT_PATH in this file (line 33)")
        print("\nContinuing without OCR...")
        input("Press Enter to continue...")

    # Get search input from user
    print("\n" + "="*80)
    print("SEARCH INPUT")
    print("="*80)

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring dialogs to front

    # Get artist name
    artist_name = simpledialog.askstring(
        "Artist Name",
        "Enter the artist name:",
        initialvalue="The Beatles"
    )

    if not artist_name:
        print("\n✗ No artist entered. Exiting...")
        root.destroy()
        return

    # Get song title
    song_title = simpledialog.askstring(
        "Song Title",
        "Enter the song title:",
        initialvalue="I Want To Hold Your Hand"
    )

    if not song_title:
        print("\n✗ No song title entered. Exiting...")
        root.destroy()
        return

    root.destroy()

    print(f"\n✓ Searching for: {artist_name} - {song_title}")

    # Initialize client
    try:
        client = discogs_client.Client(USER_AGENT, user_token=DISCOGS_TOKEN)
        print("\n✓ Connected to Discogs API")
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        return

    # Search for the song
    print("\n" + "="*80)
    print("SEARCHING...")
    print("="*80)

    try:
        search_query = f"{artist_name} {song_title}"
        results = client.search(search_query, type='release')
        print(f"\n✓ Search completed")
    except Exception as e:
        print(f"\n✗ Search failed: {e}")
        return

    # Build list of releases - FILTER FOR 45RPM SINGLES ONLY
    print("\nFiltering for 45rpm singles (7\" vinyl)...")
    release_list = []
    count = 0
    checked = 0

    for release in results:
        checked += 1
        if count >= 20:  # Limit to 20 results
            break

        if not (hasattr(release, 'data') and 'id' in release.data):
            continue

        # Check if it's a 45rpm single (7" format)
        is_45rpm = False
        if 'format' in release.data:
            formats = release.data['format']
            format_str = ', '.join(formats) if isinstance(formats, list) else str(formats)
            format_str_lower = format_str.lower()

            # Look for 7" or 45 RPM indicators
            if any(keyword in format_str_lower for keyword in ['7"', '45 rpm', 'single']):
                # Make sure it's not an LP or 12"
                if '12"' not in format_str_lower and 'lp' not in format_str_lower:
                    is_45rpm = True
                    print(f"  ✓ Found: {release.title} [{format_str}]")

        if is_45rpm:
            release_list.append(release)
            count += 1

        # Stop searching after checking 100 results
        if checked >= 100:
            break

    if not release_list:
        print("\n✗ No 45rpm singles found in first 100 results")
        print("  Try searching for a different song or artist")
        return

    total_results = len(release_list)
    print(f"\n✓ Found {total_results} 45rpm singles to browse")

    # Navigation loop
    current_index = 0

    while 0 <= current_index < total_results:
        current_release = release_list[current_index]
        release_id = current_release.data['id']

        print(f"\n{'='*80}")
        print(f"Result {current_index + 1} of {total_results}: {current_release.title}")
        print(f"Release ID: {release_id}")
        print(f"{'='*80}")

        # Get full details
        try:
            release = client.release(release_id)
            print(f"✓ Retrieved: {release.title}")
        except Exception as e:
            print(f"✗ Error getting details: {e}")
            current_index += 1
            continue

        # Separate label images from other images
        label_images = []
        other_images = []

        if hasattr(release, 'images') and release.images:
            print(f"✓ Found {len(release.images)} total images")

            for image in release.images:
                img_type = image.get('type', 'Unknown')

                if img_type.lower() == 'label':
                    label_images.append(image)
                else:
                    other_images.append(image)

            print(f"\n  Summary:")
            print(f"  - Label images: {len(label_images)}")
            print(f"  - Other images: {len(other_images)}")
        else:
            # NEW: Skip releases with no images - auto-advance to next
            print("✗ No images found for this release - SKIPPING to next...")
            current_index += 1
            continue

        # Display in pygame window with auto-loaded multi-reference ORB matching + OCR
        print("\nLaunching pygame viewer with auto-loaded multi-reference ORB matching + OCR...")
        navigation = display_with_pygame(release.data, label_images, other_images, current_index + 1, total_results, song_title)

        if navigation == "quit":
            print("\nExiting viewer...")
            break
        elif navigation == "next":
            current_index += 1
        elif navigation == "prev":
            current_index -= 1
            # Don't go before first result
            if current_index < 0:
                current_index = 0

    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
