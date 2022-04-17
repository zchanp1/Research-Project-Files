import PySimpleGUI as sg


from animation import *


def generate_layout():
    # Define the window layout
    layout = [
        [sg.Text("Plot animation", size=(30, 1), font=("Helvetica", 30), justification='c', relief=sg.RELIEF_RIDGE),
         settings_button()],
        [sg.Text('Select animation : '),
         sg.InputCombo(tuple(list_of_animation), default_value='main',
                       enable_events=True, size=(40, 1), key='-ANI-')],
        [sg.Text('Data source : '), sg.Radio('Real time data', "RADIO1", default=True, key='-REAL_TIME-'),
         sg.Radio('Record player', "RADIO1")],
        [sg.Button('Launch', size=(30, 1)), sg.Button('Set zero point', size=(20, 1), key='-ZERO-')],
        [sg.Column([[sg.Button('Exit')]], justification='r')],
    ]
    return layout


def create_window():
    # Create the form and show it without the plot
    window = sg.Window(
        "Animation GUI",
        generate_layout(),
        location=(0, 0),
        finalize=True,
        font="Helvetica 18",
    )
    return window


def main():
    # First, create the window
    window = create_window()
    # Then, initialize the MulticoreFiber
    mcf = MulticoreFiber()

    animation_name = window['-ANI-'].get()
    ani = CustomAnimation(animation_name)

    # Then, initialize the MulticoreFiber
    while True:
        event, values = window.read()

        # Close the windows
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == '-SETTINGS-':
            settings_window()
            break
        # Update the animation according to the selected animation name
        if event == '-ANI-':
            animation_name = values['-ANI-']
            ani.update_name(animation_name)

        # Update the reference wavelength before starting any animation
        if event == '-ZERO-':
            mcf.update_wav0()

        # Launch the animation
        if event == 'Launch':
            mode = values['-REAL_TIME-']

            if mode:
                # Launch animation to stream real time data
                recorder_gui(mcf, ani.name)
            else:
                # Launch animation to stream real time data
                player_gui(mcf, ani.name)

    window.close()


if __name__ == '__main__':
    main()
