def disable_a_selection_buttons(jukebox_selection_window, control_button_window):
    """
    Disable all buttons for the A selection window.

    Disables the first 7 song selection buttons (0-6), the B and C control buttons,
    and all A selection input fields (A1-A7). Uses dynamic list generation instead
    of hardcoded button lists.

    Args:
        jukebox_selection_window: The jukebox selection PySimpleGUI window object
        control_button_window: The control buttons PySimpleGUI window object

    Returns:
        None
    """
    # Dynamically generate button keys for buttons 0-6 (7 buttons, top and bottom variants)
    buttons_to_disable = [f'--button{i}_{suffix}--' for i in range(7) for suffix in ['top', 'bottom']]
    
    # Control buttons to disable (B and C for A window)
    control_buttons_to_disable = ['--B--', '--C--']
    
    # Dynamically generate selection windows A1-A7
    selection_windows_to_disable = [f'--A{i}--' for i in range(1, 8)]
    
    # Disable all buttons in the A selection window
    for button_key in buttons_to_disable:
        jukebox_selection_window[button_key].update(disabled=True)
    
    for control_button_key in control_buttons_to_disable:
        control_button_window[control_button_key].update(disabled=True)
    
    for selection_window_key in selection_windows_to_disable:
        jukebox_selection_window[selection_window_key].update(disabled=True)
