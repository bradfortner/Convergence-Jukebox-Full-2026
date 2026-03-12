"""
Song Label Cache Module
Provides shared cache for consistent record label assignments across all popup modules

This module maintains a single source of truth for song-to-label mappings,
ensuring the same song always displays with the same record label regardless
of which popup module displays it.
"""
import random
import os
import io
import mutagen
from typing import Optional, Union
from PIL import Image
from artist_label_mapping_module import get_artist_label
from year_range_label_mapping_module import get_labels_for_year


# Module-level cache to maintain consistent label assignments per song
# Maps "song_title||artist_name" to selected label filename
_song_label_cache: dict[str, str] = {}


def check_and_extract_id3_image(song_file_path: str) -> bool:
    """
    Check if song has album art and 'image' in comment tag.
    If yes, extract and save as id3_image.png

    Args:
        song_file_path (str): Full path to the MP3 file

    Returns:
        bool: True if id3_image.png was created, False otherwise
    """
    try:
        if not song_file_path or not os.path.exists(song_file_path):
            return False

        # Load audio file with mutagen
        audio = mutagen.File(song_file_path)
        if audio is None:
            return False

        # Check comment tag for 'image' keyword
        comment = ''
        if 'COMM::eng' in audio:
            comment = str(audio['COMM::eng'])
        elif 'COMM' in audio:
            comment = str(audio['COMM'])

        # Check for 'image' keyword but exclude 'noimage' (which means DON'T use image)
        comment_lower = comment.lower()
        if 'image' not in comment_lower or 'noimage' in comment_lower:
            return False

        # Look for APIC (album art) tag
        image_data = None
        for key in audio.keys():
            if key.startswith('APIC'):
                image_data = audio[key].data
                break

        if not image_data:
            return False

        # Save as id3_image.png
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        image.save('id3_image.png', 'PNG')

        print(f"[ID3 PRIORITY] Extracted album art to id3_image.png from {os.path.basename(song_file_path)}")
        return True

    except Exception as e:
        print(f"[ID3 PRIORITY] Error extracting ID3 image: {e}")
        return False


def get_or_assign_label(song_title: str, artist_name: str, available_labels: list[str], year: Optional[Union[int, str]] = None, song_file_path: Optional[str] = None) -> str:
    """
    Get cached label for a song, or assign and cache a new label.

    Priority order:
    1. Check for ID3 album art (if song has 'image' in comment tag)
    2. Check for Christmas comment tag (if song has 'christmas' in comment tag)
    3. Check cache (ensures consistency across all popups)
    4. If not in cache, check artist-specific mapping
    5. If no artist mapping, filter labels by year range
    6. If no year range, randomly select from all available labels
    7. Cache and return the result

    Args:
        song_title (str): The title of the song
        artist_name (str): The artist name
        available_labels (list): List of available label filenames to choose from
        year (int/str, optional): The year the song was created
        song_file_path (str, optional): Full path to MP3 file for ID3 extraction

    Returns:
        str: The label filename assigned to this song, or "USE_ID3_IMAGE" if ID3 art found
    """
    # PRIORITY 1: Check for ID3 album art (HIGHEST PRIORITY)
    if song_file_path and check_and_extract_id3_image(song_file_path):
        print(f"[ID3 PRIORITY] Using ID3 album art for '{song_title}'")
        return "USE_ID3_IMAGE"

    # Create unique song identifier
    song_id = f"{song_title}||{artist_name}"

    # PRIORITY 2: Check for Christmas comment tag
    if song_file_path and os.path.exists(song_file_path):
        try:
            audio = mutagen.File(song_file_path)
            if audio is not None:
                comment = ''
                if 'COMM::eng' in audio:
                    comment = str(audio['COMM::eng'])
                elif 'COMM' in audio:
                    comment = str(audio['COMM'])
                
                if 'christmas' in comment.lower():
                    christmas_labels_dir = "record_labels/blank_record_labels_christmas"
                    if os.path.isdir(christmas_labels_dir):
                        christmas_labels = [f for f in os.listdir(christmas_labels_dir) if f.endswith('.png')]
                        if christmas_labels:
                            label_filename = random.choice(christmas_labels)
                            # Return a relative path to navigate from the standard dir to the christmas dir
                            label = os.path.join('..', 'blank_record_labels_christmas', label_filename)
                            _song_label_cache[song_id] = label
                            print(f"[CHRISTMAS PRIORITY] Assigning Christmas label for '{song_title}': {label}")
                            return label
        except Exception as e:
            print(f"[CHRISTMAS PRIORITY] Error checking for Christmas tag: {e}")

    # PRIORITY 3: Check cache first - this ensures consistency across all popups
    if song_id in _song_label_cache:
        label = _song_label_cache[song_id]
        print(f"[SHARED CACHE] Using cached label for '{song_title}': {label}")
        return label

    # PRIORITY 4: Not in cache - check for artist-specific label mapping
    artist_specific_label = get_artist_label(artist_name)

    if artist_specific_label and artist_specific_label in available_labels:
        # Use artist-specific label
        label = artist_specific_label
        print(f"[SHARED CACHE] Artist-specific label for '{artist_name}': {label}")
    else:
        # PRIORITY 5: No artist mapping - filter by year range
        year_filtered_labels = get_labels_for_year(year, available_labels)

        # PRIORITY 6: Randomly select from year-filtered labels
        label = random.choice(year_filtered_labels)
        print(f"[SHARED CACHE] New song '{song_title}' (year: {year}) - randomly assigned: {label}")

    # PRIORITY 7: Cache the label for future use
    _song_label_cache[song_id] = label
    return label


def clear_cache() -> None:
    """
    Clear the song-to-label cache only if it exceeds 50 songs.

    This allows recently selected/played songs to maintain their label
    assignments across different popups, while preventing unlimited
    cache growth during long jukebox sessions.
    """
    global _song_label_cache
    cache_size = len(_song_label_cache)

    # Only clear if cache has more than 50 songs
    if cache_size > 50:
        _song_label_cache.clear()
        print(f"[SHARED CACHE] Cache limit exceeded - cleared {cache_size} songs")
    else:
        print(f"[SHARED CACHE] Cache size OK ({cache_size} songs) - not clearing")


def get_cache_size() -> int:
    """
    Get the current number of songs in the cache.

    Returns:
        int: Number of songs currently cached
    """
    return len(_song_label_cache)
