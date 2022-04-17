import os

import PySimpleGUI as sg

from config import mcf_settings, recording_settings
from settings import settings_window, settings_button

recording_abs_path = os.path.abspath("../recordings").replace('\\', '/')
radio_button_key_list = ['radio{}'.format(iter) for iter in range(1, 6)]


def generate_experiment_title(mcf_args_dict: dict, iteration: int = None):
    # Retrieve each argument from mcf_args_dict
    rail = str(mcf_args_dict['rail_material']).lower()
    phantom = str(mcf_args_dict['phantom_material']).lower()
    curvature = str(mcf_args_dict['compared_curvature']).lower()

    # Compile the name from each arguments in a name
    if iteration:
        recording_name = '{}_{}_{}_iter{}'.format(rail, phantom, curvature, iteration)
    else:
        recording_name = '{}_{}_{}'.format(rail, phantom, curvature)

    return recording_name


def check_experiment_arguments(experiment_args: dict):
    no_none_in_args = True
    none_args = [key for key, arg in experiment_args.items() if arg is None]

    if none_args:
        sg.popup('You forgot to select:', none_args)
        no_none_in_args = False
    return no_none_in_args


def update_selected_filename(experiment_iteration, natsort_filenames, window):
    for i_csv in natsort_filenames:
        if 'iter{}'.format(experiment_iteration) in i_csv:
            window['-JSON-'].update(value=i_csv)


def get_relative_current_folder_path(current_folder: str):
    """ Return only the relative current folder path fro display. """
    path_idx = current_folder.rfind('/recordings')
    relative_current_folder_path = current_folder[path_idx + len('/recordings'):]
    return relative_current_folder_path


def get_filenames_with_string_in_current_folder(current_folder_path: str, string_to_find: str):
    return [file for file in os.listdir(current_folder_path) if string_to_find in file]


def find_experiment_iteration(current_folder_path, experiment_title):
    experiment_filenames = get_filenames_with_string_in_current_folder(current_folder_path, experiment_title)
    nb_filenames = len(experiment_filenames)
    if nb_filenames < 5:
        return len(experiment_filenames) + 1
    else:
        return 5


def open_recording_file(filepath):
    try:
        f = open(filepath, 'x')
        f.close()
    except IOError as error:
        print(error)
    return


def create_folder_if_needed(current_folder, experiment_title):
    path = os.path.join(current_folder, experiment_title)
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)
    return path


# Window and layout for the GUI
def generate_file_selector_layout(experiment_folder: str, experiment_title: str):
    # Get the relative current folder path in a better looking format
    current_folder_path = get_relative_current_folder_path(experiment_folder)

    # Find all the json file so they can be displayed in the InputCombo
    filenames = get_filenames_with_string_in_current_folder(experiment_folder, '.json')

    # Create the radio button list in case you want to choose another iteration
    radio_buttons_list = [sg.Radio(str(iter), key='radio{}'.format(iter), group_id='-ITER-', enable_events=True)
                          for iter in range(1, 6)]

    left_column = [[sg.T('Current folder : ')],
                   [sg.T('Experiment title : ')],
                   [sg.T('Experiment iteration: ')],
                   [sg.T('Select JSON file : ')]]

    right_column = [[sg.T(current_folder_path, key='-FOLDER-', enable_events=True)],
                    [sg.T(experiment_title, key='-EXP_TITLE-')],
                    radio_buttons_list,
                    [sg.InputCombo(values=filenames, size=(40, 1), key='-JSON-', enable_events=True,
                                   default_value='{}.json'.format(experiment_title))]]

    recording_layout = [
        [sg.T('JSON file selector', font='Any 15'),
         sg.Column([[settings_button(2)]], element_justification='r', expand_x=True, expand_y=True)],
        [sg.Column(left_column, element_justification='l'), sg.Column(right_column, element_justification='l')],
        [sg.B('Start recording'), sg.B('Cancel')]]

    return recording_layout, filenames


