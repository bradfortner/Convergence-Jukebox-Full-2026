import FreeSimpleGUI as sg


def _create_button(key, size, image_name, dir_path, disabled=False):
    """Helper function to create buttons with common properties."""
    return sg.Button(
        size=size,
        image_size=size,
        key=key,
        pad=(0, 0),
        border_width=0,
        font='Helvetica 38',
        image_filename=dir_path + '/images/' + image_name + '_button.png',
        disabled=disabled
    )


def create_control_button_screen_layout(dir_path):
    """
    Creates the control button screen layout for the jukebox GUI.

    Args:
        dir_path: The directory path for image files

    Returns:
        A PySimpleGUI layout list for the control button screen
    """

    # Helper to create blank buttons
    def blank_btn(size):
        return _create_button('--blank--', size, 'blank', dir_path)

    # Helper to create numbered buttons (1-7)
    def num_btn(num):
        return _create_button(f'--{num}--', (50, 50), str(num), dir_path, disabled=True)

    # Row 1: Blank, blank buttons (5x), then A, B, C, 1, 2
    row1 = [
        blank_btn((35, 25)),
        blank_btn((50, 50)),
        blank_btn((50, 50)),
        blank_btn((50, 50)),
        blank_btn((50, 50)),
        _create_button('--A--', (50, 50), 'a', dir_path),
        _create_button('--B--', (50, 50), 'b', dir_path),
        _create_button('--C--', (50, 50), 'c', dir_path),
        num_btn(1),
        num_btn(2),
    ]

    # Row 2: Blank, correct button (centered), blank, 3-7, blank, select button
    row2 = [
        blank_btn((50, 25)),
        _create_button('--correct--', (150, 50), 'correct', dir_path),
        blank_btn((35, 25)),
        num_btn(3),
        num_btn(4),
        num_btn(5),
        num_btn(6),
        num_btn(7),
        blank_btn((35, 25)),
        _create_button('--select--', (150, 50), 'select', dir_path, disabled=True),
    ]

    return [row1, row2]
