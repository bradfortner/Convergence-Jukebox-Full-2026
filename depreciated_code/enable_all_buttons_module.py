def enable_all_buttons(jukebox_selection_window, control_button_window):
    """
    Enable all buttons in the jukebox selection interface.

    Enables all 21 song selection buttons (0-20) with both _top and _bottom variants,
    all control buttons (A, B, C), and all selection input fields (A1-A7, B1-B7, C1-C7).
    Uses dynamic list generation instead of hardcoded button lists.

    Args:
        jukebox_selection_window: The jukebox selection PySimpleGUI window object
        control_button_window: The control buttons PySimpleGUI window object

    Returns:
        None
    """
    # Dynamically generate button keys for buttons 0-20 (21 buttons, top and bottom variants)
    buttons_to_enable = [f'--button{i}_{suffix}--' for i in range(21) for suffix in ['top', 'bottom']]

    # Control buttons to enable (A, B, and C)
    control_buttons_to_enable = ['--A--', '--B--', '--C--']

    # Dynamically generate selection windows A1-A7, B1-B7, C1-C7
    selection_windows_to_enable = [f'--{letter}{i}--' for letter in ['A', 'B', 'C'] for i in range(1, 8)]

    # Enable all buttons in the selection window
    for button_key in buttons_to_enable:
        jukebox_selection_window[button_key].update(disabled=False)

    for control_button_key in control_buttons_to_enable:
        control_button_window[control_button_key].update(disabled=False)

    for selection_window_key in selection_windows_to_enable:
        jukebox_selection_window[selection_window_key].update(disabled=False)
