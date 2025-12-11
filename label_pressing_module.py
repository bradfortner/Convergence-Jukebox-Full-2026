"""
Label Pressing Module
Combines new_cutout_label.png with adaptor.png overlay to create final_record.png
"""

import pygame
from PIL import Image
import os
import sys


def combine_pngs(label_path, adaptor_path, output_path='final_record.png', size=(250, 250), base_record_path='blank_record.png'):
    """
    Combines three transparent PNG images and saves the result.
    Layer order (bottom to top): blank_record.png, adaptor.png, new_cutout_label.png

    Parameters:
    - label_path: Path to label PNG (top layer)
    - adaptor_path: Path to adaptor PNG (middle layer)
    - output_path: Output filename (default: 'final_record.png')
    - size: Output size as tuple (default: 250x250)
    - base_record_path: Path to base blank record PNG (bottom layer)

    Returns:
    - True if successful, False otherwise
    """
    try:
        # Check if files exist
        if not os.path.exists(label_path):
            print(f"Error: Label file not found: {label_path}")
            return False

        if not os.path.exists(adaptor_path):
            print(f"Error: Adaptor file not found: {adaptor_path}")
            return False

        if not os.path.exists(base_record_path):
            print(f"Error: Base record file not found: {base_record_path}")
            return False

        # Open all three images
        label = Image.open(label_path).convert('RGBA')
        adaptor = Image.open(adaptor_path).convert('RGBA')
        base_record = Image.open(base_record_path).convert('RGBA')

        # Resize label and base_record to target size
        label = label.resize(size, Image.Resampling.LANCZOS)
        base_record = base_record.resize(size, Image.Resampling.LANCZOS)

        # Keep adaptor at its original size (DO NOT resize to match background)
        # This makes the adapter appear bigger

        # Create final image at target size
        final_image = Image.new('RGBA', size, (0, 0, 0, 0))

        # Layer 1: Paste blank_record.png as base
        final_image.paste(base_record, (0, 0), base_record)

        # Layer 2: Paste adapter in middle (centered with offset)
        adaptor_x = (size[0] - adaptor.width) // 2 - 2  # -2 pixels horizontal offset
        adaptor_y = (size[1] - adaptor.height) // 2
        final_image.paste(adaptor, (adaptor_x, adaptor_y), adaptor)

        # Layer 3: Paste label on top
        final_image.paste(label, (0, 0), label)

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
    label_path = "new_cutout_label.png"
    adaptor_path = "adaptor.png"
    base_record_path = "blank_record.png"
    output_path = "final_record.png"

    # Combine images (3 layers: blank_record, adaptor, label)
    print("Combining images...")
    success = combine_pngs(label_path, adaptor_path, output_path, size=(250, 250), base_record_path=base_record_path)

    if success:
        print("Displaying result...")
        display_image(output_path)
    else:
        print("Failed to create combined image.")
        sys.exit(1)
