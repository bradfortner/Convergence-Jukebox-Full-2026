"""
ID3 Tag Writer Module
Writes metadata and album art to MP3 files using mutagen
"""

import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, COMM, APIC
import os
import logging

def write_id3_tags(filename, title, artist, year, genre, comment, image_path=None):
    """
    Write ID3 tags to an MP3 file

    Args:
        filename: The filename (without path) in the 'music' directory
        title: Song title
        artist: Artist name
        year: Year (as string)
        genre: Genre (as string)
        comment: Comment text
        image_path: Optional path to album art image (PNG/JPG)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Construct full path to music file
        music_path = os.path.join('processed', filename)

        # Check if file exists
        if not os.path.exists(music_path):
            logging.error(f"File not found: {music_path}")
            print(f"ERROR: File not found: {music_path}")
            return False

        # Load the MP3 file
        print(f"Writing ID3 tags to {filename}...")
        logging.info(f"Starting ID3 tag write for {filename}")

        try:
            audio = ID3(music_path)
        except mutagen.id3.ID3NoHeaderError:
            # Create new ID3 tag if none exists
            audio = ID3()

        # Write text tags (genre is already sanitized on ConfirmationScreen)
        audio["TIT2"] = TIT2(encoding=3, text=title)  # Title
        audio["TPE1"] = TPE1(encoding=3, text=artist)  # Artist
        audio["TALB"] = TALB(encoding=3, text=title)  # Album (use title as album)
        audio["TCON"] = TCON(encoding=3, text=genre)  # Genre
        audio["TDRC"] = TDRC(encoding=3, text=year)  # Year

        # Delete ALL existing COMM tags first to prevent duplicates
        comm_keys_to_delete = [key for key in audio.keys() if key.startswith('COMM')]
        for key in comm_keys_to_delete:
            del audio[key]
            logging.info(f"Deleted existing comment tag: {key}")

        audio["COMM"] = COMM(encoding=3, lang='eng', desc='', text=comment)  # Comment

        # Write album art if provided
        if image_path and os.path.exists(image_path):
            # Delete ALL existing APIC tags first
            apic_keys_to_delete = [key for key in audio.keys() if key.startswith('APIC')]
            for key in apic_keys_to_delete:
                del audio[key]
                logging.info(f"Deleted existing album art tag: {key}")

            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()

            # Determine MIME type based on extension
            if image_path.lower().endswith('.png'):
                mime = 'image/png'
            elif image_path.lower().endswith(('.jpg', '.jpeg')):
                mime = 'image/jpeg'
            else:
                mime = 'image/png'  # Default to PNG

            # Add new album art
            audio["APIC"] = APIC(
                encoding=3,
                mime=mime,
                type=3,  # Cover (front)
                desc='Cover',
                data=image_data
            )
            logging.info(f"Added new album art from {image_path}")
            print(f"Added new album art from {image_path}")

        # Save tags to file
        audio.save(music_path)

        logging.info(f"Successfully wrote ID3 tags to {filename}")
        print(f"Successfully wrote ID3 tags to {filename}")
        return True

    except Exception as e:
        logging.error(f"Error writing ID3 tags to {filename}: {e}")
        print(f"ERROR: Failed to write ID3 tags to {filename}: {e}")
        return False


def read_id3_tags(filename):
    """
    Read ID3 tags from an MP3 file

    Args:
        filename: The filename (without path) in the 'music' directory

    Returns:
        dict: Dictionary of tag values, or None if error
    """
    try:
        music_path = os.path.join('processed', filename)

        if not os.path.exists(music_path):
            logging.error(f"File not found: {music_path}")
            return None

        audio = mutagen.File(music_path)
        if audio is None:
            return None

        tags = {}

        def get_tag_text(tag_key, default='N/A'):
            return audio.get(tag_key, [default])[0] if audio.get(tag_key) else default

        tags['artist'] = get_tag_text('TPE1')
        tags['title'] = get_tag_text('TIT2')
        tags['album'] = get_tag_text('TALB')
        tags['genre'] = get_tag_text('TCON')
        tags['year'] = get_tag_text('TDRC', get_tag_text('TYER'))
        tags['comment'] = get_tag_text('COMM::eng', get_tag_text('COMM'))

        # Check for album art and extract image data
        tags['has_image'] = False
        tags['image_data'] = None
        for key in audio.keys():
            if key.startswith('APIC'):
                tags['has_image'] = True
                tags['image_data'] = audio[key].data
                break

        return tags

    except Exception as e:
        logging.error(f"Error reading ID3 tags from {filename}: {e}")
        print(f"ERROR: Failed to read ID3 tags from {filename}: {e}")
        return None
