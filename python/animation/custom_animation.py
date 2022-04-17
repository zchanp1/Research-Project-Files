from dataclasses import dataclass, field
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data_containers import MulticoreFiber, MulticoreFiber2


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


@dataclass
class CustomAnimation:
    """Object for creating an animation"""
    name: str
    mcf: MulticoreFiber or MulticoreFiber2 = MulticoreFiber2()
    type: str = 'recorder'

    fig_agg: FigureCanvasTkAgg = field(init=False)

    def animate(self, *args):
        pass

    def update_name(self, name):
        self.name = name

    def print_name(self):
        print('Animation name: ', self.name)

    def generate_animation_args(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    custom_animation = CustomAnimation('Localization')
    custom_animation.print_name()
