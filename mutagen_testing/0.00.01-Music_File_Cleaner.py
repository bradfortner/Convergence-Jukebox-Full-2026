#!/usr/bin/env python3
"""
A script for cleaning music file metadata using mutagen.
"""
import os
from mutagen.easyid3 import EasyID3
import discogs_client
import config

# Initialize Discogs client
# The user token is now imported from config.py
d = discogs_client.Client('YourApp/1.0', user_token=config.DISCOGS_USER_TOKEN)

def search_discogs(query, search_type='release'):
    """
    Searches the Discogs database for releases, artists, or masters.
    """
    print(f"\nSearching Discogs for '{query}' (type: {search_type})...")
    try:
        results = d.search(query, type=search_type)
        if results:
            print(f"Found {results.count} results. Showing the first 5:")
            for i, result in enumerate(results.page(1)):
                if i >= 5:
                    break
                print(f"  Result {i+1}:")
                if isinstance(result, discogs_client.models.Release):
                    print(f"    Title: {result.title}")
                    print(f"    Artist: {result.artists[0].name if result.artists else 'N/A'}")
                    print(f"    Year: {result.year}")
                    print(f"    Labels: {', '.join([l.name for l in result.labels])}")
                elif isinstance(result, discogs_client.models.Artist):
                    print(f"    Name: {result.name}")
                elif isinstance(result, discogs_client.models.Master):
                    print(f"    Title: {result.title}")
                    print(f"    Artist: {result.artists[0].name if result.artists else 'N/A'}")
                    print(f"    Year: {result.year}")
        else:
            print(f"  No {search_type} results found for '{query}'.")
    except Exception as e:
        print(f"Error searching Discogs: {e}")

def clean_music_file(file_path):
    """
    Cleans the metadata of a music file.
    """
    try:
        audio = EasyID3(file_path)
        print(f"Cleaning {file_path}...")
        print(f"Artist: {audio.get('artist')}")
        print(f"Title: {audio.get('title')}")
        print(f"Album: {audio.get('album')}")

        # Example of how to change a tag
        # audio['artist'] = 'New Artist'
        # audio.save()

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    """
    The main function of the script.
    """
    print("Music File Cleaner")
    
    # Example usage:
    # clean_music_file("path/to/your/music.mp3")

    # Example Discogs search:
    search_discogs("Pink Floyd - The Dark Side of the Moon", search_type='release')


if __name__ == "__main__":
    main()
