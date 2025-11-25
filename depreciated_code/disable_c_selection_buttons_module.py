def disable_c_selection_buttons(jukebox_selection_window, control_button_window):
    """
    Disable all buttons for the C selection window.

    Disables buttons 14-20 (7 buttons with _top and _bottom variants),
    the A and B control buttons, and all C selection input fields (C1-C7).
    Uses dynamic list generation instead of hardcoded button lists.

    Args:
        jukebox_selection_window: The jukebox selection PySimpleGUI window object
        control_button_window: The control buttons PySimpleGUI window object

    Returns:
        None
    """
    # Dynamically generate button keys for buttons 14-20 (7 buttons, top and bottom variants)
    buttons_to_disable = [f'--button{i}_{suffix}--' for i in range(14, 21) for suffix in ['top', 'bottom']]

    # Control buttons to disable (A and B for C window)
    control_buttons_to_disable = ['--A--', '--B--']

    # Dynamically generate selection windows C1-C7
    selection_windows_to_disable = [f'--C{i}--' for i in range(1, 8)]

    # Disable all buttons in the C selection window
    for button_key in buttons_to_disable:
        jukebox_selection_window[button_key].update(disabled=True)

    for control_button_key in control_buttons_to_disable:
        control_button_window[control_button_key].update(disabled=True)

    for selection_window_key in selection_windows_to_disable:
        jukebox_selection_window[selection_window_key].update(disabled=True)
