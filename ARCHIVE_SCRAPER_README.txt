================================================================================
Archive.org Wayback Machine MP3 Scraper - Installation & Usage Instructions
================================================================================

INSTALLATION
============

This script requires Python 3.6 or higher.

Required Libraries:
-------------------
1. requests - for HTTP requests
2. beautifulsoup4 - for HTML parsing
3. lxml - for faster HTML parsing (optional but recommended)

Installation Steps:
-------------------

Option 1: Install with pip (Recommended)
-----------------------------------------
Open Command Prompt or Terminal and run:

    pip install requests beautifulsoup4 lxml

Option 2: Install from requirements file
-----------------------------------------
If you have a requirements.txt file, run:

    pip install -r requirements.txt

Option 3: Install in a virtual environment (Advanced)
------------------------------------------------------
1. Create virtual environment:
    python -m venv venv

2. Activate it:
    Windows: venv\Scripts\activate
    Mac/Linux: source venv/bin/activate

3. Install packages:
    pip install requests beautifulsoup4 lxml

Verify Installation:
--------------------
Run this command to verify libraries are installed:

    python -c "import requests, bs4; print('All libraries installed successfully!')"

If you see the success message, you're ready to go!


USAGE
=====

Running the Scraper:
--------------------
1. Open Command Prompt or Terminal

2. Navigate to the project folder:
    cd D:\Convergence-Jukebox-Full-2026

3. Run the script:
    python 0.00.00-archive_scraper.py

What Happens:
-------------
1. The script fetches the archived page from archive.org
2. It parses the HTML to find all MP3 links
3. It shows you how many files were found
4. It asks for confirmation before downloading
5. It downloads all MP3s to the "rockabilly" folder
6. It shows progress for each download
7. It provides a summary when complete


Configuration:
--------------
You can edit these settings at the top of the script:

    WAYBACK_URL - The archive.org URL to scrape
    DOWNLOAD_FOLDER - Where to save MP3 files
    TIMEOUT - How long to wait for downloads (seconds)
    DELAY_BETWEEN_DOWNLOADS - Pause between files (be respectful!)


Troubleshooting:
----------------

Problem: "No module named 'requests'"
Solution: Run: pip install requests

Problem: "No module named 'bs4'"
Solution: Run: pip install beautifulsoup4

Problem: Script finds 0 MP3 links
Solution: The page structure may be different than expected. The MP3s might be
         loaded via JavaScript. You may need to inspect the page HTML manually.

Problem: Downloads fail with timeout errors
Solution: Increase the TIMEOUT value in the script (line 16)

Problem: Some files won't download
Solution: The original files may no longer be available on archive.org, or the
         URLs may be incorrect. Check the error messages for details.


Notes:
------
- The "rockabilly" folder is in .gitignore and won't be tracked by Git
- Already-downloaded files will be skipped automatically
- The script is respectful to archive.org with delays between downloads
- Progress is shown for each file download


SUPPORT
=======

If you encounter issues:
1. Check that all libraries are installed correctly
2. Verify you have an active internet connection
3. Try visiting the Wayback Machine URL in your browser to confirm it works
4. Check the console output for specific error messages
