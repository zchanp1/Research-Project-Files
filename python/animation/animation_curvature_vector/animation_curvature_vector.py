#!/usr/bin/env Python3

from dataclasses import dataclass, field
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt

from animation import *
from config import NB_GRATINGS_PER_CORE
from data_containers import MulticoreFiber, curvature_modulus
from data_containers.experiment import Experiment


@dataclass
class AnimationCurvatureVector(CustomAnimation):
    name: str = 'curvature_vector'

    layout: list = field(default_factory=list)
    window: sg.Window = field(init=False)
    fig: plt.Figure = field(init=False)
    axs: plt.subplot = field(init=False)

    experiment: Experiment = Experiment()
    wav_data: np.ndarray = np.array([])

    def __post_init__(self):
        super().__init__(self.name)
        self.mcf = MulticoreFiber()

        self.generate_layout()
        self.window = sg.Window('Plotting window', self.layout, finalize=True)

        # Get the Tk element from the canvas for the animation
        self.fig, self.axs = plt.subplots(ncols=1, nrows=2, figsize=(8, 8))
        canvas_elem = self.window['-CANVAS-'].TKCanvas
        self.fig_agg = draw_figure(canvas_elem, self.fig)

    def generate_layout(self):
        self.layout = [[sg.Canvas(size=(640, 480), key='-CANVAS-')]]

    def set_figure_layout(self):
        # Initialize the plot
        for i_ax in range(len(self.axs)):
            self.axs[i_ax].clear()
            self.axs[i_ax].set_ylim([-0.3, 0.3])
            self.axs[i_ax].minorticks_on()
            self.axs[i_ax].grid(color='black', linestyle='--', linewidth=0.5)
            self.axs[i_ax].grid(which='minor', color='grey', linestyle='--', linewidth=0.5)

        ax = self.axs[0]
        ax.set_ylabel('Curvature $cm^{-1}$')

        ax = self.axs[1]
        ax.set_ylabel('Curvature $cm^{-1}$')

        plt.xlabel("Grating index")

    def animate(self, *args):
        # Set the x, y values according to the new fbgs wav_data
        grating_indexes = range(NB_GRATINGS_PER_CORE)

        # Get a line of data
        if self.type == 'recorder':
            self.mcf.update_current_labview_data()
        else:
            self.mcf.update_current_labview_data(self.wav_data)

        curvatures_avg = np.transpose(self.mcf.calculate_curvature_vector())

        # Compute the curvature vector
        curvatures_avg_nx = curvatures_avg[0] * 10 ** -2  # 1/cm
        curvatures_avg_ny = curvatures_avg[1] * 10 ** -2  # 1/cm

        # Compute the curvature modulus
        modulus = curvature_modulus(np.transpose(curvatures_avg)) * 10 ** -2  # 1/cm

        # Initialize the plot
        self.set_figure_layout()

        # Plot the curvature vector
        self.axs[0].plot(grating_indexes, curvatures_avg_nx, label='Curvature $n_x$', marker='o', ms=2)
        self.axs[0].plot(grating_indexes, curvatures_avg_ny, label='Curvature $n_y$', marker='o', ms=2)

        self.axs[1].plot(grating_indexes, modulus, label='Curvature modulus', marker='o', ms=2)

        self.axs[0].legend(loc='upper right')
        self.axs[1].legend(loc='upper right')
        self.fig_agg.draw()

    def gui(self):
        while True:
            event, values = self.window.read(timeout=1)

            # Update the plot
            self.animate()

            if event in (sg.WIN_CLOSED, '-STOP_REC-'):
                break

        self.window.close()


if __name__ == '__main__':
    custom_animation = AnimationCurvatureVector()
    custom_animation.gui()
