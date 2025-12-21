import os
import datetime
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError

def check_for_title_mismatch(since_date_str="2025-11-30"):
    music_dir = "music"

    try:
        since_date = datetime.datetime.strptime(since_date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format for 'since_date_str'. Expected YYYY-MM-DD. Got {since_date_str}")
        return

    if not os.path.exists(music_dir):
        print(f"Error: Directory '{music_dir}' not found.")
        return

    filenames = [f for f in os.listdir(music_dir) if os.path.isfile(os.path.join(music_dir, f)) and f.lower().endswith('.mp3')]
    
    if not filenames:
        print(f"No MP3 files found in directory '{music_dir}'.")
        return

    print(f"Scanning for title mismatches in '{music_dir}' for files modified after {since_date.strftime('%Y-%m-%d')}...")
    
    mismatches_found = 0

    for filename in filenames:
        try:
            filepath = os.path.join(music_dir, filename)

            # Check modification date
            mtime_timestamp = os.path.getmtime(filepath)
            mtime_datetime = datetime.datetime.fromtimestamp(mtime_timestamp)

            if mtime_datetime <= since_date:
                continue

            # --- Proceed with mismatch check only if file is recent enough ---

            # Extract title from filename
            parts = filename.rsplit(' - ', 1)
            filename_title = ""
            if len(parts) == 2:
                title_with_ext = parts[1]
                if title_with_ext.lower().endswith('.mp3'):
                    filename_title = title_with_ext[:-4].strip()

            if not filename_title:
                # This file is recent, so we should mention we couldn't parse it.
                print(f"\nCould not parse title from recent file: {filename}")
                continue

            # Extract title from ID3 tag
            id3_title = ""
            try:
                audio = EasyID3(filepath)
                if 'title' in audio:
                    id3_title = audio['title'][0].strip()
            except ID3NoHeaderError:
                print(f"\nNo ID3 header found for recent file: {filename}")
                continue
            except Exception as e:
                print(f"\nError reading ID3 tags for recent file {filename}: {e}")
                continue

            # Compare titles
            if filename_title.lower() != id3_title.lower():
                mismatches_found += 1
                print("\n--- Mismatch Found! ---")
                print(f"File:     {filename}")
                print(f"Modified: {mtime_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Filename Title: '{filename_title}'")
                print(f"ID3 Title:      '{id3_title}'")
                print("-----------------------")
                
                choice = input("Update ID3 title with filename title? (y/n): ").lower()
                if choice == 'y':
                    try:
                        audio = EasyID3(filepath)
                        audio['title'] = filename_title
                        audio.save()
                        print(f"ID3 title for '{filename}' updated successfully.")
                    except Exception as e:
                        print(f"Error updating ID3 tag for {filename}: {e}")
                else:
                    print("Skipping...")

        except OSError as e:
            print(f"Error accessing file '{filename}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred with file {filename}: {e}")
            continue
    
    if mismatches_found == 0:
        print("\nScan complete. No mismatches found in files modified after the specified date.")
    else:
        print("\nScan complete.")


if __name__ == "__main__":
    check_for_title_mismatch()
