from dataclasses import dataclass, field

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

import PySimpleGUI as sg

from config import LOCALIZATION_EXPERIMENT_ARGS_TO_KEY
from data_containers import MulticoreFiber
from data_containers.experiment import Experiment

from record import *


def generate_recording_frame():
    recording_frame = [sg.Frame('Experiment',
                                [[sg.Text('Select experiment folder ')],
                                 [sg.InputCombo(tuple(), size=(25, 1), key='-EXP_FOLDER-', enable_events=True)],
                                 [sg.Text('Select json file : ')],
                                 [sg.InputCombo(tuple(), size=(25, 1), key='-EXP_FILE-', enable_events=True)]])]
    return recording_frame


def basic_player_layout():
    layout = [
        [sg.Text('Record player', font='Any 20')],
        generate_recording_frame(),
        generate_recording_layout()]

    return layout


def update_json_file_combobox(current_folder, experiment_title, window):
    experiment_folder = '{}/{}'.format(current_folder, experiment_title)
    experiment_files = get_filenames_with_string_in_current_folder(experiment_folder, '.json')
    window['-EXP_FILE-'].update(values=experiment_files)
    return experiment_folder


def generate_layout():
    return basic_player_layout()


@dataclass
class RecordingPlayer:
    """Object for creating an animation"""
    name: str
    mcf: MulticoreFiber = field(init=False)
    type: str = 'recorder'

    window: sg.Window = field(init=False)
    fig_agg: FigureCanvasTkAgg = field(init=False)

    selected_json_file: str = ''

    def __post_init__(self):
        self.mcf = MulticoreFiber() if self.name == 'curvature_vector' else MulticoreFiber2()

    def animate(self, *args):
        return

    def update_name(self, name):
        self.name = name

    def print_name(self):
        print('Animation name: ', self.name)

    def generate_animation_args(self, *args, **kwargs):
        pass

    def initialize_according_to_recording(self):
        with open(self.selected_json_file, 'r') as file:
            # Generate an experiment object from the loaded file
            experiment = Experiment(json.load(file))

            # Get the experiment args as a dictionnary
            experiment_args = experiment.experiment_parameters.to_dict()

        # Update the window according to experiment arguments and known keys
        for key, value in LOCALIZATION_EXPERIMENT_ARGS_TO_KEY.items():
            self.window[value].update(experiment_args[key])

        return experiment

    def gui(self):
        while True:
            event, values = self.window.read(timeout=10)

            if event == sg.WIN_CLOSED:
                break

        self.window.close()


if __name__ == '__main__':
    custom_animation = RecordingPlayer('Localization')
    custom_animation.gui()
