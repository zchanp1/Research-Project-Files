from os import path
import PySimpleGUI as sg

from config import *


first_index = 0
last_index = first_index + NB_GRATINGS_IN_RAIL
range_gratings = tuple(range(1, NB_GRATINGS_PER_CORE + 1))
range_experiment = tuple(range(1, 20))

LOCALIZATION_SETTINGS_FILE = path.join(path.dirname(__file__), r'localization_settings_file.cfg').replace('\\', '/')
LOCALIZATION_DEFAULT_SETTINGS = {
    'phantom_name': 'phantom_D_50',
    'phantom_material': 'rigid',
    'rail_material': 'DS30',
    'first_grating_idx': first_index + 1,
    'last_grating_idx': last_index + 1,
    'experiment_id': 1}

localization_settings = load_settings(LOCALIZATION_SETTINGS_FILE, LOCALIZATION_DEFAULT_SETTINGS,
                                      LOCALIZATION_EXPERIMENT_ARGS_TO_KEY)


def create_localization_column(disabled=False):
    label_column_list = [[sg.Text('Phantom name: ')], [sg.Text('Phantom material: ')],
                         [sg.Text('First grating : ')], [sg.Text('Last grating : ')],
                         [sg.Text('Rail material:')], [sg.Text('Experiment id:')]]

    input_size = (14, 1)
    input_combo_column_list = [
        [sg.InputCombo(tuple(phantoms_dict.keys()), default_value=localization_settings['phantom_name'],
                       enable_events=True, disabled=disabled, size=input_size, key='-PHANTOM-')],
        [sg.InputCombo(phantom_materials, default_value=localization_settings['phantom_material'],
                       enable_events=True, disabled=disabled, size=input_size, key='-PHANTOM_MAT-')],
        [sg.InputCombo(range_gratings, default_value=localization_settings['first_grating_idx'],
                       enable_events=True, disabled=False, size=input_size, key='-MIN-')],
        [sg.InputCombo(range_gratings, default_value=localization_settings['last_grating_idx'],
                       enable_events=True, disabled=False, size=input_size, key='-MAX-')],
        [sg.InputCombo(rail_materials, default_value=localization_settings['rail_material'],
                       enable_events=True, disabled=disabled, size=input_size, key='-RAIL-')],
        [sg.InputCombo(range_experiment, default_value=localization_settings['experiment_id'],
                       enable_events=True, size=input_size, key='-ID-')]]

    parameters_column_list = [
        sg.Frame('Parameters', [[sg.Column(label_column_list, element_justification='l'),
                                 sg.Column(input_combo_column_list, element_justification='c')]]
                 )]

    return parameters_column_list
