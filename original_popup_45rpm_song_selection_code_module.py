"""
45RPM Record Pop-up Code Module
Handles the display of 45rpm record labels with song information as animated popups
"""

import os
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont
import vlc
import FreeSimpleGUI as sg


def display_45rpm_popup(MusicMasterSongList, counter, jukebox_selection_window):
    """
    Display an animated 45rpm record popup with song title and artist information.

    This function creates a visual representation of a 45rpm record label with the
    selected song's title and artist, then displays it as an animated popup.

    Args:
        MusicMasterSongList (list): List containing song information dictionaries
        counter (int): Index of the current song in MusicMasterSongList
        jukebox_selection_window: The FreeSimpleGUI window object to hide/unhide

    Returns:
        None
    """

    # https://www.tutorialspoint.com/how-to-add-text-on-an-image-using-pillow-in-python
    # Center Anchor Lable Position https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
    center_position = 684

    # Record Title Name
    record_title_name = str(MusicMasterSongList[counter]['title'])
    record_title_name_length = len(record_title_name)

    # Record Artist Name
    record_artist_name = str(MusicMasterSongList[counter]['artist'])
    record_artist_name_length = len(record_artist_name)

    # Open the desired Image you want to add text on
    # Create the list of all black print 45rpm record labels
    path = "record_labels/final_black_sel/"
    black_print_label_list = os.listdir(path)

    # Selects a random 45rpm record label requiring black print
    record_label = Image.open('record_labels/final_black_sel/' + str(random.choice(black_print_label_list)))
    draw_on_45rpm_image = ImageDraw.Draw(record_label)

    # Record Display Generation
    if record_title_name_length > 37 or record_artist_name_length >= 30:
        font = ImageFont.truetype("fonts/OpenSans-ExtraBold.ttf", 15)
        wrapper = textwrap.TextWrapper(width=37)  # https://www.geeksforgeeks.org/textwrap-text-wrapping-filling-python/
        record_title_name_wrap = wrapper.wrap(text=record_title_name)
        draw_on_45rpm_image.text((center_position, 520), record_title_name_wrap[0], fill="black", anchor="mb", font=font)
        try:
            draw_on_45rpm_image.text((center_position, 535), record_title_name_wrap[1], fill="black", anchor="mb", font=font)
        except Exception:
            pass
        wrapper = textwrap.TextWrapper(width=30)
        record_artist_name_wrap = wrapper.wrap(text=record_artist_name)
        draw_on_45rpm_image.text((center_position, 555), record_artist_name_wrap[0], fill="black", anchor="mb", font=font)
        try:
            draw_on_45rpm_image.text((center_position, 570), record_artist_name_wrap[1], fill="black", anchor="mb", font=font)
        except Exception:
            pass
    elif record_title_name_length < 37 and record_title_name_length > 17:
        font = ImageFont.truetype("fonts/OpenSans-ExtraBold.ttf", 20)
        draw_on_45rpm_image.text((center_position, 515), record_title_name, fill="black", anchor="mb", font=font)
        draw_on_45rpm_image.text((center_position, 540), record_artist_name, fill="black", anchor="mb", font=font)
    elif record_artist_name_length < 26 and record_artist_name_length > 13:
        font = ImageFont.truetype("fonts/OpenSans-ExtraBold.ttf", 20)
        draw_on_45rpm_image.text((center_position, 515), record_title_name, fill="black", anchor="mb", font=font)
        draw_on_45rpm_image.text((center_position, 540), record_artist_name, fill="black", anchor="mb", font=font)
    elif record_title_name_length <= 17:
        font = ImageFont.truetype("fonts/OpenSans-ExtraBold.ttf", 30)
        draw_on_45rpm_image.text((center_position, 515), record_title_name, fill="black", anchor="mb", font=font)
        draw_on_45rpm_image.text((center_position, 540), record_artist_name, fill="black", anchor="mb", font=font)
    elif record_artist_name_length <= 13:
        font = ImageFont.truetype("fonts/OpenSans-ExtraBold.ttf", 30)
        draw_on_45rpm_image.text((center_position, 515), record_title_name, fill="black", anchor="mb", font=font)
        draw_on_45rpm_image.text((center_position, 540), record_artist_name, fill="black", anchor="mb", font=font)

    # Save the image on which we have added the text
    record_label.save("images/selection_45.jpg")

    # Save and resize the image on which we have added the text
    record_label.resize((680, 394)).save('images/selection_45.gif')

    # VLC Song Playback Code Begin
    p = vlc.MediaPlayer('jukebox_required_audio_files/success.mp3')
    p.play()

    # Display the image as popup
    jukebox_selection_window.Hide()
    for i in range(600):  # adjust the range to control the time the image runs
        sg.PopupAnimated('images/selection_45.gif', relative_location=(167, 45), time_between_frames=1, no_titlebar=True, keep_on_top=True)
    sg.PopupAnimated(None)  # close all Animated Popups
    jukebox_selection_window.UnHide()
