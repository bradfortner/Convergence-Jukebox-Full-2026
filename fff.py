import os
import glob

try:
    from mutagen.id3 import ID3, ID3NoHeaderError
except ImportError:
    print("Error: The 'mutagen' library is required for this script.")
    print("Please install it by running: pip install mutagen")
    exit()

MUSIC_DIRECTORY = "music"
TARGET_WORD = "no"

def find_files_with_word(target_word):
    """
    Scans all MP3 files in the music directory and lists the filenames that
    contain the specified exact word in their ID3 comment tag.
    """
    music_dir_path = os.path.join(os.getcwd(), MUSIC_DIRECTORY)
    if not os.path.isdir(music_dir_path):
        print(f"Error: Music directory not found at '{music_dir_path}'")
        return

    mp3_files = glob.glob(os.path.join(music_dir_path, '*.mp3'))

    if not mp3_files:
        print(f"No .mp3 files found in the '{MUSIC_DIRECTORY}' directory.")
        return

    print(f"Scanning {len(mp3_files)} MP3 files for the exact word '{target_word}' in comments...")
    
    found_files = []

    for filepath in mp3_files:
        try:
            audio = ID3(filepath)
            comment_frame = audio.get('COMM::eng')
            
            if comment_frame:
                # Get the comment text and split it into a list of words
                comment_tags = comment_frame.text[0].lower().split()
                
                # Check if the exact target word exists in the list of tags
                if target_word in comment_tags:
                    found_files.append(os.path.basename(filepath))

        except ID3NoHeaderError:
            # Silently skip files without an ID3 header
            continue
        except Exception as e:
            print(f"Error processing file {os.path.basename(filepath)}: {e}")
            continue
    
    # --- Print the final results ---
    print("\n" + "="*80)
    if not found_files:
        print(f"No files found containing the exact word '{target_word}' in their comment tag.")
    else:
        print(f"Found {len(found_files)} file(s) containing the exact word '{target_word}':")
        print("-" * 80)
        for filename in sorted(found_files):
            print(filename)
        
    print("="*80)


if __name__ == "__main__":
    find_files_with_word(TARGET_WORD)