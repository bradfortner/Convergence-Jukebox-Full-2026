"""
Song Label Cache Module
Provides shared cache for consistent record label assignments across all popup modules

This module maintains a single source of truth for song-to-label mappings,
ensuring the same song always displays with the same record label regardless
of which popup module displays it.
"""
import random


# Module-level cache to maintain consistent label assignments per song
# Maps "song_title||artist_name" to selected label filename
_song_label_cache = {}


def get_or_assign_label(song_title, artist_name, available_labels):
    """
    Get cached label for a song, or assign and cache a new random label.

    Args:
        song_title (str): The title of the song
        artist_name (str): The artist name
        available_labels (list): List of available label filenames to choose from

    Returns:
        str: The label filename assigned to this song
    """
    # Create unique song identifier
    song_id = f"{song_title}||{artist_name}"

    # Check cache for existing label assignment
    if song_id in _song_label_cache:
        label = _song_label_cache[song_id]
        print(f"[SHARED CACHE] Using cached label for '{song_title}': {label}")
        return label
    else:
        # First time for this song - randomly select and cache the choice
        label = random.choice(available_labels)
        _song_label_cache[song_id] = label
        print(f"[SHARED CACHE] New song '{song_title}' - assigned and cached: {label}")
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
