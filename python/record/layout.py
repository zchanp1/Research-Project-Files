import PySimpleGUI as sg

from config import NB_GRATINGS_PER_CORE, phantom_materials, rail_materials, radii_list
from icons import play, stop, pause


def create_parameters_column_list():
    label_column_list = [[sg.Text('First grating : ')], [sg.Text('Last grating : ')], [sg.Text('Phantom material: ')],
                         [sg.Text('Rail material:')], [sg.Text('Curvature (1/mm):')]]

    grating_index_tuple = tuple(range(NB_GRATINGS_PER_CORE))
    input_combo_column_list = [
        [sg.InputCombo(grating_index_tuple, default_value=0,
                       enable_events=True, size=(7, 1),
                       key='-MIN-')],
        [sg.InputCombo(grating_index_tuple, default_value=NB_GRATINGS_PER_CORE - 1,
                       enable_events=True, size=(7, 1),
                       key='-MAX-')],
        [sg.InputCombo(phantom_materials, default_value=phantom_materials[0],
                       enable_events=True, size=(7, 1),
                       key='-PHANTOM-')],
        [sg.InputCombo(rail_materials, default_value=rail_materials[0],
                       enable_events=True, size=(7, 1),
                       key='-RAIL-')],
        [sg.InputCombo(radii_list, default_value=radii_list[0],
                       enable_events=True, size=(7, 1),
                       key='-RADIUS-')]]

    parameters_column_list = [[
        sg.Frame('Parameters', [[sg.Column(label_column_list, element_justification='l'),
                                 sg.Column(input_combo_column_list, element_justification='c')]]
                 )]]

    return parameters_column_list


def generate_recording_layout():
    recording_layout = [sg.Frame('Record',
                                 [[sg.Button(image_data=play,
                                             button_color=(sg.theme_background_color(), sg.theme_background_color()),
                                             border_width=0, key='-START_REC-'),
                                   sg.Button(image_data=pause,
                                             button_color=(sg.theme_background_color(), sg.theme_background_color()),
                                             border_width=0, key='-PAUSE-'),
                                   sg.Button(image_data=stop,
                                             button_color=(sg.theme_background_color(), sg.theme_background_color()),
                                             border_width=0, key='-STOP_REC-')],
                                  [sg.Text('Elapsed time :'), sg.Text('', key='-TIME-', size=(10, 1))]]
                                 )]
    return recording_layout


def generate_parameters_column(euclidean_dist=False):
    layout = [[sg.Text('Experiment recorder', font='Any 20')]]
    post_layout = [generate_recording_layout(),
                   [sg.B('Update reference wavelength', key='-WAV0-')],
                   [sg.Button('Exit')]]

    if euclidean_dist:
        post_layout.insert(0, [sg.Text('Euclidean distances:'), sg.Button('Calculate')])

    # Stacking everything together
    parameters_column = create_parameters_column_list()
    layout.extend(parameters_column)
    layout.extend(post_layout)

    return sg.Column(layout)


if __name__ == '__main__':
    window = sg.Window('Parameter column', layout=[[generate_parameters_column()]])

    while True:
        event, values = window.read(timeout=10)

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
