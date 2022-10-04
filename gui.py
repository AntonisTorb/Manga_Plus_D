import PySimpleGUI as sg
from pathlib import Path
from user_messages import multiline_error_handler

FONT = ("Arial", 14)
APP_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
DEFAULT_MANGA_DIR = APP_DIR / "Manga"
DEFAULT_FF_DRIVER_PATH = APP_DIR / "geckodriver.exe"
DEFAULT_GC_DRIVER_PATH = APP_DIR / "chromedriver.exe"
ROOT_TITLE_URL = "https://mangaplus.shueisha.co.jp/titles/"
ROOT_CHAPTER_URL = "https://mangaplus.shueisha.co.jp/viewer/"

#sg.theme("DarkGrey5")
sg.theme("DarkBlue12")
manga_dir_layout = [
    [sg.Text("Specify Download directory:"), 
        sg.Input(default_text=DEFAULT_MANGA_DIR, key = "-DL_DIR-", expand_x=True, disabled=True, disabled_readonly_background_color="#86a6df"), 
        sg.Button("Browse", key= "-BROWSE_DL_DIR-")]
]
column_1 = [
    [sg.Radio("Google Chrome", group_id="browser", default=True, key="-GC-")],
    [sg.Radio("Mozilla Firefox", group_id="browser", key="-FF-")]
]
column_2 = [
    [sg.Push(), sg.Text("Specify delay between 0.1 and 10 seconds:"), sg.Push()], 
    [sg.Push(), sg.Input(default_text=0.5, size=(5, 1), key="-DELAY-"), sg.Push()]
]
options_layout = [
    [sg.Push(), sg.Text("Specify browser:"), sg.Column(column_1, expand_x=True), sg.VerticalSeparator(), sg.Column(column_2, expand_x=True)],
    [sg.HorizontalSeparator()],
    [sg.Text("Specify driver:"), 
        sg.Input(default_text=DEFAULT_GC_DRIVER_PATH, key="-DRIVER-", expand_x=True, disabled=True, disabled_readonly_background_color="#86a6df"), 
        sg.Button("Browse", key= "-BROWSE_DRIVER-")]
]
links_layout = [
    [sg.Text("Get chapter links from Manga title URL:")],
    [sg.Input(key = "-TITLE_URL-", expand_x=True), sg.Button("Get Links")],
    [sg.Text("Or paste them below, one URL on each line.")],
    [sg.Multiline(key="-CHAPTER_URLS-", expand_x=True, expand_y=True)]
]
layout = [
    [sg.Frame("Download Directory", manga_dir_layout, expand_x=True)],
    [sg.Frame("Options", options_layout, expand_x=True)],
    [sg.Frame("Links", links_layout, expand_x=True, expand_y=True)],
    [sg.Push(), sg.Button("Download chapter(s)", key="-DOWNLOAD-"), sg.Push()]
]


def get_browser(values: dict) -> str:
    '''Returns a string representation of the browser to use according to user input.'''

    if values["-GC-"]:
        return "gc"
    elif values["-FF-"]:
        return "ff"


window = sg.Window("M+D", layout, font=FONT, enable_close_attempted_event= True, finalize=True, size=(900, 600))

while True:
    event, values = window.read()
    match event:
        case sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            break
        case "-BROWSE_DL_DIR-":
            dl_dir = Path(sg.popup_get_folder("", no_window=True))
            print(dl_dir)
            if dl_dir:
                window.Element("-DL_DIR-").update(dl_dir)
        case "-BROWSE_DRIVER-":
            driver_path = Path(sg.popup_get_file("", file_types=(("Windows Executable File", "*.exe"),), no_window= True))
            if driver_path:
                window.Element("-DRIVER-").update(driver_path)
        case "Get Links":
            title_url = values["-TITLE_URL-"]
            if not title_url:
                multiline_error_handler(["Please provide a Manga title URL."])
            elif not title_url.startswith(ROOT_TITLE_URL):
                multiline_error_handler(["Please provide a valid Manga title URL.", f"The manga title URL must start with: '{ROOT_TITLE_URL}'"])
            else:
                pass  # Get chapter links from Manga title URL.
        case "-DOWNLOAD-":
            try:
                links = str(values["-CHAPTER_URLS-"]).splitlines()
                browser = get_browser(values)

                try:
                    delay = float(values["-DELAY-"])
                except ValueError:
                    raise ValueError
                driver_path = Path(values["-DRIVER-"])

                valid_links = True
                for link in links:
                    if not link.startswith(ROOT_CHAPTER_URL):
                        valid_links = False
                
                if not links:
                    multiline_error_handler(["Please provide at least one chapter link."])
                elif not valid_links:
                    multiline_error_handler(["Please ensure that all chapter links are valid.", f"All chapter URLs must start with: '{ROOT_CHAPTER_URL}'"])
                elif ((browser == "gc" and not str(driver_path).endswith("chromedriver.exe")) or
                    (browser == "ff" and not str(driver_path).endswith("geckodriver.exe"))):
                    multiline_error_handler(["Please select the correct driver for the selected browser."])
                elif delay < 0.1 or delay > 10:
                    multiline_error_handler(["Please ensure that the delay is between 0.1 and 10 seconds."])
                else:
                    pass  # Have 2 progress bars and some text showing the progress for total chapters and currect chapter. 
            except ValueError:
                multiline_error_handler(["Please ensure that the delay is a number between 0.1 and 10."])
window.close()