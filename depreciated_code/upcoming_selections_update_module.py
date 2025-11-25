def update_upcoming_selections(info_screen_window, UpcomingSongPlayList):
    """
    Update the upcoming selections display with songs from the queue.

    Clears all 10 upcoming selection fields, then populates them with entries
    from the UpcomingSongPlayList if they exist. Uses a mapping of indices to
    field names to avoid repetitive code.

    Args:
        info_screen_window: The info screen PySimpleGUI window object
        UpcomingSongPlayList: List of upcoming songs to display (up to 10 items)

    Returns:
        None
    """
    # Mapping of index (0-9) to field name (one, two, three, ... ten)
    field_names = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

    # Clear all upcoming selection fields
    for field_name in field_names:
        info_screen_window[f'--upcoming_{field_name}--'].Update(' ')

    # Update upcoming selections from the playlist
    for index, field_name in enumerate(field_names):
        try:
            if UpcomingSongPlayList[index] != []:
                info_screen_window[f'--upcoming_{field_name}--'].Update('  ' + UpcomingSongPlayList[index])
        except Exception:
            info_screen_window[f'--upcoming_{field_name}--'].Update(' ')
