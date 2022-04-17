import json
import os
import time

import PySimpleGUI as sg
import pandas as pd
import numpy as np

from animation_description import generate_args, indirect
from animation.custom_animation import draw_figure
from record.json_file_checker import get_filenames_with_string_in_current_folder
from record.layout import generate_parameters_column


def generate_layout_record_player():
    layout = [[sg.Canvas(size=(640, 480), key='-CANVAS-'),
               generate_parameters_column('recording')]]
    return layout


def play_recorded_data_window():
    # The choice of the recording folder should be made directly in the plotting window
    event, values = sg.Window('Recording player - Folder',
                              [[sg.T('Select a folder'), sg.In(key='-FOLDER-'), sg.FolderBrowse()],
                               [sg.B('Start reading'), sg.B('Cancel')]]).read(close=True)
    if event == 'Start reading':
        return values['-FOLDER-']
    else:
        return False


def initialize_according_to_recording(window, json_file):
    with open(json_file, 'r') as file:
        experiment = json.load(file)
        experiment_args = experiment['experiment_parameters']

    window['-MIN-'].update(experiment_args['first_grating_idx'])
    window['-MAX-'].update(experiment_args['last_grating_idx'])
    window['-PHANTOM-'].update(experiment_args['phantom_material'])
    window['-RAIL-'].update(experiment_args['rail_material'])
    window['-RADIUS-'].update(experiment_args['compared_curvature'])

    return experiment


def update_json_file_combobox(current_folder, experiment_title, window):
    experiment_folder = '{}/{}'.format(current_folder, experiment_title)
    experiment_files = get_filenames_with_string_in_current_folder(experiment_folder, '.json')
    window['-EXP_FILE-'].update(values=experiment_files)
    return experiment_folder


def player_gui(mcf, animation_name: str):
    # Create the window
    window = sg.Window('Record player', generate_layout_record_player(),
                       location=(100, 300), finalize=True)

    # Get the Tk element from the canvas for the animation
    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    # Generate the arguments to draw the initial plot
    animation_args, animation_kwargs = generate_args(animation_name, mcf)
    fig, axs, mcf = animation_args
    # Draw the figure for the first time
    fig_agg = draw_figure(canvas, fig)

    # Load the mcf_settings
    current_folder = recording_settings['current_folder']

    # Initialize the experiment combo boxes
    experiment_list = os.listdir(current_folder)
    window['-EXP_FOLDER-'].update(values=experiment_list, value=experiment_list[0])
    experiment_folder = update_json_file_combobox(current_folder, experiment_list[0], window)

    player_args = {'play_start_time': 0, 'elapsed_time': 0, 'i_frame': 0,
                   'elapsed_time_array': np.zeros(2)}
    experiment, data_df = None, None
    i_frame = 0
    is_playing = False

    while True:
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event == '-SETTINGS-':
            # Update the main_settings
            settings = settings_window('recording')
            current_folder = settings['current_folder']
            experiment_list = os.listdir(current_folder)
            window['-EXP_FOLDER-'].update(values=experiment_list, value=experiment_list[0])
            # Update Json selector
            experiment_folder = update_json_file_combobox(current_folder, experiment_list[0], window)

        if event == '-EXP_FOLDER-':
            experiment_title = values['-EXP_FOLDER-']
            experiment_folder = update_json_file_combobox(current_folder, experiment_title, window)

        if event == '-EXP_FILE-':
            experiment_file = '{}/{}'.format(experiment_folder, values['-EXP_FILE-'])
            experiment = initialize_according_to_recording(window, experiment_file)
            data_df = pd.DataFrame.from_dict(experiment['data'])
            player_args['elapsed_time_array'] = np.array(data_df['elapsed_time'])

        if event == '-START_REC-' and experiment is not None:
            is_playing = True
            window['-TIME-'].update('Playing ...')
            i_frame = 0
            player_args['elapsed_time_array'] = data_df['elapsed_time'].to_numpy()
            player_args['play_start_time'] = time.time()
            animation_kwargs['data_player'] = data_df.iloc[i_frame]

        if event == '-STOP_REC-':
            is_playing = False

        if event in ['-MIN-', '-MAX-']:
            mcf.update_range_gratings(values['-MIN-'], values['-MAX-'])

        if event == '-RADIUS-':
            # Here do we need to have two dictionary? Why are they overlapping?
            animation_kwargs['radius_mm'] = values['-RADIUS-']

        if is_playing:
            elapsed_time = time.time() - player_args['play_start_time']
            # Update the elapsed time
            window['-TIME-'].update(format_time(elapsed_time))

            if elapsed_time > player_args['elapsed_time_array'][i_frame]:
                # Check that it is not the last frame
                if i_frame < len(player_args['elapsed_time_array']) - 1:
                    animation_kwargs['data_player'] = data_df.iloc[i_frame]
                    i_frame += 1
                # Else, stop the playing
                else:
                    is_playing = False

        # Plot the corresponding graph
        indirect(animation_name, animation_args, animation_kwargs)
        fig_agg.draw()

    return window


if __name__ == '__main__':
    # Generate layout recording
    mcf = MulticoreFiber()
    player_gui(mcf, 'main')
