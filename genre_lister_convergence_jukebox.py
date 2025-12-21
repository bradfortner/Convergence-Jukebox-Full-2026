"""
This script maintains and standardizes genre tags in the Convergence Jukebox music collection.
It requires the 'mutagen' library and the 'MusicMasterSongList.txt' file.

Functions:
1. find_and_correct_genre: Scans for specific incorrect genre keywords, prompts the user 
   for correction, and updates both the ID3 tags of the physical files and the master JSON list.
2. print_final_genre_list: Reads the updated master list and prints a sorted summary of 
   all unique genres currently present in the collection.
"""

import json
import os

try:
    from mutagen.id3 import ID3, COMM
except ImportError:
    print("Error: The 'mutagen' library is required.")
    print("Please install it by running: pip install mutagen")
    exit()

SONG_LIST_PATH = "MusicMasterSongList.txt"

def find_and_correct_genre(song_list, wrong_genre, correct_genre):
    """
    Finds songs with a specific incorrect genre, prompts the user to correct them
    in both the ID3 tags and the in-memory song list.

    Returns the (potentially modified) song list and a boolean indicating if
    any changes were made.
    """
    songs_to_fix = [
        song for song in song_list
        if wrong_genre in song.get('comment', '').split()
    ]

    if not songs_to_fix:
        print(f"No files found with the genre '{wrong_genre}'.")
        return song_list, False

    print("-" * 80)
    print(f"Found {len(songs_to_fix)} file(s) with the genre '{wrong_genre}':")
    for song in songs_to_fix:
        print(f"  - {song.get('location', 'Unknown Location')}")
    print("-" * 80)

    choice = input(f"Would you like to change '{wrong_genre}' to '{correct_genre}' in these files? (y/n): ").lower()
    print()

    if choice != 'y':
        print("Skipping modification.\n")
        return song_list, False

    modified_count = 0
    for song_data in songs_to_fix:
        filepath = song_data.get('location')
        if not filepath or not os.path.exists(filepath):
            print(f"Warning: Skipping non-existent file: {filepath}")
            continue
        try:
            audio = ID3(filepath)
            comment_text = audio.get('COMM::eng', COMM(encoding=3, lang='eng', desc='', text=[''])).text[0]
            tags = comment_text.split()
            
            tags = [correct_genre if tag == wrong_genre else tag for tag in tags]
            
            new_comment = " ".join(tags)
            audio['COMM::eng'] = COMM(encoding=3, lang='eng', desc='', text=[new_comment])
            audio.save()

            song_data['comment'] = new_comment
            print(f"Successfully updated: {os.path.basename(filepath)}")
            modified_count += 1
        except Exception as e:
            print(f"ERROR updating file {os.path.basename(filepath)}: {e}")

    print(f"Completed: {modified_count} file(s) updated.\n")
    return song_list, modified_count > 0

def print_final_genre_list():
    """
    Reads the master song list directly from the file and prints a final
    summary of all unique genres.
    """
    print("Reading file to generate final genre summary...")
    
    try:
        with open(SONG_LIST_PATH, 'r', encoding='utf-8') as f:
            song_list = json.load(f)
    except Exception as e:
        print(f"Could not read or parse '{SONG_LIST_PATH}' for final summary: {e}")
        return

    all_genres = set()
    for song in song_list:
        comment = song.get('comment', '')
        if comment:
            genre_tags = comment.split()
            for tag in genre_tags:
                cleaned_tag = tag.strip()
                if cleaned_tag:
                    all_genres.add(cleaned_tag)
    
    if all_genres:
        print("-" * 50)
        print("Final List of All Unique Genres:")
        print("-" * 50)
        for genre in sorted(list(all_genres)):
            print(genre)
        print("-" * 50)
        print(f"Total unique genres: {len(all_genres)}")

if __name__ == "__main__":
    if not os.path.exists(SONG_LIST_PATH):
        print(f"FATAL ERROR: Song list file not found at '{SONG_LIST_PATH}'")
        exit()

    try:
        with open(SONG_LIST_PATH, 'r', encoding='utf-8') as f:
            master_song_list = json.load(f)
    except Exception as e:
        print(f"FATAL ERROR: Could not read or parse '{SONG_LIST_PATH}': {e}")
        exit()

    master_song_list, changes1 = find_and_correct_genre(master_song_list, "boomgrafitti", "boominstrumentals")
    master_song_list, changes2 = find_and_correct_genre(master_song_list, "boomgraff", "boominstrumentals")
    master_song_list, changes3 = find_and_correct_genre(master_song_list, "boominstrumental", "boominstrumentals")
    master_song_list, changes4 = find_and_correct_genre(master_song_list, "boominstumental", "boominstrumentals")
    master_song_list, changes5 = find_and_correct_genre(master_song_list, "boominstumentals", "boominstrumentals")
    master_song_list, changes6 = find_and_correct_genre(master_song_list, "instrumental", "boominstrumentals")
    master_song_list, changes7 = find_and_correct_genre(master_song_list, "cdn", "canadian")
    master_song_list, changes8 = find_and_correct_genre(master_song_list, "clasiccountry", "classiccountry")
    master_song_list, changes9 = find_and_correct_genre(master_song_list, "clasicrock", "classicrock")
    master_song_list, changes10 = find_and_correct_genre(master_song_list, "folk", "folkera")
    master_song_list, changes11 = find_and_correct_genre(master_song_list, "modenrock", "modernrock")
    master_song_list, changes12 = find_and_correct_genre(master_song_list, "modernrpop", "modernpop")
    master_song_list, changes13 = find_and_correct_genre(master_song_list, "norandon", "norandom")
    master_song_list, changes14 = find_and_correct_genre(master_song_list, "showtune", "showtunes")
    master_song_list, changes15 = find_and_correct_genre(master_song_list, "swing", "swingera")
    master_song_list, changes16 = find_and_correct_genre(master_song_list, "no", "noimage")

    if changes1 or changes2 or changes3 or changes4 or changes5 or changes6 or changes7 or changes8 or changes9 or changes10 or changes11 or changes12 or changes13 or changes14 or changes15 or changes16:
        try:
            with open(SONG_LIST_PATH, 'w', encoding='utf-8') as f:
                json.dump(master_song_list, f, indent=4)
            print(f"Successfully saved all changes to '{SONG_LIST_PATH}'.")
        except Exception as e:
            print(f"\nERROR writing final updates to '{SONG_LIST_PATH}': {e}")
    
    print("\n-------------------------------------------------")
    print("All modifications and checks complete.")
    
    print_final_genre_list()
