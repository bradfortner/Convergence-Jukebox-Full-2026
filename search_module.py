"""
Search Module for Convergence Jukebox
Provides title and artist search functionality
"""

import FreeSimpleGUI as sg
import time
from search_window_button_layout_module import create_search_window_button_layout


def run_search(search_type, MusicMasterSongList, all_artists_list, main_windows, callback_functions):
    """
    Run the search interface for title or artist search.

    Args:
        search_type (str): "title" or "artist"
        MusicMasterSongList (list): The master list of all songs
        all_artists_list (list): List of unique artist names
        main_windows (dict): Dictionary containing all main jukebox windows:
            - 'right_arrow_selection_window'
            - 'left_arrow_selection_window'
            - 'jukebox_selection_window'
            - 'info_screen_window'
            - 'control_button_window'
            - 'song_playing_lookup_window'
            - 'window_background'
        callback_functions (dict): Dictionary containing callback functions:
            - 'selection_buttons_update'
            - 'disable_a_selection_buttons'
            - 'disable_b_selection_buttons'
            - 'disable_c_selection_buttons'

    Returns:
        dict: {'song_number': int, 'song_selected': str} if song selected
        None: if user cancelled (ESC or EXIT)
    """
    # Extract windows from dict
    right_arrow_selection_window = main_windows['right_arrow_selection_window']
    left_arrow_selection_window = main_windows['left_arrow_selection_window']
    jukebox_selection_window = main_windows['jukebox_selection_window']
    info_screen_window = main_windows['info_screen_window']
    control_button_window = main_windows['control_button_window']
    song_playing_lookup_window = main_windows['song_playing_lookup_window']
    window_background = main_windows['window_background']

    # Extract callback functions
    selection_buttons_update = callback_functions['selection_buttons_update']
    disable_a_selection_buttons = callback_functions['disable_a_selection_buttons']
    disable_b_selection_buttons = callback_functions['disable_b_selection_buttons']
    disable_c_selection_buttons = callback_functions['disable_c_selection_buttons']

    # Track search flag for logic branching
    search_flag = search_type

    # Hide jukebox interface and bring up title search interface
    right_arrow_selection_window.Hide()
    left_arrow_selection_window.Hide()
    jukebox_selection_window.Hide()
    info_screen_window.Hide()
    control_button_window.Hide()
    song_playing_lookup_window.Hide()
    window_background.Hide()

    # Search Windows Button Layout
    search_window_button_layout = create_search_window_button_layout()
    search_window = sg.Window('', search_window_button_layout, modal=True, no_titlebar = True, size = (1280,720),
        default_button_element_size=(5, 2), auto_size_buttons=False, background_color='black',
        button_color=["firebrick4", "goldenrod1"], font="Helvetica 16 bold", finalize=True)

    # Apply focus highlighting to A button (reversed colors)
    search_window['--A--'].update(button_color=["goldenrod1", "firebrick4"])
    search_window['--A--'].set_focus()
    search_window.bind('<Right>', '-NEXT-')
    search_window.bind('<Left>', '-PREV-')
    search_window.bind('<Up>', '-UP-')
    search_window.bind('<Down>', '-DOWN-')
    search_window.bind('<S>', '--SELECTED_LETTER--')
    search_window.bind('<C>', '--DELETE--')
    search_window.bind('<Escape>', '--ESC--')
    keys_entered = ''
    search_results = []

    # Button grid mapping for Up/Down navigation: {button_key: (row, col)}
    button_grid = {
        # Row 0: Numbers
        '1': (0, 0), '2': (0, 1), '3': (0, 2), '4': (0, 3), '5': (0, 4),
        '6': (0, 5), '7': (0, 6), '8': (0, 7), '9': (0, 8), '0': (0, 9), '-': (0, 10),
        # Row 1: Letters A-K
        '--A--': (1, 0), 'B': (1, 1), 'C': (1, 2), 'D': (1, 3), 'E': (1, 4),
        'F': (1, 5), 'G': (1, 6), 'H': (1, 7), 'I': (1, 8), 'J': (1, 9), 'K': (1, 10),
        # Row 2: Letters L-V
        'L': (2, 0), 'M': (2, 1), 'N': (2, 2), 'O': (2, 3), 'P': (2, 4),
        'Q': (2, 5), 'R': (2, 6), 'S': (2, 7), 'T': (2, 8), 'U': (2, 9), 'V': (2, 10),
        # Row 3: Letters W-Z, apostrophe
        'W': (3, 0), 'X': (3, 1), 'Y': (3, 2), 'Z': (3, 3), "'": (3, 4),
        # Row 4: Special buttons
        '--DELETE--': (4, 0), '--space--': (4, 1), '--CLEAR--': (4, 2), '--EXIT--': (4, 3),
        # Row 5: Result buttons
        '--result_one--': (5, 0), '--result_two--': (5, 1), '--result_three--': (5, 2),
        '--result_four--': (5, 3), '--result_five--': (5, 4)
    }

    # Reverse mapping for navigation: {(row, col): button_key}
    grid_to_button = {v: k for k, v in button_grid.items()}

    # Color schemes for focus highlighting
    NORMAL_COLORS = ["firebrick4", "goldenrod1"]  # Dark red text on gold background
    FOCUSED_COLORS = ["goldenrod1", "firebrick4"]  # Gold text on dark red background (reversed)

    # Track currently focused button for color highlighting
    current_focused_button = '--A--'

    # Set search window to artist if Artist search selected
    if search_flag == "artist":
        search_window["--search_type--"].update("Search For Artist")

    # Keyboard event loop for title search window
    while True:
        event, values = search_window.read()  # read the title_search_window
        print(event, values)
        # Handle ESC key in search window
        if event == '--ESC--':
            search_window.close()
            # Restore main jukebox windows
            right_arrow_selection_window.UnHide()
            left_arrow_selection_window.UnHide()
            jukebox_selection_window.UnHide()
            info_screen_window.UnHide()
            control_button_window.UnHide()
            window_background.UnHide()
            return None
        if event == "-NEXT-" or event == "-PREV-" or event == "-UP-" or event == "-DOWN-" or event == "--CLEAR--" or event == '--EXIT--':
            if event == "-NEXT-":
                next_element = search_window.find_element_with_focus().get_next_focus()
                next_key = next_element.Key
                # Reset previous focused button to normal colors
                search_window[current_focused_button].update(button_color=NORMAL_COLORS)
                # Set new focused button to highlighted colors
                search_window[next_key].update(button_color=FOCUSED_COLORS)
                next_element.set_focus()
                current_focused_button = next_key
            if event == "-PREV-":
                prev_element = search_window.find_element_with_focus().get_previous_focus()
                prev_key = prev_element.Key
                # Reset previous focused button to normal colors
                search_window[current_focused_button].update(button_color=NORMAL_COLORS)
                # Set new focused button to highlighted colors
                search_window[prev_key].update(button_color=FOCUSED_COLORS)
                prev_element.set_focus()
                current_focused_button = prev_key
            if event == "-UP-":
                # Get current focused button
                current_element = search_window.find_element_with_focus()
                current_key = current_element.Key
                # Look up position in grid
                if current_key in button_grid:
                    current_row, current_col = button_grid[current_key]
                    # Calculate target position (one row up)
                    target_row = current_row - 1
                    target_col = current_col
                    # Handle column alignment for shorter rows
                    if target_row == 3 and target_col > 4:  # Row 3 only has 5 buttons (cols 0-4)
                        target_col = 4
                    elif target_row == 4 and target_col > 3:  # Row 4 only has 4 buttons (cols 0-3)
                        target_col = 3
                    # Check if target position exists
                    if target_row >= 0 and (target_row, target_col) in grid_to_button:
                        target_key = grid_to_button[(target_row, target_col)]
                        # Reset previous focused button to normal colors
                        search_window[current_focused_button].update(button_color=NORMAL_COLORS)
                        # Set new focused button to highlighted colors
                        search_window[target_key].update(button_color=FOCUSED_COLORS)
                        # Set focus to target button
                        search_window[target_key].set_focus()
                        current_focused_button = target_key
            if event == "-DOWN-":
                # Get current focused button
                current_element = search_window.find_element_with_focus()
                current_key = current_element.Key
                # Look up position in grid
                if current_key in button_grid:
                    current_row, current_col = button_grid[current_key]
                    # Calculate target position (one row down)
                    target_row = current_row + 1
                    target_col = current_col
                    # Handle column alignment for shorter rows
                    if target_row == 3 and target_col > 4:  # Row 3 only has 5 buttons (cols 0-4)
                        target_col = 4
                    elif target_row == 4 and target_col > 3:  # Row 4 only has 4 buttons (cols 0-3)
                        target_col = 3
                    elif target_row == 5:  # Row 5 is result buttons
                        if target_col > 4:  # Only 5 result buttons (cols 0-4)
                            target_col = 4
                        # Check if result buttons are visible before navigating to them
                        if (target_row, target_col) in grid_to_button:
                            target_key = grid_to_button[(target_row, target_col)]
                            # Only navigate to result button if it's visible
                            if len(search_results) > 0:
                                # Reset previous focused button to normal colors
                                search_window[current_focused_button].update(button_color=NORMAL_COLORS)
                                # Set new focused button to highlighted colors
                                search_window[target_key].update(button_color=FOCUSED_COLORS)
                                search_window[target_key].set_focus()
                                current_focused_button = target_key
                    elif target_row <= 4:  # Rows 0-4 (keyboard rows)
                        if (target_row, target_col) in grid_to_button:
                            target_key = grid_to_button[(target_row, target_col)]
                            # Reset previous focused button to normal colors
                            search_window[current_focused_button].update(button_color=NORMAL_COLORS)
                            # Set new focused button to highlighted colors
                            search_window[target_key].update(button_color=FOCUSED_COLORS)
                            search_window[target_key].set_focus()
                            current_focused_button = target_key
            if event == "--CLEAR--":  # clear keys if clear button
                keys_entered = ""
                search_results = []
                search_window["--letter_entry--"].Update(keys_entered)
                search_window["--result_one--"].update("", visible=False, disabled=False)
                search_window["--result_two--"].update("", visible=False)
                search_window["--result_three--"].update("", visible=False)
                search_window["--result_four--"].update("", visible=False)
                search_window["--result_five--"].update("", visible=False)
            if event == "--EXIT--":
                #  Code to restore main jukebox windows
                right_arrow_selection_window.UnHide()
                left_arrow_selection_window.UnHide()
                jukebox_selection_window.UnHide()
                info_screen_window.UnHide()
                control_button_window.UnHide()
                window_background.UnHide()
                # Clear search results
                keys_entered = ""
                # close title search window
                search_window.close()
                return None
        else:
            # Code specific to title search
            if search_flag == "title":
                if event == "--result_one--" or event == "--result_two--" or event == "--result_three--" or event == "--result_four--" or event == "--result_five--":
                    button_text = search_window[event].get_text()
                    song_search = f'{button_text}'
                    # Code to search for song number
                    for i in range(len(MusicMasterSongList)):
                        if song_search == str(MusicMasterSongList[i]['artist'] + ' - ' + str(MusicMasterSongList[i]['title'])):
                            #Song number found
                            # Song number assigned to song_selected_number variable
                            song_selected_number = MusicMasterSongList[i]['number']
                            # Code to set main jukeox selection window screen for selected song
                            selection_window_number = song_selected_number
                            selection_buttons_update(selection_window_number)
                            # Code to update the main jukebox selection window position A1 to the selected song
                            jukebox_selection_window['--button0_top--'].update(text = MusicMasterSongList[i]['title'])
                            jukebox_selection_window['--button0_bottom--'].update(text = MusicMasterSongList[i]['artist'])
                            # Code to set main main jukebox selection window to selected song
                            disable_a_selection_buttons()
                            control_button_window['--A--'].update(disabled=True)
                            jukebox_selection_window['--button0_top--'].update(disabled = False)
                            jukebox_selection_window['--button0_bottom--'].update(disabled = False)
                            control_button_window['--select--'].update(disabled = False)
                            disable_b_selection_buttons()
                            disable_c_selection_buttons()
                            # Requied by the main jukebox selection window
                            song_selected = "A1"
                            # Code to restore main jukebox windows
                            window_background.UnHide()
                            right_arrow_selection_window.UnHide()
                            left_arrow_selection_window.UnHide()
                            jukebox_selection_window.UnHide()
                            info_screen_window.UnHide()
                            control_button_window.UnHide()
                            # Clear search results
                            keys_entered = ""
                            # close title search window
                            search_window.close()
                            return {'song_number': song_selected_number, 'song_selected': song_selected}
                    #Skip code that updates main Jukebox windows
                    break
            if search_flag == "artist":
                if event == "--result_one--" or event == "--result_two--" or event == "--result_three--" or event == "--result_four--" or event == "--result_five--":
                    button_text = search_window[event].get_text()
                    song_search = f'{button_text}'
                    #  Locate song number
                    counter = 0
                    for i in MusicMasterSongList:
                        if song_search in MusicMasterSongList[counter]['artist']:
                            print('artist looking for is: ' + str(song_search))
                            print('artist match found')
                            # Song Number Start Found
                            if len(song_search) == len(MusicMasterSongList[counter]['artist']):
                                print(MusicMasterSongList[counter]['number'])
                                # Song number found
                                #print(find_list[counter])
                                print("Title Selected is number: " + str(MusicMasterSongList[counter]['number']))
                                print("Artist Selected is: " + str(MusicMasterSongList[counter]['artist']))
                                # Song number assigned ot song_selected_number variable
                                song_selected_number = MusicMasterSongList[counter]['number']
                                # Code to set main jukeox selection window screen for selected song
                                selection_window_number = song_selected_number
                                selection_buttons_update(selection_window_number)
                                # Code to restore main jukebox windows
                                right_arrow_selection_window.UnHide()
                                left_arrow_selection_window.UnHide()
                                jukebox_selection_window.UnHide()
                                info_screen_window.UnHide()
                                control_button_window.UnHide()
                                window_background.UnHide()
                                # Clear search results
                                keys_entered = ""
                                # close artist search window
                                search_window.close()
                                # Note: Artist search doesn't set song_selected like title search does
                                # Return just the song_number for now
                                return {'song_number': song_selected_number, 'song_selected': None}
                            else:
                                pass
                        counter += 1
                    #Skip code that updates main Jukebox windows
                    break
            if event == sg.WIN_CLOSED:  # if the X button clicked, just exit
                break
            # Code to update the search results based on the keys entered via the keypad
            if (event) == "--SELECTED_LETTER--":
                selected_letter_entry = search_window.find_element_with_focus()
                selected_letter_entry.Click()
                # key_entry(keys_entered)
                if event == "A":
                    keys_entered = keys_entered + "A"
                if event == "B":
                    keys_entered = keys_entered + "B"
                if event == "C":
                    keys_entered = keys_entered + "C"
                if event == "D":
                    keys_entered = keys_entered + "D"
                if event == "E":
                    keys_entered = keys_entered + "E"
                if event == "F":
                    keys_entered = keys_entered + "F"
                if event == "G":
                    keys_entered = keys_entered + "G"
                if event == "H":
                    keys_entered = keys_entered + "H"
                if event == "I":
                    keys_entered = keys_entered + "I"
                if event == "J":
                    keys_entered = keys_entered + "J"
                if event == "K":
                    keys_entered = keys_entered + "K"
                if event == "L":
                    keys_entered = keys_entered + "L"
                if event == "M":
                    keys_entered = keys_entered + "M"
                if event == "N":
                    keys_entered = keys_entered + "N"
                if event == "O":
                    keys_entered = keys_entered + "O"
                if event == "P":
                    keys_entered = keys_entered + "P"
                if event == "Q":
                    keys_entered = keys_entered + "Q"
                if event == "R":
                    keys_entered = keys_entered + "R"
                if event == "S":
                    keys_entered = keys_entered + "S"
                if event == "T":
                    keys_entered = keys_entered + "T"
                if event == "U":
                    keys_entered = keys_entered + "U"
                if event == "V":
                    keys_entered = keys_entered + "V"
                if event == "W":
                    keys_entered = keys_entered + "W"
                if event == "X":
                    keys_entered = keys_entered + "X"
                if event == "Y":
                    keys_entered = keys_entered + "Y"
                if event == "Z":
                    keys_entered = keys_entered + "Z"
                if event == "1":
                    keys_entered = keys_entered + "1"
                if event == "2":
                    keys_entered = keys_entered + "2"
                if event == "3":
                    keys_entered = keys_entered + "3"
                if event == "4":
                    keys_entered = keys_entered + "4"
                if event == "5":
                    keys_entered = keys_entered + "5"
                if event == "6":
                    keys_entered = keys_entered + "6"
                if event == "7":
                    keys_entered = keys_entered + "7"
                if event == "8":
                    keys_entered = keys_entered + "8"
                if event == "9":
                    keys_entered = keys_entered + "9"
                if event == "0":
                    keys_entered = keys_entered + "0"
            if event == "--DELETE--":
                keys_entered = keys_entered[:-1]
            if event == "--space--":
                keys_entered += " "
            elif event == "-":
                keys_entered += "-"
            elif event == "'":
                keys_entered += "'"
            # Code to update the search results based on the keys entered via a computer keyboard or mouse
            elif event in "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                print(event, values)
                if event == "B":
                    keys_entered = keys_entered + "B"
                if event == "C":
                    keys_entered = keys_entered + "C"
                if event == "D":
                    keys_entered = keys_entered + "D"
                if event == "E":
                    keys_entered = keys_entered + "E"
                if event == "F":
                    keys_entered = keys_entered + "F"
                if event == "G":
                    keys_entered = keys_entered + "G"
                if event == "H":
                    keys_entered = keys_entered + "H"
                if event == "I":
                    keys_entered = keys_entered + "I"
                if event == "J":
                    keys_entered = keys_entered + "J"
                if event == "K":
                    keys_entered = keys_entered + "K"
                if event == "L":
                    keys_entered = keys_entered + "L"
                if event == "M":
                    keys_entered = keys_entered + "M"
                if event == "N":
                    keys_entered = keys_entered + "N"
                if event == "O":
                    keys_entered = keys_entered + "O"
                if event == "P":
                    keys_entered = keys_entered + "P"
                if event == "Q":
                    keys_entered = keys_entered + "Q"
                if event == "R":
                    keys_entered = keys_entered + "R"
                if event == "S":
                    keys_entered = keys_entered + "S"
                if event == "T":
                    keys_entered = keys_entered + "T"
                if event == "U":
                    keys_entered = keys_entered + "U"
                if event == "V":
                    keys_entered = keys_entered + "V"
                if event == "W":
                    keys_entered = keys_entered + "W"
                if event == "X":
                    keys_entered = keys_entered + "X"
                if event == "Y":
                    keys_entered = keys_entered + "Y"
                if event == "Z":
                    keys_entered = keys_entered + "Z"
                if event == "1":
                    keys_entered = keys_entered + "1"
                if event == "2":
                    keys_entered = keys_entered + "2"
                if event == "3":
                    keys_entered = keys_entered + "3"
                if event == "4":
                    keys_entered = keys_entered + "4"
                if event == "5":
                    keys_entered = keys_entered + "5"
                if event == "6":
                    keys_entered = keys_entered + "6"
                if event == "7":
                    keys_entered = keys_entered + "7"
                if event == "8":
                    keys_entered = keys_entered + "8"
                if event == "9":
                    keys_entered = keys_entered + "9"
                if event == "0":
                    keys_entered = keys_entered + "0"
                print(keys_entered)
            elif event == "Submit":
                keys_entered = values["input"]
                search_window["out"].update(keys_entered)  # output the final stringsd
            if event == "--A--":
                keys_entered = keys_entered + "A"
            print(keys_entered)
            # Code to bring up search results based on keys entered
            # Code to search for song title based on keys entered
            if search_flag == "title":
                for i, item in enumerate(MusicMasterSongList):
                    find_list_search = MusicMasterSongList[i]['title']
                    match = find_list_search.lower().find(keys_entered.lower())
                    if match == 0:  # ensures match is from left of string
                        search_results.append(str(MusicMasterSongList[i]['artist']) + " - " + str(MusicMasterSongList[i]['title']))
            # Code to search for artist based on keys entered
            if search_flag == "artist":
                find_list = all_artists_list
                print(keys_entered)
                for i, item in enumerate(find_list):
                    find_list_search = find_list[i]
                    match = find_list_search.lower().find(keys_entered.lower())
                    if match == 0:  # ensures match is from left of string
                        search_results.append(str(find_list[i]))
            # Code to update search results on search window
            if len(search_results) <= 5:
                search_window["--result_one--"].update(visible=True, disabled=False)
                search_window["--result_two--"].update(visible=True)
                search_window["--result_three--"].update(visible=True)
                search_window["--result_four--"].update(visible=True)
                search_window["--result_five--"].update(visible=True)
            if len(search_results) <= 4:
                search_window["--result_one--"].update(visible=True, disabled=False)
                search_window["--result_two--"].update(visible=True)
                search_window["--result_three--"].update(visible=True)
                search_window["--result_four--"].update(visible=True)
                search_window["--result_five--"].update(visible=False)
            if len(search_results) <= 3:
                search_window["--result_one--"].update(visible=True, disabled=False)
                search_window["--result_two--"].update(visible=True)
                search_window["--result_three--"].update(visible=True)
                search_window["--result_four--"].update(visible=False)
                search_window["--result_five--"].update(visible=False)
            if len(search_results) <= 2:
                search_window["--result_one--"].update(visible=True, disabled=False)
                search_window["--result_two--"].update(visible=True)
                search_window["--result_three--"].update(visible=False)
                search_window["--result_four--"].update(visible=False)
                search_window["--result_five--"].update(visible=False)
            if len(search_results) <= 1:
                search_window["--result_one--"].update(visible=True, disabled=False)
                search_window["--result_two--"].update(visible=False)
                search_window["--result_three--"].update(visible=False)
                search_window["--result_four--"].update(visible=False)
                search_window["--result_five--"].update(visible=False)
            if len(search_results) == 0:
                search_window["--result_one--"].update("Song Title Not On Jukebox", disabled=True)
                search_window["--result_two--"].update(visible=False)
                search_window["--result_three--"].update(visible=False)
                search_window["--result_four--"].update(visible=False)
                search_window["--result_five--"].update(visible=False)
            for x in range(len(search_results)):
                if len(search_results) == 0:
                    search_window["--result_one--"].update("", disabled=False)
                    search_window["--result_two--"].update("")
                    search_window["--result_three--"].update("")
                    search_window["--result_four--"].update("")
                    search_window["--result_five--"].update("")
                if len(search_results) == 1:
                    search_window["--result_one--"].update(search_results[0], disabled=False)
                    search_window["--result_two--"].update("")
                    search_window["--result_three--"].update("")
                    search_window["--result_four--"].update("")
                    search_window["--result_five--"].update("")
                if len(search_results) == 2:
                    search_window["--result_one--"].update(search_results[0], disabled=False)
                    search_window["--result_two--"].update(search_results[1])
                    search_window["--result_three--"].update("")
                    search_window["--result_four--"].update("")
                    search_window["--result_five--"].update("")
                if len(search_results) == 3:
                    search_window["--result_one--"].update(search_results[0], disabled=False)
                    search_window["--result_two--"].update(search_results[1])
                    search_window["--result_three--"].update(search_results[2])
                    search_window["--result_four--"].update("")
                    search_window["--result_five--"].update("")
                if len(search_results) == 4:
                    search_window["--result_one--"].update(search_results[0], disabled=False)
                    search_window["--result_two--"].update(search_results[1])
                    search_window["--result_three--"].update(search_results[2])
                    search_window["--result_four--"].update(search_results[3])
                    search_window["--result_five--"].update("")
                if len(search_results) == 5:
                    search_window["--result_one--"].update(search_results[0], disabled=False)
                    search_window["--result_two--"].update(search_results[1])
                    search_window["--result_three--"].update(search_results[2])
                    search_window["--result_four--"].update(search_results[3])
                    search_window["--result_five--"].update(search_results[4])
                if len(search_results) > 5:
                    search_window["--result_one--"].update(keys_entered, disabled=False)
                    search_window["--result_two--"].update(keys_entered)
                    search_window["--result_three--"].update(keys_entered)
                    search_window["--result_four--"].update(keys_entered)
                    search_window["--result_five--"].update(keys_entered)
        search_results = []
        search_window["--letter_entry--"].Update(keys_entered)
        # End of search window event loop code

    # If we exit the while loop without returning, it means user closed window
    return None
