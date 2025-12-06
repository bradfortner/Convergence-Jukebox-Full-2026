"""
Label Pressing Module
Combines new_cutout_label.png with adaptor.png overlay to create final_record.png
"""

import pygame
from PIL import Image
import os
import sys


def combine_pngs(background_path, overlay_path, output_path='final_record.png', size=(250, 250)):
    """
    Combines two transparent PNG images and saves the result.

    Parameters:
    - background_path: Path to background PNG (bottom layer)
    - overlay_path: Path to overlay PNG (top layer - adaptor)
    - output_path: Output filename (default: 'final_record.png')
    - size: Output size as tuple (default: 250x250)

    Returns:
    - True if successful, False otherwise
    """
    try:
        # Check if files exist
        if not os.path.exists(background_path):
            print(f"Error: Background file not found: {background_path}")
            return False

        if not os.path.exists(overlay_path):
            print(f"Error: Overlay file not found: {overlay_path}")
            return False

        # Open both images
        background = Image.open(background_path).convert('RGBA')
        overlay = Image.open(overlay_path).convert('RGBA')

        # Resize background to target size
        background = background.resize(size, Image.Resampling.LANCZOS)

        # Resize overlay to match background (or keep proportional)
        overlay = overlay.resize(size, Image.Resampling.LANCZOS)

        # Create new image and paste layers
        final_image = Image.new('RGBA', size, (0, 0, 0, 0))
        final_image.paste(background, (0, 0), background)
        final_image.paste(overlay, (0, 0), overlay)

        # Save result
        final_image.save(output_path, 'PNG')
        print(f"Successfully created: {output_path}")
        return True

    except Exception as e:
        print(f"Error combining images: {e}")
        return False


def display_image(image_path):
    """
    Display the combined image using pygame and hold it on screen.
    Press ESC or close window to exit.

    Parameters:
    - image_path: Path to image to display
    """
    try:
        # Initialize pygame
        pygame.init()

        # Load image
        image = pygame.image.load(image_path)
        image_rect = image.get_rect()

        # Create window (add padding around image)
        screen_width = image_rect.width + 100
        screen_height = image_rect.height + 100
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Final Record Label")

        # Center image on screen
        image_x = (screen_width - image_rect.width) // 2
        image_y = (screen_height - image_rect.height) // 2

        # Main loop
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Clear screen to black
            screen.fill((0, 0, 0))

            # Draw image
            screen.blit(image, (image_x, image_y))

            # Update display
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    except Exception as e:
        print(f"Error displaying image: {e}")
        pygame.quit()


if __name__ == "__main__":
    # Define paths
    background_path = "images/new_cutout_label.png"
    overlay_path = "images/adaptor.png"
    output_path = "final_record.png"

    # Combine images
    print("Combining images...")
    success = combine_pngs(background_path, overlay_path, output_path, size=(250, 250))

    if success:
        print("Displaying result...")
        display_image(output_path)
    else:
        print("Failed to create combined image.")
        sys.exit(1)
