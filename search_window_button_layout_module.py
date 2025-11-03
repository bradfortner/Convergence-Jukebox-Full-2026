import FreeSimpleGUI as sg


def _create_spacer_text(width=55):
    """Helper to create spacer text elements."""
    return sg.Text("", font="Helvetica 8", s=(width, 1), background_color="black")


def _create_letter_button(label, key=None):
    """Helper to create letter/number buttons."""
    return sg.Button(label, focus=False, s=(1, 1), border_width=6, key=key)


def _create_result_display(result_num):
    """Helper to create result display buttons."""
    return sg.Button("", s=(34, 1), visible=False, border_width=6,
                     button_color=["white", "black"], k=f"--result_{result_num}--",
                     disabled_button_color="black")


def create_search_window_button_layout():
    """
    Creates the search window button layout for the jukebox GUI.

    Returns:
        A PySimpleGUI layout list for the search window
    """

    # Row 1: Logo
    row1 = [
        _create_spacer_text(55),
        sg.Button("", s=(1, 1), disabled=True, image_size=(439, 226),
                  image_filename="images/jukebox_2025_logo.png",
                  button_color=["black", "white"], font="Helvetica 16 bold"),
    ]

    # Row 2: Top spacer
    row2 = [_create_spacer_text(30)]

    # Row 3: Search type header
    row3 = [
        _create_spacer_text(38),
        sg.Text("Search For Title", p=None, font="Helvetica 16 bold",
                background_color="white", text_color="black", k="--search_type--"),
        sg.Button("", s=(1, 1), disabled=True, image_size=(25, 25),
                  image_filename="images/magglass.png",
                  button_color=["black", "white"], font="Helvetica 16 bold"),
        sg.Text("", font="Helvetica 16 bold", k="--letter_entry--", s=(35, 1),
                background_color="white", text_color="black"),
        _create_spacer_text(30),
    ]

    # Row 4: Spacer
    row4 = [_create_spacer_text(60)]

    # Row 5: Number buttons (1-9, 0, -)
    row5 = [
        _create_spacer_text(14),
        _create_letter_button("1"),
        _create_letter_button("2"),
        _create_letter_button("3"),
        _create_letter_button("4"),
        _create_letter_button("5"),
        _create_letter_button("6"),
        _create_letter_button("7"),
        _create_letter_button("8"),
        _create_letter_button("9"),
        _create_letter_button("0"),
        _create_letter_button("-"),
        _create_spacer_text(2),
        _create_result_display("one"),
    ]

    # Row 6: Letter buttons A-K
    row6 = [
        _create_spacer_text(14),
        _create_letter_button("A", key="--A--"),  # First letter highlighted
        _create_letter_button("B"),
        _create_letter_button("C"),
        _create_letter_button("D"),
        _create_letter_button("E"),
        _create_letter_button("F"),
        _create_letter_button("G"),
        _create_letter_button("H"),
        _create_letter_button("I"),
        _create_letter_button("J"),
        _create_letter_button("K"),
        _create_spacer_text(2),
        _create_result_display("two"),
    ]

    # Apply special formatting to A button
    # (Note: This is handled by post-processing in the main file)

    # Row 7: Letter buttons L-V
    row7 = [
        _create_spacer_text(14),
        _create_letter_button("L"),
        _create_letter_button("M"),
        _create_letter_button("N"),
        _create_letter_button("O"),
        _create_letter_button("P"),
        _create_letter_button("Q"),
        _create_letter_button("R"),
        _create_letter_button("S"),
        _create_letter_button("T"),
        _create_letter_button("U"),
        _create_letter_button("V"),
        _create_spacer_text(2),
        _create_result_display("three"),
    ]

    # Row 8: Letter buttons W-Z, ', DELETE
    row8 = [
        _create_spacer_text(14),
        _create_letter_button("W"),
        _create_letter_button("X"),
        _create_letter_button("Y"),
        _create_letter_button("Z"),
        _create_letter_button("'"),
        sg.Button("DELETE LAST ENTRY", k="--DELETE--", s=(17, 1), border_width=6),
        _create_spacer_text(2),
        _create_result_display("four"),
    ]

    # Row 9: Function buttons SPACE, CLEAR, EXIT
    row9 = [
        _create_spacer_text(14),
        sg.Button("SPACE", k="--space--", s=(9, 1), border_width=6),
        sg.Button("CLEAR", k="--CLEAR--", s=(9, 1), border_width=6),
        sg.Button("EXIT", k="--EXIT--", s=(10, 1), border_width=6),
        _create_spacer_text(1),
        _create_result_display("five"),
    ]

    return [row1, row2, row3, row4, row5, row6, row7, row8, row9]
