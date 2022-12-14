from .global_constants import FONT
import PySimpleGUI as sg  # pip install PySimpleGUI


def multiline_error_handler(string_list: list[str]) -> None:
    '''Displays window with an error message. Each string in the provided string_list appears in a new line.'''

    sg.Window("ERROR!", [
        [[sg.Push(), sg.Text(text), sg.Push()] for text in string_list],
        [sg.Push(), sg.OK(), sg.Push()]
    ], font= FONT, icon= "icon.ico", modal= True).read(close= True)


def multiline_warning_handler(string_list: list[str]) -> None:
    '''Displays window with a warning message. Each string in the provided string_list appears in a new line.'''

    sg.Window("Warning", [
        [[sg.Push(), sg.Text(text), sg.Push()] for text in string_list],
        [sg.Push(), sg.OK(), sg.Push()]
    ], font= FONT, icon= "icon.ico", modal= True).read(close= True)


def operation_successful(text: str) -> None:
    '''Displays window when an operation completes successfully.'''

    sg.Window("Success", [
            [sg.Push(), sg.Text(text), sg.Push()],
            [sg.Push(), sg.OK(), sg.Push()]
    ], font= FONT, icon= "icon.ico", modal= True).read(close= True)
