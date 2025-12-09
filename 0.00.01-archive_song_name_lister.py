"""
Archive.org Song Name List Generator
Version: 0.00.01
Generates a Python list of song data from archived web page

Changes in v0.00.01:
- Processes ALL songs (removed 5 record limit)
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configuration
WAYBACK_URL = "https://web.archive.org/web/20171219205142/http://www.mp3rockabilly.com/"
OUTPUT_FILE = "rockabilly_song_list.py"
TIMEOUT = 30


def fetch_page(url):
    """Fetch the HTML content from the Wayback Machine"""
    print(f"Fetching page: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        print(f"Page fetched successfully ({len(response.content)} bytes)\n")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None


def extract_mp3_filename(url):
    """Extract just the filename from MP3 URL"""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    return filename


def swap_song_format(original_name):
    """
    Swap artist and title around the hyphen
    Input: "Song Title - Artist Name"
    Output: "Artist Name - Song Title"
    """
    # Split on ' - ' (note the spaces)
    if ' - ' in original_name:
        parts = original_name.split(' - ', 1)  # Split only on first occurrence
        if len(parts) == 2:
            song_title = parts[0].strip()
            artist_name = parts[1].strip()
            return f"{artist_name} - {song_title}"

    # If no hyphen or pattern doesn't match, return as-is
    return original_name


def extract_song_data(html_content):
    """Parse HTML and extract song data"""
    print("Parsing HTML for song data...")
    soup = BeautifulSoup(html_content, 'html.parser')

    song_list = []

    # Find all links with MP3 files
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.lower().endswith('.mp3'):
            original_name = link.get_text(strip=True)
            mp3_filename = extract_mp3_filename(href)
            swapped_name = swap_song_format(original_name)

            song_list.append((original_name, mp3_filename, swapped_name))

    print(f"Found {len(song_list)} songs total")
    return song_list


def generate_output_file(song_list, filename):
    """Generate a Python file with the song list"""
    print(f"\nGenerating output file: {filename}")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('Rockabilly Song List\n')
        f.write('Generated from: https://web.archive.org/web/20171219205142/http://www.mp3rockabilly.com/\n')
        f.write('\n')
        f.write('Structure: List of tuples\n')
        f.write('Each tuple: (original_name, mp3_filename, swapped_name)\n')
        f.write('  - original_name: Song as displayed on page\n')
        f.write('  - mp3_filename: MP3 file name only\n')
        f.write('  - swapped_name: Artist - Song Title (swapped format)\n')
        f.write('"""\n\n')
        f.write('songs = [\n')

        for i, (orig, mp3, swapped) in enumerate(song_list):
            # Escape any quotes in the strings
            orig_escaped = orig.replace('"', '\\"')
            mp3_escaped = mp3.replace('"', '\\"')
            swapped_escaped = swapped.replace('"', '\\"')

            f.write(f'    ("{orig_escaped}", "{mp3_escaped}", "{swapped_escaped}")')

            if i < len(song_list) - 1:
                f.write(',\n')
            else:
                f.write('\n')

        f.write(']\n')

    print(f"Output file created: {os.path.abspath(filename)}")
    print(f"Total records written: {len(song_list)}")


def main():
    """Main function"""
    print("=" * 70)
    print("Archive.org Song Name List Generator v0.00.01")
    print("=" * 70)
    print("Processing ALL songs from the page")
    print("=" * 70)
    print()

    # Fetch the page
    html_content = fetch_page(WAYBACK_URL)
    if not html_content:
        print("Failed to fetch page. Exiting.")
        return

    # Extract song data
    all_songs = extract_song_data(html_content)

    if not all_songs:
        print("No songs found!")
        return

    print(f"\nProcessing all {len(all_songs)} records...")

    # Show first 5 and last 5 as preview
    print("\n" + "=" * 70)
    print("First 5 records:")
    print("=" * 70)
    for i, (orig, mp3, swapped) in enumerate(all_songs[:5], 1):
        print(f"{i}. {orig}")
        print(f"   MP3: {mp3}")
        print(f"   Swapped: {swapped}")
        print()

    print("=" * 70)
    print("Last 5 records:")
    print("=" * 70)
    for i, (orig, mp3, swapped) in enumerate(all_songs[-5:], len(all_songs)-4):
        print(f"{i}. {orig}")
        print(f"   MP3: {mp3}")
        print(f"   Swapped: {swapped}")
        print()

    # Generate output file
    print("=" * 70)
    generate_output_file(all_songs, OUTPUT_FILE)

    print("\n" + "=" * 70)
    print("Complete!")
    print("=" * 70)
    print(f"\nGenerated list with {len(all_songs)} songs in '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
