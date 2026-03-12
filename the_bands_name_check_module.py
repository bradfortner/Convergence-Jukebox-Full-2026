import os

def load_the_bands_data() -> set[str]:
    """Load the_bands.txt

    Returns:
        set: the_bands_set: Set of lowercase band names that should have 'The'
    """
    the_bands_set = set()

    # Load the_bands.txt (comma-separated lowercase band names)
    try:
        with open('the_bands.txt', 'r', encoding='utf-8') as f:
            content = f.read().lower()
            # Split by comma and strip whitespace
            the_bands_set = set(name.strip() for name in content.split(',') if name.strip())
    except FileNotFoundError:
        print("Warning: the_bands.txt not found - 'The' prefix feature disabled")
    except Exception as e:
        print(f"Error reading the_bands.txt: {e}")

    return the_bands_set


def apply_the_prefix(artist_name: str, the_bands_set: set[str]) -> str:
    """Check if artist needs 'The' prefix

    Args:
        artist_name: Original artist name from song list
        the_bands_set: Set of band names (lowercase) that should have 'The'

    Returns:
        str: Modified artist name with or without 'The' prefix
    """
    if not artist_name or not the_bands_set:
        return artist_name

    # Check if artist (lowercase) is in the_bands.txt
    if artist_name.lower() in the_bands_set:
        # Add "The " prefix
        return 'The ' + artist_name

    # Artist not in the_bands.txt - return unchanged
    return artist_name