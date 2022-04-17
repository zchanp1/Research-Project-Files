import os
from datetime import datetime
import time

import PySimpleGUI as sg

# Yet another usage of MatPlotLib with animations.
from data_containers.experiment import Experiment
from data_containers.experiment_parameters import ExperimentParameters
from fbgs_converter.config import *
from fbgs_converter.animations.animation_description import indirect, generate_args
from data_containers import MulticoreFiber

from fbgs_converter.others.time_formatting import format_time, format_date
from fbgs_converter.animations.plotting import draw_figure, plot_curvature_ground_truth, plot_ground_truth_positions_2d
from fbgs_converter.record.scripts.json_file_checker import check_experiment_arguments, recording_window

from fbgs_converter.record.scripts.layout import generate_parameters_column


def start_recording(experiment_args):
    """ Initializes the Experiment container and starts the recording """
    # Get the current date and time
    date = format_date(datetime.now())
    experiment_start_time = time.time()

    # Generate the experiment header with the experiment parameters
    experiment_header = ExperimentParameters(
        experiment_args['experiment_title'], experiment_args['iteration'],
        date, experiment_start_time,
        experiment_args['rail_material'], experiment_args['phantom_material'], experiment_args['compared_curvature'],
        experiment_args['first_grating_idx'], experiment_args['last_grating_idx'], experiment_args['wav0'])

    # Generate the experiment container
    experiment = Experiment(experiment_header)
    experiment.start_recording()
    experiment.set_recording_file(experiment_args['json_file'])

    return experiment


def stop_to_record(experiment: Experiment, experiment_args: dict):
    # Save the recording in selected JSON file
    experiment.to_temp_file()

    # Validate the recording
    is_valid_recording = validate_recording_popup()

    # 'Yes' - Action to perform if the recording went well
    if is_valid_recording == 'Yes':

        # If no recording file selected, force the users to choose one
        if not experiment.recording_file:
            event_rec = ''
            # Create a popup to let the user choose a file
            while not experiment.recording_file:
                # Break on Cancel
                if event_rec == 'Cancel':
                    break
                event_rec, experiment = select_recording_file_popup(experiment)

        # Save the recording in selected JSON file
        experiment.to_json_file()

    # 'Start again' - Offer the chance to record again with the same parameters
    elif is_valid_recording == 'Start again':
        experiment = start_recording(experiment_args)

    # 'Discard' - Stop recording if there was an issue
    else:
        print('Deleted', experiment_args['json_file'])
        os.remove(experiment_args['json_file'])

    return experiment


def validate_recording_popup():
    """ Basic interface. Allow the user to validate the data, start the experiment again or just discard it."""
    event, values = sg.Window('Data validation',
                              [[sg.Text('How do you rate the localization')],
                               [sg.B('Excellent'), sg.B('Poor'), sg.B('Unclear'), sg.B('Discard')]],
                              element_justification='center').read(close=True)

    return event


def select_recording_file_popup(experiment):
    # Create the window until a file was not selected
    event_rec, values_rec = sg.Window('Recording file',
                                      [[sg.Text('Choose a JSON file :')],
                                       [sg.InputText(key='json_file'), sg.FileBrowse()],
                                       [sg.Submit(), sg.Cancel()]]).read(close=True)

    experiment.set_recording_file(values_rec['json_file'])

    return event_rec, experiment


def generate_layout(animation_name: str):
    # define the form layout
    if animation_name in ['frenet_serret_2d', 'frenet_serret_all', 'test_main',
                          'main', 'curv_and_pos_curvature_data']:

        layout = [[sg.Canvas(size=(640, 480), key='-CANVAS-'),
                   generate_parameters_column()]]

    else:
        layout = [[sg.Canvas(size=(640, 480), key='-CANVAS-')],
                  [sg.Button('Exit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')]]

    return layout


def recorder_gui(mcf: MulticoreFiber, animation_name: str):
    # Generate the window layout
    layout = generate_layout(animation_name)
    # Create the window
    window = sg.Window('Plotting window', layout, location=(100, 300), finalize=True)

    # Get the Tk element from the canvas for the animation
    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    # Generate the arguments to draw the initial plot
    animation_args, animation_kwargs = generate_args(animation_name, mcf)
    fig, axs, mcf = animation_args
    # Draw the figure for the first time
    fig_agg = draw_figure(canvas, fig)

    # Initialize mcg arguments dictionary with None values
    experiment_args = dict.fromkeys(EXPERIMENT_ARGS)
    _, values = window.read(timeout=1)
    experiment_args.update({'first_grating_idx': values['-MIN-'], 'last_grating_idx': values['-MAX-']})

    experiment = Experiment()

    while True:
        event, values = window.read(timeout=10)

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        # Plot the corresponding graph
        indirect(animation_name, animation_args, animation_kwargs)
        fig_agg.draw()

        if event == '-PHANTOM-':
            experiment_args['phantom_material'] = values['-PHANTOM-']

        if event == '-RAIL-':
            experiment_args['rail_material'] = values['-RAIL-']

        if event == '-RADIUS-':
            # Here do we need to have two dictionary? Why are they overlapping?
            radius_mm = values['-RADIUS-']
            experiment_args['compared_curvature'] = radius_mm

            # Update the compared curvature when the radius it changed
            plot_curvature_ground_truth(axs, radius_mm, mcf.range_gratings)
            plot_ground_truth_positions_2d(mcf, radius_mm, axs[1])

        if event in ['-MIN-', '-MAX-']:
            first_grating_idx, last_grating_idx = values['-MIN-'], values['-MAX-']
            mcf.update_range_gratings(first_grating_idx, last_grating_idx)
            experiment_args.update({'first_grating_idx': first_grating_idx, 'last_grating_idx': last_grating_idx})

        # Event "Start recording"
        if event == '-START_REC-' and not experiment.is_recording:
            # Generate the experiment title and select the saving file in recording window popup
            if check_experiment_arguments(experiment_args):
                experiment_args, start = recording_window(experiment_args)
                # Initialize and start the experiment
                if start:
                    experiment_args['wav0'] = mcf.wav0
                    experiment = start_recording(experiment_args)

        # Event "Stop recording"
        if experiment.stop_recording(event):
            experiment = stop_to_record(experiment, experiment_args)

        # While recording
        if experiment.is_recording:
            # Update the elapsed time
            window['-TIME-'].update(format_time(experiment.get_elapsed_time()))
            # Record a line of data
            experiment.record_aline_data(mcf)

        if event == '-WAV0-':
            mcf.update_wav0()

    window.close()


if __name__ == '__main__':
    mutlicore_fiber = MulticoreFiber()
    recorder_gui(mutlicore_fiber, 'main')
