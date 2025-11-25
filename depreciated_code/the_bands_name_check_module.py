import os

def the_bands_name_check(jukebox_selection_window, dir_path, band_names_exemptions):
    """
    Check band names and add 'The' prefix where appropriate.

    Processes all 21 selection button artist fields, checking if the artist name
    exists in the_bands.txt file and applying exemptions from the_exempted_bands.txt.
    Dynamically generates the list of buttons instead of hardcoding.

    Args:
        jukebox_selection_window: The jukebox selection PySimpleGUI window object
        dir_path: Directory path containing the_bands.txt and the_exempted_bands.txt
        band_names_exemptions: Function to apply band name exemption rules

    Returns:
        None
    """
    # Dynamically generate list of button keys for all 21 selection buttons (artist fields)
    jukebox_selection_windows_to_update = [f'--button{i}_bottom--' for i in range(21)]

    # Read band files once (using os.path.join for platform compatibility)
    try:
        with open(os.path.join(dir_path, 'the_bands.txt'), 'r') as f:
            the_bands = f.read()
        with open(os.path.join(dir_path, 'the_exempted_bands.txt'), 'r') as f:
            exempted_bands = [line.strip() for line in f]
    except FileNotFoundError:
        return

    # Process all selection windows
    for jukebox_selection_windows in jukebox_selection_windows_to_update:
        band_to_check = jukebox_selection_window[jukebox_selection_windows].get_text()

        if band_to_check.lower() in the_bands:
            the_band_to_update = 'The ' + band_to_check
            the_band_to_update = band_names_exemptions(the_band_to_update, exempted_bands, band_to_check)
            print(the_band_to_update)

            if len(the_band_to_update) > 22:
                jukebox_selection_window[jukebox_selection_windows].Widget.config(font='Helvetica 10 bold')
            else:
                jukebox_selection_window[jukebox_selection_windows].update(the_band_to_update)
