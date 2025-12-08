"""
Archive.org Wayback Machine MP3 Scraper
Version: 0.00.00
Downloads MP3 files from archived web pages on the Wayback Machine
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Configuration
WAYBACK_URL = "https://web.archive.org/web/20171219205142/http://www.mp3rockabilly.com/"
DOWNLOAD_FOLDER = "rockabilly"
TIMEOUT = 30  # seconds
DELAY_BETWEEN_DOWNLOADS = 1  # seconds to be respectful to archive.org


def create_download_folder():
    """Create the download folder if it doesn't exist"""
    Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    print(f"Download folder: {os.path.abspath(DOWNLOAD_FOLDER)}")


def fetch_page(url):
    """Fetch the HTML content from the Wayback Machine"""
    print(f"\nFetching page: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        print(f"Page fetched successfully ({len(response.content)} bytes)")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None


def extract_mp3_links(html_content, base_url):
    """Parse HTML and extract all MP3 file links"""
    print("\nParsing HTML for MP3 links...")
    soup = BeautifulSoup(html_content, 'html.parser')
    mp3_links = []

    # Find all links that might contain MP3s
    # Look in <a> tags, <source> tags, <embed> tags, etc.

    # Method 1: Direct links in <a> tags
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.lower().endswith('.mp3'):
            mp3_links.append(href)

    # Method 2: Audio sources in <source> tags
    for source in soup.find_all('source', src=True):
        src = source['src']
        if src.lower().endswith('.mp3'):
            mp3_links.append(src)

    # Method 3: Audio tags with src attribute
    for audio in soup.find_all('audio', src=True):
        src = audio['src']
        if src.lower().endswith('.mp3'):
            mp3_links.append(src)

    # Method 4: Embedded players with data attributes
    for elem in soup.find_all(['embed', 'object'], src=True):
        src = elem['src']
        if src.lower().endswith('.mp3'):
            mp3_links.append(src)

    # Method 5: Search for MP3 URLs in JavaScript or inline text
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            # Find all .mp3 URLs in script content
            found_urls = re.findall(r'["\']([^"\']*\.mp3)["\']', script.string, re.IGNORECASE)
            mp3_links.extend(found_urls)

    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for link in mp3_links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)

    # Convert relative URLs to absolute URLs
    absolute_links = []
    for link in unique_links:
        # Handle Wayback Machine URLs
        if link.startswith('http'):
            absolute_url = link
        elif link.startswith('/web/'):
            # Already a Wayback Machine path
            absolute_url = 'https://web.archive.org' + link
        else:
            # Relative URL - need to construct Wayback Machine URL
            # Extract timestamp from base_url
            timestamp_match = re.search(r'/web/(\d+)/', base_url)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                original_domain = "http://www.mp3rockabilly.com/"
                absolute_url = f"https://web.archive.org/web/{timestamp}/{urljoin(original_domain, link)}"
            else:
                absolute_url = urljoin(base_url, link)

        absolute_links.append(absolute_url)

    print(f"Found {len(absolute_links)} unique MP3 links")
    return absolute_links


def sanitize_filename(url):
    """Extract and sanitize filename from URL"""
    # Get the last part of the URL path
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)

    # Remove Wayback Machine artifacts if present
    filename = re.sub(r'^\d+[a-z]*_', '', filename)  # Remove timestamp prefixes

    # Ensure it ends with .mp3
    if not filename.lower().endswith('.mp3'):
        filename += '.mp3'

    # Sanitize for Windows filesystem
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    return filename


def download_mp3(url, folder, index, total):
    """Download a single MP3 file"""
    filename = sanitize_filename(url)
    filepath = os.path.join(folder, filename)

    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"[{index}/{total}] SKIP: {filename} (already exists)")
        return True

    print(f"[{index}/{total}] Downloading: {filename}")
    print(f"    URL: {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
        response.raise_for_status()

        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))

        # Download with progress
        downloaded = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r    Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')

        print(f"\n    SUCCESS: {filename} ({downloaded} bytes)")
        return True

    except requests.exceptions.RequestException as e:
        print(f"\n    ERROR: Failed to download {filename}")
        print(f"    Reason: {e}")
        # Remove partial file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return False


def main():
    """Main scraper function"""
    print("=" * 70)
    print("Archive.org Wayback Machine MP3 Scraper v0.00.00")
    print("=" * 70)

    # Create download folder
    create_download_folder()

    # Fetch the archived page
    html_content = fetch_page(WAYBACK_URL)
    if not html_content:
        print("\nFailed to fetch page. Exiting.")
        return

    # Extract MP3 links
    mp3_links = extract_mp3_links(html_content, WAYBACK_URL)

    if not mp3_links:
        print("\nNo MP3 links found on the page.")
        print("This could mean:")
        print("  1. The MP3s are loaded dynamically via JavaScript")
        print("  2. The links are obfuscated or embedded differently")
        print("  3. The page structure is different than expected")
        print("\nTry visiting the page manually and inspecting the HTML source.")
        return

    # Display links found
    print("\n" + "=" * 70)
    print("MP3 Links Found:")
    print("=" * 70)
    for i, link in enumerate(mp3_links[:10], 1):  # Show first 10
        print(f"{i}. {link}")
    if len(mp3_links) > 10:
        print(f"... and {len(mp3_links) - 10} more")

    # Ask for confirmation
    print("\n" + "=" * 70)
    response = input(f"\nProceed with downloading {len(mp3_links)} files? (y/n): ")
    if response.lower() != 'y':
        print("Download cancelled.")
        return

    # Download all MP3s
    print("\n" + "=" * 70)
    print("Starting Downloads...")
    print("=" * 70)

    success_count = 0
    fail_count = 0

    for i, link in enumerate(mp3_links, 1):
        if download_mp3(link, DOWNLOAD_FOLDER, i, len(mp3_links)):
            success_count += 1
        else:
            fail_count += 1

        # Respectful delay between downloads
        if i < len(mp3_links):
            time.sleep(DELAY_BETWEEN_DOWNLOADS)

    # Summary
    print("\n" + "=" * 70)
    print("Download Complete!")
    print("=" * 70)
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {len(mp3_links)}")
    print(f"\nFiles saved to: {os.path.abspath(DOWNLOAD_FOLDER)}")


if __name__ == "__main__":
    main()
