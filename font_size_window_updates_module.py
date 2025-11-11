def reset_button_fonts(jukebox_selection_window, font_size_window_updates):
    """
    Reset all selection button fonts to standard size (Helvetica 12 bold).

    Args:
        jukebox_selection_window: The selection window object
        font_size_window_updates: List of button element keys to update
    """
    for font_size_window in font_size_window_updates:
        jukebox_selection_window[font_size_window].Widget.config(font='Helvetica 12 bold')


def update_selection_button_text(jukebox_selection_window, MusicMasterSongList, selection_window_number):
    """
    Update all 21 selection buttons with song titles and artists from the master song list.

    This function loops through buttons 0-20, updating both the title (top) and
    artist (bottom) text for each button based on the selection window offset.

    Args:
        jukebox_selection_window: The selection window object
        MusicMasterSongList: The master list of songs with title and artist data
        selection_window_number: The starting index in the master list for this window
    """
    for button_index in range(21):
        offset = selection_window_number + button_index
        jukebox_selection_window[f'--button{button_index}_top--'].update(text=MusicMasterSongList[offset]['title'])
        jukebox_selection_window[f'--button{button_index}_bottom--'].update(text=MusicMasterSongList[offset]['artist'])


def adjust_button_fonts_by_length(jukebox_selection_window, font_size_window_updates):
    """
    Adjust button fonts based on text length to ensure readability.

    Font sizes are determined by text length:
    - >= 28 characters: Helvetica 8 bold
    - 22-27 characters: Helvetica 10 bold
    - < 22 characters: Helvetica 12 bold (already set by reset_button_fonts)

    Args:
        jukebox_selection_window: The selection window object
        font_size_window_updates: List of button element keys to check and update
    """
    for font_size_window in font_size_window_updates:
        font_length_string = jukebox_selection_window[font_size_window].get_text()
        if len(font_length_string) >= 28:
            jukebox_selection_window[font_size_window].Widget.config(font='Helvetica 8 bold')
        elif len(font_length_string) > 21 and len(font_length_string) < 28:
            jukebox_selection_window[font_size_window].Widget.config(font='Helvetica 10 bold')


def create_font_size_window_updates():
    """
    Generate the list of all button element keys for font size updates.

    Creates a list of 42 keys representing the 21 song selection buttons (0-20),
    each with '_top' (song title) and '_bottom' (artist) variants. This dynamic
    generation replaces the need for manually listing all keys.

    Returns:
        list: Keys for all button elements in the format '--buttonN_[top|bottom]--'
              where N ranges from 0 to 20.

    Example:
        >>> keys = create_font_size_window_updates()
        >>> len(keys)
        42
        >>> keys[0]
        '--button0_top--'
        >>> keys[1]
        '--button0_bottom--'
    """
    return [f'--button{i}_{suffix}--' for i in range(21) for suffix in ['top', 'bottom']]
