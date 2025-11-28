import FreeSimpleGUI as sg


def create_info_screen_layout(master_songlist_number):
    """
    Create and return the layout for the info screen window.

    Args:
        master_songlist_number: The total number of songs available

    Returns:
        A list representing the PySimpleGUI layout for the info screen
    """
    info_screen_layout = [
        [sg.Text(text="Now Playing", border_width=0, pad=(0, 0), size=(18, 1), justification="center",
             text_color='SeaGreen3', font='Helvetica 20 bold')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(20, 1), justification="center",
                 text_color='White', font='Helvetica 18 bold', key='--song_title--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(24, 1), justification="center",
                 text_color='White', font='Helvetica 16 bold', key='--song_artist--')],
        [sg.Text(text='  Mode: Playing Song', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3', font='Helvetica 12 bold')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3', font='Helvetica 12 bold', key='--mini_song_title--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3', font='Helvetica 12 bold', key='--mini_song_artist--')],
        [sg.Text(text='  Year:        Length:     ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3', font='Helvetica 12 bold', key='--year--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1),
             justification="left", text_color='SeaGreen3', font='Helvetica 12 bold', key='--album--')],
        [sg.Text(text='Upcoming Selections', border_width=0, pad=(0, 0), size=(20, 1), justification="center",
                 text_color='SeaGreen3', font='Helvetica 18 bold')],
        [sg.Text(text='', border_width=0, pad=(0, 0), size=(28, 1), justification="left", text_color='SeaGreen1',
                  font='Helvetica 2 bold')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3',  font='Helvetica 12 bold', key='--upcoming_one--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3',  font='Helvetica 12 bold', key='--upcoming_two--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3',  font='Helvetica 12 bold',key='--upcoming_three--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1),
                 justification="left", text_color='SeaGreen3', font='Helvetica 12 bold', key='--upcoming_four--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3',  font='Helvetica 12 bold', key='--upcoming_five--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1),
                 justification="left", text_color='SeaGreen3', font='Helvetica 12 bold', key='--upcoming_six--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3',  font='Helvetica 12 bold', key='--upcoming_seven--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3',  font='Helvetica 12 bold', key='--upcoming_eight--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left",
                 text_color='SeaGreen3',  font='Helvetica 12 bold', key='--upcoming_nine--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1),
                 justification="left", text_color='SeaGreen3', font='Helvetica 12 bold', key='--upcoming_ten--')],
        [sg.Text(text=' ', border_width=0, pad=(0, 0), size=(28, 1), justification="left", text_color='SeaGreen1',
                  font='Helvetica 2 bold')],
        [sg.Text(text='CREDITS 0', border_width=0, pad=(0, 0), size=(19, 1), justification="center", text_color='White',
                  font='Helvetica 20 bold', key='--credits--')],
        [sg.Text(text='Twenty-Five Cents Per Selection', border_width=0, pad=(0, 0), size=(30, 1),
                 justification="center", text_color='SeaGreen3', font='Helvetica 12 bold')],
        [sg.Text(text=str(master_songlist_number) + ' Song Selections Available', border_width=0, pad=(0, 0), size=(30, 1),
                 justification="center", text_color='SeaGreen3', font='Helvetica 12 bold')]
    ]

    return info_screen_layout