def update_combo_box(window, iteration):
    for i_radio in range(5):
        window[radio_button_key_list[i_radio]].update(False)
    key = radio_button_key_list[iteration-1]
    window[key].update(True)
    return


def recording_window(experiment_args: dict):
    # Load the main_settings
    current_folder = recording_settings['current_folder']

    # Choose and create the file from previous experiments
    experiment_title = generate_experiment_title(experiment_args)
    create_folder_if_needed(current_folder, experiment_title)
    experiment_folder = '{}/{}'.format(current_folder, experiment_title)

    # Find the experiment iteration and append the name to the experiment title
    experiment_iteration = find_experiment_iteration(experiment_folder, experiment_title)

    # Generate the full experiment title and filename
    full_experiment_title = "{}_iter{}".format(experiment_title, experiment_iteration)
    full_experiment_filename = '{}/{}.json'.format(experiment_folder, full_experiment_title)

    # Automatically create the file if it never was
    open_recording_file(full_experiment_filename)

    # Generate the layout and the window
    recording_layout, natsort_filenames = generate_file_selector_layout(experiment_folder, full_experiment_title)
    window = sg.Window('File checker', recording_layout, finalize=True, location=(300, 50))

    update_combo_box(window, experiment_iteration)
    start = True

    # Looping
    while True:  # Event Loop
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            start = False
            print('Deleted', full_experiment_filename)
            os.remove(full_experiment_filename)
            break

        if event == '-SETTINGS-':
            # Update the main_settings
            settings = settings_window('recording')

            # Compare the previous main_settings to the old one
            settings_current_folder = get_relative_current_folder_path(settings['current_folder'])
            window_current_folder = window['-FOLDER-'].get()

            # Update the folder relative path if different
            if settings_current_folder != window_current_folder:
                window['-FOLDER-'].update(value=settings_current_folder)

                # Update the list of filenames according to the new experiment path
                current_folder_full_path = recording_abs_path + '/' + settings_current_folder
                natsort_filenames = get_filenames_with_string_in_current_folder(current_folder_full_path, '.json')
                window['-JSON-'].update(values=natsort_filenames)

                # Update the selected filename according to the selected iteration
                update_selected_filename(experiment_iteration, natsort_filenames, window)

        if event in radio_button_key_list:
            'Update the iter name and the corresponding file'
            experiment_iteration = int(event.strip('radio'))
            full_experiment_title = generate_experiment_title(experiment_args, experiment_iteration)
            window['-EXP_TITLE-'].update(full_experiment_title)

            # Update the selected filename according to the selected iteration
            update_selected_filename(experiment_iteration, natsort_filenames, window)

        if event == '-JSON-':
            combo_value = values['-JSON-']
            full_experiment_filename = '{}/{}'.format(experiment_folder, values['-JSON-'])

            # Update experiment iteration
            experiment_iteration = int(combo_value[values['-JSON-'].find('iter')+len('iter'):].rstrip('.json'))
            update_combo_box(window, experiment_iteration)

        if event == 'Start recording':
            # Save the recording arguments before starting the recording
            experiment_args['json_file'] = full_experiment_filename
            experiment_args['experiment_title'] = experiment_title
            experiment_args['iteration'] = experiment_iteration
            # Break the loop
            break

    # Close the window
    window.close()

    # Return the gathered recording arguments
    return experiment_args, start


if __name__ == '__main__':
    mcf_args_dict = {'phantom_material': 'Eco30', 'rail_material': 'DS10', 'compared_curvature': 90,
                     'first_grating_idx': 3, 'last_grating_idx': 5}

    # Test the recording function
    recording_window(mcf_args_dict)

    # Test the data validation popup
    # is_validated = validate_recording_popup()

    # Test the check dictionary
    # mcf_args_dict = {'phantom_material': None, 'rail_material': None, 'compared_curvature': 90,
    #                  'first_grating_idx': 3, 'last_grating_idx': 5}
    # check_experiment_arguments(mcf_args_dict)


