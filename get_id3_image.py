import os
import mutagen
from PIL import Image
import io

def find_and_extract_id3_image():
    """
    Scans the music directory for the first file with "image" in the Comments tag
    and saves its embedded image as a transparent PNG to id3_image.png
    """
    music_dir = 'music'

    if not os.path.exists(music_dir):
        print(f"Error: '{music_dir}' directory not found.")
        return False

    # Get all files in the music directory
    music_files = [f for f in os.listdir(music_dir) if os.path.isfile(os.path.join(music_dir, f))]

    if not music_files:
        print(f"No files found in '{music_dir}' directory.")
        return False

    print(f"Scanning {len(music_files)} files in '{music_dir}' directory...")

    # Scan each file for "image" in comment tag
    for filename in music_files:
        filepath = os.path.join(music_dir, filename)

        try:
            # Load the audio file with mutagen
            audio = mutagen.File(filepath)

            if audio is None:
                continue

            # Get comment tag
            comment = ''
            if 'COMM::eng' in audio:
                comment = str(audio['COMM::eng'])
            elif 'COMM' in audio:
                comment = str(audio['COMM'])

            # Check if "image" is in the comment
            if 'image' in comment.lower():
                print(f"\nFound file with 'image' in comment: {filename}")
                print(f"Comment: {comment}")

                # Look for APIC (Attached Picture) tags
                image_data = None
                for key in audio.keys():
                    if key.startswith('APIC'):
                        image_data = audio[key].data
                        print(f"Image tag: {key}")
                        break

                if image_data:
                    # Convert image data to PIL Image
                    image = Image.open(io.BytesIO(image_data))

                    # Convert to RGBA if not already (to support transparency)
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')

                    # Save as PNG with transparency support
                    output_path = 'id3_image.png'
                    image.save(output_path, 'PNG')

                    print(f"Image saved to: {output_path}")
                    print(f"Image size: {image.size}")
                    print(f"Image mode: {image.mode}")

                    return True
                else:
                    print(f"Warning: File has 'image' in comment but no embedded image found.")

        except Exception as e:
            # Skip files that can't be read
            continue

    print("\nNo files with 'image' in comment tag found in the music directory.")
    return False

if __name__ == '__main__':
    print("ID3 Image Extractor")
    print("=" * 50)
    success = find_and_extract_id3_image()

    if success:
        print("\nSuccess! Image extracted and saved as id3_image.png")
    else:
        print("\nFailed to extract image.")
