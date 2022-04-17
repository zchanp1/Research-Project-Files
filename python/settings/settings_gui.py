import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)

from os import path

from icons import settings_icon

"""
    A simple "main_settings" implementation.  Load/Edit/Save main_settings for your programs
    Uses json file format which makes it trivial to integrate into a Python program.  If you can
    put your data into a dictionary, you can save it as a main_settings file.

    Note that it attempts to use a lookup dictionary to convert from the main_settings file to keys used in 
    your main_settings window.  Some element's "update" methods may not work correctly for some elements.

    Copyright 2020 PySimpleGUI.com
    Licensed under LGPL-3
"""

MCF_SETTINGS_FILE = path.join(path.dirname(__file__), r'settings_file.cfg').replace('\\', '/')
MCF_DEFAULT_SETTINGS = {
    'labview_topic': '../../data/topic.txt', 'refresh_period': 0.01,
    'grating_spacing': 10 * 10 ** -3,
    'core_to_center': 37,
    'calibration_matrix_f': '../calibration/calibration_files/calibration_matrix_23022021.npy',
    'wav0_f': '../../data/wav0.csv', 'nb_gratings': 25, 'central_core': 2, 'interpolate_factor': 1,
    'first_grating': 1, 'last_grating': 8}
MCF_SETTINGS_KEYS_TO_ELEMENT_KEYS = {
    'labview_topic': '-TOPIC-', 'refresh_period': '-REFRESH_T-',
    'grating_spacing': '-SPACING-', 'core_to_center': '-CORE_TO_CENTER-',
    'interpolate_factor': '-INTERPOLATE-',
    'calibration_matrix_f': '-CALIBRATION MAT-', 'wav0_f': '-WAV0-',
    'nb_gratings': '-NB_GRATINGS-', 'central_core': '-CENTRAL_CORE-',
    'first_grating': '-FIRST_G-', 'last_grating': '-LAST_G-'}
# Settings recording variables
RECORDING_SETTINGS_FILE = path.join(path.dirname(__file__), r'recording_settings_file.cfg').replace('\\', '/')
RECORDING_DEFAULT_SETTINGS = {'current_folder': '', 'temp_json_file': ''}
RECORDING_SETTINGS_KEYS_TO_ELEMENT_KEYS = {'current_folder': '-FOLDER-', 'temp_json_file': '-TEMP_JSON-'}


# ------------------- Load/Save Settings File -------------------
def load_settings(settings_file, default_settings=None, settings_keys_to_elm_keys=None):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
            check_settings_format(settings)

    except Exception as e:
        sg.popup_quick_message(f'exception {e}', 'No main_settings file found... will create one for you',
                               keep_on_top=True,
                               background_color='red', text_color='white')
        settings = default_settings
        save_settings(settings_file, settings, default_settings, settings_keys_to_elm_keys)
    return settings


def check_settings_format(settings):
    """
    In case the dict value is a string, check that if it is a number of not
    - if value is digit convert it to int
    - if value is numeric convert it to float
    """

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    for key, value in settings.items():
        if isinstance(value, str):
            if value.isdigit():
                settings[key] = int(value)
            elif isfloat(value):
                settings[key] = float(value)
    return


def save_settings(settings_file, settings, values, settings_keys_to_elm_keys, popup=False):
    if values:  # if there are stuff specified by another window, fill in those values
        for key in settings_keys_to_elm_keys:  # update window with the values read from main_settings file
            try:
                settings[key] = values[settings_keys_to_elm_keys[key]]
            except Exception as e:
                print(f'Problem updating main_settings from window values. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    if popup:
        sg.popup('Settings saved')


# ------------------- Different main_settings layout ------------------
def text_label(text):
    return sg.Text(text + ':', justification='r', size=(20, 1))


def generate_mcf_settings_layout():
    layout = [[sg.Text('Settings', font='Any 15')],
              [text_label('Labview topic'), sg.Input(key='-TOPIC-'), sg.FileBrowse(target='-TOPIC-')],
              [text_label('Reference wavelengths file'), sg.Input(key='-WAV0-'), sg.FileBrowse(target='-WAV0-')],
              [text_label('Gratings per core'), sg.Input(key='-NB_GRATINGS-', size=(5, 1)),
               text_label('Refresh period'), sg.Input(key='-REFRESH_T-', size=(5, 1))],
              [text_label('Grating spacing'), sg.Input(key='-SPACING-', size=(5, 1)),
               text_label('Core to center (μm)'), sg.Input(key='-CORE_TO_CENTER-', size=(5, 1))],
              [text_label('Coefficient matrix file'), sg.Input(key='-CALIBRATION MAT-'),
               sg.FileBrowse(target='-CALIBRATION MAT-')],
              [text_label('Central core'), sg.Input(key='-CENTRAL_CORE-', size=(5, 1)),
               text_label('Interpolation factor'), sg.Input(key='-INTERPOLATE-', size=(5, 1))],
              [text_label('First grating in rail'), sg.Input(key='-FIRST_G-', size=(5, 1)),
               text_label('Last grating in rail'), sg.Input(key='-LAST_G-', size=(5, 1))],
              [sg.Button('Save'), sg.Button('Exit')]]
    return layout


def generate_recording_settings_layout():
    layout = [[sg.Text('Settings', font='Any 15')],
              [text_label('Current folder'), sg.Input(key='-FOLDER-'), sg.FolderBrowse(target='-FOLDER-')],
              [text_label('Temp JSON file'), sg.Input(key='-TEMP_JSON-'), sg.FileBrowse(target='-TEMP_JSON-')],
              [sg.Button('Save'), sg.Button('Exit')]]
    return layout


# ------------------- Different main_settings layout ------------------
def create_settings_window(settings, layout, settings_keys_to_elm_keys):
    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    for key in settings_keys_to_elm_keys:  # update window with the values read from main_settings file
        try:
            window[settings_keys_to_elm_keys[key]].update(value=settings[key])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from main_settings. Key = {key}')

    return window


# ------------------- Settings Window & Event Loop -------------------
def settings_button(image_subsample=1):
    settings_button = sg.Button('', image_data=settings_icon, key='-SETTINGS-',
                                button_color=(sg.theme_background_color(), sg.theme_background_color()),
                                border_width=0, image_subsample=image_subsample)
    return settings_button


def settings_window(settings_type='mcf'):
    settings_file, default_settings, layout, settings_keys_to_elm_keys = None, None, None, None

    if settings_type == 'recording':
        settings_file = RECORDING_SETTINGS_FILE
        default_settings = RECORDING_DEFAULT_SETTINGS
        layout = generate_recording_settings_layout()
        settings_keys_to_elm_keys = RECORDING_SETTINGS_KEYS_TO_ELEMENT_KEYS

    elif settings_type == 'mcf':
        settings_file = MCF_SETTINGS_FILE
        default_settings = MCF_DEFAULT_SETTINGS
        layout = generate_mcf_settings_layout()
        settings_keys_to_elm_keys = MCF_SETTINGS_KEYS_TO_ELEMENT_KEYS

    settings = load_settings(settings_file, default_settings, settings_keys_to_elm_keys)

    while True:  # Event Loop
        event, values = create_settings_window(settings, layout, settings_keys_to_elm_keys).read(close=True)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event == 'Save':
            save_settings(settings_file, settings, values, settings_keys_to_elm_keys)
            break
    return settings


if __name__ == '__main__':
    settings_window('mcf')
    settings_window('recording')
