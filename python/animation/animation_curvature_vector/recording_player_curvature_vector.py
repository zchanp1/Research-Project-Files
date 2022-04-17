import os

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg

from animation import AnimationCurvatureVector, RecordingPlayer, basic_player_layout
from animation.animation_curvature_vector.localization_common import create_localization_column
from config import recording_settings

current_recording_folder = recording_settings['current_folder']
plt.rcParams.update(mpl.rcParamsDefault)


@dataclass
class RecordingPlayerLocalization(RecordingPlayer, AnimationCurvatureVector):
    """Object for creating an animation"""
    name: str = 'curvature_vector'
    type: str = 'player'

    selected_phantom_folder: str = 'dvrk_side_sliding'
    selected_experiment_folder: str = ''

    is_playing: bool = False
    i_frame: int = 0
    start_time: datetime = datetime.now()
    elapsed_time: timedelta = datetime.now() - start_time
    next_time_delta: timedelta = field(init=False)

    def update_experiment_id_combobox(self):
        experiment_title_list = os.listdir(self.selected_phantom_folder)

        experiment_id_list = [int(folder.split('_')[-1]) for folder in experiment_title_list]

        self.window['-ID-'].update(values=experiment_id_list, value=experiment_id_list[0])

        self.update_selected_experiment(experiment_title_list[0])

    def update_selected_experiment(self, selected_experiment_title):
        # Select the first JSON file available
        self.selected_experiment_folder = os.path.join(self.selected_phantom_folder, selected_experiment_title)

        experiment_files = os.listdir(self.selected_experiment_folder)
        json_file_title = experiment_files[1]

        # Concatenate the full path
        self.selected_json_file = os.path.join(self.selected_experiment_folder, json_file_title)

        # Update the window
        self.experiment = self.initialize_according_to_recording()

    def __post_init__(self):
        super().__post_init__()
        AnimationCurvatureVector.__post_init__(self)
        self.type = 'player'

        # Initialize the experiment combo boxes
        phantom_folder_list = os.listdir(current_recording_folder)
        self.window['-EXP_FOLDER-'].update(values=phantom_folder_list, value=self.selected_phantom_folder)

        phantom_material_folder_list = os.listdir(os.path.join(current_recording_folder, self.selected_phantom_folder))
        self.window['-EXP_FILE-'].update(values=phantom_material_folder_list, value=phantom_material_folder_list[0])

        # Update the current experiment folder from selection
        self.selected_phantom_folder = os.path.join(current_recording_folder, self.selected_phantom_folder,
                                                    phantom_material_folder_list[0])

        # Update the experiment that can be selected according to
        self.update_experiment_id_combobox()

    def generate_layout(self):
        right_column = basic_player_layout() + [create_localization_column()]
        self.layout = [[sg.Canvas(size=(640, 480), key='-CANVAS-'), sg.Column(right_column)]]
        return self.layout

    def animate(self, values):
        # Print updating wav_data
        self.wav_data = np.array(self.experiment.data[self.i_frame].get('wav_data'))
        AnimationCurvatureVector.animate(self, values)

    def gui(self):
        while True:
            event, values = self.window.read(timeout=10)

            if event == sg.WIN_CLOSED:
                break

            if event == '-EXP_FOLDER-':
                phantom_material_folder_list = os.listdir(os.path.join(current_recording_folder,
                                                                       values['-EXP_FOLDER-']))

                self.window['-EXP_FILE-'].update(values=phantom_material_folder_list,
                                                 value=phantom_material_folder_list[0])

                # Update the current experiment folder from selection
                self.selected_phantom_folder = os.path.join(current_recording_folder, values['-EXP_FOLDER-'],
                                                            phantom_material_folder_list[0])

                # Update the experiment that can be selected according to
                self.update_experiment_id_combobox()

            if event == '-EXP_FILE-':
                # Update the experiment that can be selected according to
                self.selected_phantom_folder = os.path.join(current_recording_folder, values['-EXP_FOLDER-'],
                                                            values['-EXP_FILE-'])

                # Update the experiment that can be selected according to
                self.update_experiment_id_combobox()

            if event == '-ID-':
                selected_experiment_title = [file for file in os.listdir(self.selected_phantom_folder)
                                             if str(values['-ID-']) in file.split('_')[-1]][0]
                self.update_selected_experiment(selected_experiment_title)

            if event == '-START_REC-':
                self.is_playing = True
                self.window['-TIME-'].update('Playing ...')
                self.i_frame = 0
                self.next_time_delta = timedelta(seconds=self.experiment.data[self.i_frame + 1]['elapsed_time'])
                self.start_time = datetime.now()

            if event == '-PAUSE-':
                self.is_playing = False

            if event == '-STOP_REC-':
                self.is_playing = False

            if self.is_playing:
                # Update the elapsed time and show it
                self.elapsed_time = datetime.now() - self.start_time
                self.window['-TIME-'].update(self.elapsed_time)

                if self.elapsed_time > self.next_time_delta:
                    # Check that it is not the last frame
                    if self.i_frame < len(self.experiment.data) - 1:
                        self.i_frame += 1
                        self.next_time_delta = timedelta(seconds=self.experiment.data[self.i_frame]['elapsed_time'])
                    # Else, stop the playing
                    else:
                        self.is_playing = False

                self.animate(values)

        self.window.close()


if __name__ == '__main__':
    animation = RecordingPlayerLocalization()
    animation.gui()
