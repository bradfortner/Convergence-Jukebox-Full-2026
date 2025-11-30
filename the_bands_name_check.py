import os

def load_the_bands_data():
    """Load the_bands.txt and the_exempted_bands.txt

    Returns:
        tuple: (the_bands_set, exempted_bands_list)
            - the_bands_set: Set of lowercase band names that should have 'The'
            - exempted_bands_list: List of bands exempted from 'The' prefix
    """
    the_bands_set = set()
    exempted_bands_list = []

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

    # Load the_exempted_bands.txt (one band per line)
    try:
        with open('the_exempted_bands.txt', 'r', encoding='utf-8') as f:
            exempted_bands_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Warning: the_exempted_bands.txt not found - no exemptions will apply")
    except Exception as e:
        print(f"Error reading the_exempted_bands.txt: {e}")

    return the_bands_set, exempted_bands_list


def apply_the_prefix(artist_name, the_bands_set, exempted_bands_list):
    """Check if artist needs 'The' prefix

    Args:
        artist_name: Original artist name from song list
        the_bands_set: Set of band names (lowercase) that should have 'The'
        exempted_bands_list: List of bands exempted from 'The' prefix

    Returns:
        str: Modified artist name with or without 'The' prefix
    """
    if not artist_name or not the_bands_set:
        return artist_name

    # Check if artist (lowercase) is in the_bands.txt
    if artist_name.lower() in the_bands_set:
        # Add "The " prefix
        modified_artist = 'The ' + artist_name

        # Check if this modified name is in exemptions list
        if modified_artist in exempted_bands_list:
            # Exempted - return original name without "The"
            return artist_name
        else:
            # Not exempted - return name with "The"
            return modified_artist

    # Artist not in the_bands.txt - return unchanged
    return artist_name
