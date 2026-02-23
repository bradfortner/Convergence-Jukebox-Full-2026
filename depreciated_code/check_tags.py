
import mutagen
import os

files_to_check = [
    r"music\Britney Spears - My Only Wish This Year.mp3",
    r"music\Julie London - Warm December.mp3"
]

for file_path in files_to_check:
    print(f"\nChecking: {file_path}")
    if not os.path.exists(file_path):
        print("File not found!")
        continue
        
    try:
        audio = mutagen.File(file_path)
        if audio:
            print("Keys found:", audio.keys())
            
            comment = ''
            if 'COMM::eng' in audio:
                comment = str(audio['COMM::eng'])
                print(f"COMM::eng found: '{comment}'")
            elif 'COMM' in audio:
                comment = str(audio['COMM'])
                print(f"COMM found: '{comment}'")
            else:
                # Check for other COMM keys (e.g., COMM::XXX)
                comm_keys = [k for k in audio.keys() if k.startswith('COMM')]
                if comm_keys:
                    for k in comm_keys:
                        print(f"{k} found: '{audio[k]}'" )
                else:
                    print("No COMM tags found.")
            
            if 'christmas' in comment.lower():
                print("SUCCESS: 'christmas' found in comment.")
            else:
                print("FAILURE: 'christmas' NOT found in comment.")
        else:
            print("Mutagen could not load file.")
    except Exception as e:
        print(f"Error: {e}")
