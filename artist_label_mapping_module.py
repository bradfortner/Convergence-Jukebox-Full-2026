"""
Artist Label Mapping Module
Loads artist-to-label assignments from RecordLabelAssignList.txt at startup

This module provides a way to assign specific record labels to specific artists
(e.g., Beach Boys always get Capitol Records) instead of random label selection.
"""
import os
import ast


# Module-level dictionary to store artist -> label mappings
_artist_label_mapping = {}


def load_artist_label_mapping(file_path="RecordLabelAssignList.txt"):
    """
    Load artist-to-label mappings from file and convert to dictionary.

    The file should contain a Python list of lists:
    [["Artist Name", "label_filename.png"], ["Another Artist", "another_label.png"], ...]

    Args:
        file_path (str): Path to the RecordLabelAssignList.txt file

    Returns:
        dict: Dictionary mapping artist names to label filenames
    """
    global _artist_label_mapping

    if not os.path.exists(file_path):
        print(f"[ARTIST MAPPING] File not found: {file_path} - using random labels for all artists")
        return {}

    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()

        # Parse the list using ast.literal_eval (safe evaluation)
        artist_list = ast.literal_eval(content)

        # Convert list of lists to dictionary
        _artist_label_mapping = {artist: label for artist, label in artist_list}

        print(f"[ARTIST MAPPING] Loaded {len(_artist_label_mapping)} artist-to-label mappings")
        for artist, label in _artist_label_mapping.items():
            print(f"  - {artist} -> {label}")

        return _artist_label_mapping

    except Exception as e:
        print(f"[ARTIST MAPPING] Error loading file: {e}")
        print(f"[ARTIST MAPPING] Using random labels for all artists")
        return {}


def get_artist_label(artist_name):
    """
    Get the assigned label for a specific artist.

    Args:
        artist_name (str): The artist name to look up

    Returns:
        str: Label filename if artist is mapped, None otherwise
    """
    # Case-insensitive lookup
    artist_lower = artist_name.lower()

    for mapped_artist, label in _artist_label_mapping.items():
        if mapped_artist.lower() == artist_lower:
            print(f"[ARTIST MAPPING] Found mapping: '{artist_name}' -> {label}")
            return label

    # No mapping found
    return None


def get_mapping_count():
    """
    Get the number of artists currently mapped.

    Returns:
        int: Number of artist-to-label mappings loaded
    """
    return len(_artist_label_mapping)


# Load mappings when module is first imported
print("[ARTIST MAPPING] Initializing artist label mappings...")
load_artist_label_mapping()
