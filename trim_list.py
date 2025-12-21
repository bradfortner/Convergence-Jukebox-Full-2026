import os

# Read the file
with open('discogs_search_list.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Split by comma
entries = content.split(',')

# Find the target entry
target = "Sheila E - The Glamorous Life.mp3"
try:
    index = entries.index(target)
    print(f"Found '{target}' at position {index}")
    print(f"Total entries before trim: {len(entries)}")
    print(f"Entries to delete: {index}")
    print(f"Entries remaining: {len(entries) - index}")

    # Keep from target onwards
    new_entries = entries[index:]

    # Write back to file
    with open('discogs_search_list.txt', 'w', encoding='utf-8') as f:
        f.write(','.join(new_entries))

    print(f"Done! File updated.")

except ValueError:
    print(f"Could not find '{target}' in the file")
