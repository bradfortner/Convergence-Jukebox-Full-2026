"""
Song Label Cache Module
Provides shared cache for consistent record label assignments across all popup modules

This module maintains a single source of truth for song-to-label mappings,
ensuring the same song always displays with the same record label regardless
of which popup module displays it.
"""
import random
from artist_label_mapping_module import get_artist_label
from year_range_label_mapping_module import get_labels_for_year


# Module-level cache to maintain consistent label assignments per song
# Maps "song_title||artist_name" to selected label filename
_song_label_cache = {}


def get_or_assign_label(song_title, artist_name, available_labels, year=None):
    """
    Get cached label for a song, or assign and cache a new label.

    Priority order:
    1. Check cache (ensures consistency across all popups)
    2. If not in cache, check artist-specific mapping
    3. If no artist mapping, filter labels by year range
    4. If no year range, randomly select from all available labels
    5. Cache and return the result

    Args:
        song_title (str): The title of the song
        artist_name (str): The artist name
        available_labels (list): List of available label filenames to choose from
        year (int/str, optional): The year the song was created

    Returns:
        str: The label filename assigned to this song
    """
    # Create unique song identifier
    song_id = f"{song_title}||{artist_name}"

    # Check cache first - this ensures consistency across all popups
    if song_id in _song_label_cache:
        label = _song_label_cache[song_id]
        print(f"[SHARED CACHE] Using cached label for '{song_title}': {label}")
        return label

    # Not in cache - check for artist-specific label mapping
    artist_specific_label = get_artist_label(artist_name)

    if artist_specific_label and artist_specific_label in available_labels:
        # Use artist-specific label
        label = artist_specific_label
        print(f"[SHARED CACHE] Artist-specific label for '{artist_name}': {label}")
    else:
        # No artist mapping - filter by year range
        year_filtered_labels = get_labels_for_year(year, available_labels)

        # Randomly select from year-filtered labels
        label = random.choice(year_filtered_labels)
        print(f"[SHARED CACHE] New song '{song_title}' (year: {year}) - randomly assigned: {label}")

    # Cache the label for future use
    _song_label_cache[song_id] = label
    return label


def clear_cache():
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


def get_cache_size():
    """
    Get the current number of songs in the cache.

    Returns:
        int: Number of songs currently cached
    """
    return len(_song_label_cache)
