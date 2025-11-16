import pygame
from PIL import Image
import io

def display_record_playing(image_path):
    """
    Rotate an image 45 times per second in real-time using pygame.
    Simulates a record player spinning with dark grey background.

    Args:
        image_path: Path to the input image (e.g., 'final_record_pressing.png')
    """
    # Load image with PIL
    pil_image = Image.open(image_path)

    # Convert to RGB if necessary (ensures compatibility)
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    # Initialize pygame
    pygame.init()

    # Convert PIL image to pygame surface using raw bytes
    # This preserves exact color values without any compression or color space conversion
    raw_bytes = pil_image.tobytes()
    original_surface = pygame.image.fromstring(raw_bytes, pil_image.size, 'RGB')

    # Set up display
    screen = pygame.display.set_mode((pil_image.width, pil_image.height))
    pygame.display.set_caption("Record Playing")
    clock = pygame.time.Clock()

    # Dark grey color
    dark_grey = (64, 64, 64)

    # Get center for rotation
    center_x = pil_image.width // 2
    center_y = pil_image.height // 2

    angle = 0
    running = True

    print("Starting endless animation (close window to stop)...")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill background with dark grey
        screen.fill(dark_grey)

        # Rotate the surface by the current angle
        rotated_surface = pygame.transform.rotate(original_surface, angle)

        # Get the rect of rotated surface and center it
        rotated_rect = rotated_surface.get_rect(center=(center_x, center_y))

        # Display rotated image
        screen.blit(rotated_surface, rotated_rect)
        pygame.display.flip()

        # Decrement angle: 240° per second at 30 fps = 8° per frame (reversed direction)
        angle = (angle - 8) % 360

        # 30 fps = 1000ms / 30 = ~33.33ms per frame
        clock.tick(30)

    pygame.quit()

# Usage example
if __name__ == "__main__":
    display_record_playing('final_record_pressing.png')
