from binascii import a2b_base64
import PySimpleGUI as sg
from pathlib import Path
import re
from time import sleep
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, InvalidArgumentException, 
    ElementClickInterceptedException, ElementNotInteractableException)
from scripts import (FONT, ROOT_TITLE_URL, ROOT_CHAPTER_URL, COOKIE_XPATH, SLEEP_SECONDS, 
    CHAPTER_XPATH, TITLE_XPATH, CHAPTER_NO_XPATH, PAGES_XPATH, ILLEGAL_CHARACTERS, PAGE_XPATH,
    multiline_error_handler, operation_successful)


APP_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
DEFAULT_MANGA_DIR = APP_DIR / "Manga"


def get_main_layout() -> list[list[sg.Element]]:
    '''Returns the PySimpleGUI layout for the main window.'''

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
        [sg.Push(), sg.Input(default_text=SLEEP_SECONDS, size=(5, 1), key="-DELAY-"), sg.Push()]
    ]
    options_layout = [
        [sg.Push(), sg.Text("Specify browser:"), sg.Column(column_1, expand_x=True), sg.VerticalSeparator(), sg.Column(column_2, expand_x=True)],
        [sg.HorizontalSeparator()],
        [sg.Text("Specify driver:"), 
            sg.Input(key="-DRIVER-", expand_x=True, disabled=True, disabled_readonly_background_color="#86a6df"), 
            sg.Button("Browse", key= "-BROWSE_DRIVER-")]
    ]
    links_layout = [
        [sg.Text("Get chapter links from Manga title URL:")],
        [sg.Input(key = "-TITLE_URL-", expand_x=True), sg.Button("Get Links")],
        [sg.Text("Or paste them below, one URL on each line.")],
        [sg.Multiline(auto_refresh= True, key="-CHAPTER_URLS-", expand_x=True, expand_y=True)]
    ]
    layout = [
        [sg.Frame("Download Directory", manga_dir_layout, expand_x=True)],
        [sg.Frame("Options", options_layout, expand_x=True)],
        [sg.Frame("Links", links_layout, expand_x=True, expand_y=True)],
        [sg.Push(), sg.Button("Download chapter(s)", key="-DOWNLOAD-"), sg.Push()]
    ]
    return layout


def get_browser(values: dict) -> str:
    '''Returns a string representation of the browser to use according to user input.'''

    if values["-GC-"]:
        return "gc"
    elif values["-FF-"]:
        return "ff"


def detect_driver(window: sg.Window) -> None:
    '''Detects whether a driver executable is located in the script directory. If found, sets the driver 
    input field to the driver executable pathselects the appropriate browser option, depending on the driver.
    If both are present, then Chromedriver and Google Chrome will be selected as default.
    '''

    if "chromedriver.exe" in list(x.name for x in APP_DIR.glob("*.exe")):
        window["-DRIVER-"].update(APP_DIR / "chromedriver.exe")
        window["-GC-"].update(True)
        window["-FF-"].update(False)
    elif "geckodriver.exe" in list(x.name for x in APP_DIR.glob("*.exe")):
        window["-DRIVER-"].update(APP_DIR / "geckodriver.exe")
        window["-GC-"].update(False)
        window["-FF-"].update(True)


def set_driver(browser: str) -> (webdriver.Firefox| webdriver.Chrome):
    '''Sets the driver based on the browser selection and returns its class name without initializing it. 
    The driver will be initialized in a context manager expression with the options and service as parameters.
    '''

    if browser == "ff":
        return webdriver.Firefox
    elif browser == "gc":
        return webdriver.Chrome


def set_service(browser: str, driver_path: Path) -> (FirefoxService | ChromeService):
    '''Sets the driver service based on the browser selection and returns the related object.'''

    if browser == "ff":
        return FirefoxService(executable_path=driver_path)
    elif browser == "gc":
        return ChromeService(executable_path=driver_path)


def set_options(browser: str) -> (FirefoxOptions | ChromeOptions):
    '''Sets the driver options based on the browser selection and returns the related object.'''

    if browser == "ff":
        ff_options = FirefoxOptions()
        ff_options.add_argument("--headless")  # Comment this line out for debugging.
        return ff_options
    elif browser == "gc":
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-site-isolation-trials")
        chrome_options.add_argument("--headless")  # Comment this line out for debugging.
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Comment this line out for debugging.
        return chrome_options


def chapter_links_window(delay: float, values: dict) -> list[str]:
    '''Creates window for the "get_chapter_links" function. Returns the list of URLs.'''

    url_layout = [
            [sg.Text(""), sg.Button("na", visible=False, key="-NA-")],
            [sg.Push(), sg.Text("Getting chapter URLs, please wait..."), sg.Push()]
        ]
    fetching_urls_window = sg.Window("", url_layout, font=FONT, size=(400, 110), no_titlebar=True, grab_anywhere=True, modal=True, finalize=True)
    fetching_urls_window.set_min_size((400, 110))  # This is uesd to properly rendeer the window, if we remove this , window will be white.
    
    while True:
        fetching_urls_window["-NA-"].click()  # Clicking invisible button to initiate the script.
        event, _ = fetching_urls_window.read()
        if event == "-NA-":
            try:
                chapter_urls = get_chapter_links(delay, values)
                break
            except (NoSuchElementException, InvalidArgumentException, ElementClickInterceptedException):
                break
    fetching_urls_window.close()
    return chapter_urls


def get_chapter_links(delay: float, values: dict) -> list[str]:
    '''Gets all the available chapter URLs from the Manga title URL and returns them in a list.'''

    chapter_urls = []
    browser = get_browser(values)
    driver = set_driver(browser)
    driver_path =  Path(values["-DRIVER-"])
    options = set_options(browser)
    service = set_service(browser, driver_path)
    url = values["-TITLE_URL-"]

    with driver(options=options, service=service) as driver:
        driver.get(url)
        sleep(delay)
        
        driver.find_element("xpath", COOKIE_XPATH).click()  # Rejecting cookies, otherwise we cannot  click on the chapters for some reason.
        sleep(delay)
        
        for element in range(3,10):  # Max 6 chapters, some manga titles have an ad inbetween chapters.
            try:
                chapter_element = driver.find_element("xpath", CHAPTER_XPATH.format(element=element))
                chapter_element.click()
            except ElementNotInteractableException:  # Ads inbetween chapters.
                continue
            sleep(delay)
            
            chapter_urls.append(driver.current_url)
            
            driver.execute_script(
                '''
                window.history.go(-1);
                '''
            )
            sleep(delay)
    return chapter_urls


def get_elements(driver: webdriver) -> tuple[str, str, int]:
    '''Gets the manga title, chapter number and the declared page amount from the URL and returns them.'''

    title = driver.find_element("xpath", TITLE_XPATH).text
    chapter_no = driver.find_element("xpath", CHAPTER_NO_XPATH).text[1:]  # Remove the # from the chapter number representation.
    total_pages = int(driver.find_element("xpath", PAGES_XPATH).text[2:])  # Not real page amount, there are adds at the end. Amount of adds changes between series, so cannot just subtract a number.
    return title, chapter_no, total_pages    


def get_title_directory(manga_directory: Path, title: str) -> Path:
    '''Modifes the title if it contains illegal filesystem characters.
    Creates the title directory if it does not exist and returns its Path object.
    '''

    final_title = re.sub(ILLEGAL_CHARACTERS, "", title)

    title_directory = manga_directory / final_title
    if not title_directory.exists():
        title_directory.mkdir()

    return title_directory


def get_chapter_directory(chapter_no: str, title_directory: Path) -> Path:
    '''Creates the chapter directory if it does not exist and returns its Path object.'''

    chapter_directory = title_directory / chapter_no

    if not chapter_directory.exists():
        chapter_directory.mkdir()

    return chapter_directory


def get_real_pages_no(delay, driver: webdriver, total_pages: int) -> int:
    '''Determines and returns the real amount of pages ofthe chapter, without any ads.
    This loop is necessary, since different manga titles have different amount of ad elements after the chapter ends apparently.'''

    real_pages = 0
    for page_no in range(1, total_pages + 1):
        
        try:
            page = driver.find_element("xpath", PAGE_XPATH.format(page_no=page_no))
            real_pages += 1
            sleep(delay)
        except NoSuchElementException:  # Found an add, stop counting.
            break

        driver.execute_script(
            """
            const image = arguments[0];
            image.scrollIntoView()
            """,
            page
        )
    
    return real_pages


def get_filename_format(real_pages: int) -> str:
    '''Returns the format of the page representation, with leading zeroes depending on the total page number.'''

    if real_pages < 10:
        return "01d"
    elif real_pages < 100:
        return "02d"
    else:
        return "03d"


def save_page(chapter_directory: Path, format: str,  page_data: bytes, page_no: int) -> None:
    '''Saves an individual chapter page in the specified directory as a PNG file.'''

    file_path = chapter_directory / f"{page_no:{format}}.png"
    with open(file_path, "wb") as page:
        page.write(page_data)


def get_pages(chapter_urls: list[str], delay: float, driver: webdriver, fetching_pages_window: sg.Window, 
    manga_directory: Path, options: (FirefoxOptions | ChromeOptions), service: (FirefoxService | ChromeService)) -> None:
    '''Get and save the chapter pages in the specified directory.'''
    
    with driver(options=options, service=service) as driver:
        for url_index, url in enumerate(chapter_urls):
            driver.get(url)
            sleep(delay)

            title, chapter_no, total_pages = get_elements(driver)
            title_directory = get_title_directory(manga_directory, title)
            chapter_directory = get_chapter_directory(chapter_no, title_directory)
            real_pages = get_real_pages_no(delay, driver, total_pages)
            format = get_filename_format(real_pages)

            fetching_pages_window["-TEXT_PROGRESS_ALL-"].update(f"Chapter {chapter_no}".ljust(15))
            fetching_pages_window["-PROGRESS_ALL-"].update(current_count=url_index, max=len(chapter_urls))

            for page_no in range(1, real_pages + 1):
                page = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div[1]/div/div[{page_no}]/div/div/div/img")
                
                image_base64 = driver.execute_script(
                    """
                    const image = arguments[0];
                    image.scrollIntoView();

                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = image.width;
                    canvas.height = image.height;
                    ctx.drawImage(image, 0, 0);

                    data_url = canvas.toDataURL('image/png');
                    return data_url
                    """, 
                    page)

                page_data = a2b_base64(image_base64.split(',')[1])
                save_page(chapter_directory, format, page_data, page_no)
                sleep(delay)
                fetching_pages_window["-TEXT_PROGRESS-"].update(f"Page {page_no}/{real_pages}".ljust(15))
                fetching_pages_window["-PROGRESS-"].update(current_count=page_no, max=real_pages)
            fetching_pages_window["-PROGRESS_ALL-"].update(current_count=url_index + 1, max=len(chapter_urls))


def pages_window(chapter_urls: list[str], delay: float, driver: webdriver, manga_directory: Path, 
    options: (FirefoxOptions | ChromeOptions), service: (FirefoxService | ChromeService)):
    '''Window displaying the chapter download progress.'''

    col_1 = [
        [sg.Text(" " * 20, key = "-TEXT_PROGRESS_ALL-")],
        [sg.Text(" " * 20, key = "-TEXT_PROGRESS-")]
    ]
    col_2 = [
        [sg.ProgressBar(1, size=(1, 20), key="-PROGRESS_ALL-", visible=True, bar_color="green on white", expand_x=True)],
        [sg.ProgressBar(1, size=(1, 20), key="-PROGRESS-", visible=True, bar_color="green on white", expand_x=True)]
    ]
    url_layout = [
            [sg.Button("na", visible=False, key="-NA-")],
            [sg.Text("Download progress:")],
            [sg.Column(col_1), sg.Column(col_2, expand_x=True)]
            # [sg.Text(" " * 15, key = "-TEXT_PROGRESS_ALL-"), sg.ProgressBar(1, size=(1, 20), key="-PROGRESS_ALL-", visible=True, bar_color="green on white", expand_x=True)],
            # [sg.Text(" " * 15, key = "-TEXT_PROGRESS-"), sg.ProgressBar(1, size=(1, 20), key="-PROGRESS-", visible=True, bar_color="green on white", expand_x=True)]
        ]
    fetching_pages_window = sg.Window("", url_layout, font=FONT, size=(500, 150), no_titlebar=False, grab_anywhere=True, modal=True, finalize=True)
    fetching_pages_window.set_min_size((500, 150))  # This is uesd to properly rendeer the window, if we remove this , window will be white.
    
    while True:
        fetching_pages_window["-NA-"].click()  # Clicking invisible button to initiate the script.
        event, _ = fetching_pages_window.read()
        if event == "-NA-":
            try:
                get_pages(chapter_urls, delay, driver, fetching_pages_window, manga_directory, options, service)
                break
            except (NoSuchElementException, InvalidArgumentException, ElementClickInterceptedException) as e:
                raise e
    fetching_pages_window.close()


def main() -> None:
    '''Main function.'''

    sg.theme("DarkBlue12")
    window = sg.Window("M+D", get_main_layout(), font=FONT, enable_close_attempted_event= True, finalize=True, size=(900, 600))
    detect_driver(window)

    while True:
        event, values = window.read()
        match event:
            case sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                break
            case "-BROWSE_DL_DIR-":
                dl_dir = Path(sg.popup_get_folder("", no_window=True))
                if dl_dir:
                    window["-DL_DIR-"].update(dl_dir)
            case "-BROWSE_DRIVER-":
                driver_path = sg.popup_get_file("", file_types=(("Windows Executable File", "*.exe"),), no_window= True)
                if driver_path:
                    window["-DRIVER-"].update(driver_path)
            case "Get Links":
                title_url = values["-TITLE_URL-"]
                if not title_url:
                    multiline_error_handler(["Please provide a Manga title URL."])
                elif not title_url.startswith(ROOT_TITLE_URL):
                    multiline_error_handler(["Please provide a valid Manga title URL.", f"The manga title URL must start with: '{ROOT_TITLE_URL}'"])
                else:
                    window["-CHAPTER_URLS-"].update("")
                    try:
                        delay = float(values["-DELAY-"])
                    except ValueError as e:
                        multiline_error_handler(["Please ensure that the delay is a number between 0.1 and 10."])
                    if delay < 0.1 or delay > 10:
                        multiline_error_handler(["Please ensure that the delay is between 0.1 and 10 seconds."])
                    else:
                        chapter_urls = chapter_links_window(delay, values)
                        if chapter_urls:
                            for url in chapter_urls:
                                window["-CHAPTER_URLS-"].update(f"{url}\n", append=True)
                        else:
                            multiline_error_handler(["Failed to get chapter URLs, please try again."])
            case "-DOWNLOAD-":
                try:
                    try:
                        delay = float(values["-DELAY-"])
                    except ValueError as e:
                        raise ValueError(e)
                    chapter_urls = str(values["-CHAPTER_URLS-"]).splitlines()
                    browser = get_browser(values)
                    options = set_options(browser)
                    driver_path = Path(values["-DRIVER-"])
                    service = set_service(browser, driver_path)
                    driver_path = Path(values["-DRIVER-"])
                    manga_directory = Path(values["-DL_DIR-"])
                    driver = set_driver(browser)

                    valid_links = True
                    for url in chapter_urls:
                        if not url.startswith(ROOT_CHAPTER_URL):
                            valid_links = False
                    
                    if not chapter_urls:
                        multiline_error_handler(["Please provide at least one chapter link."])
                    elif not valid_links:
                        multiline_error_handler(["Please ensure that all chapter links are valid.", f"All chapter URLs must start with: '{ROOT_CHAPTER_URL}'"])
                    elif ((browser == "gc" and not str(driver_path).endswith("chromedriver.exe")) or
                        (browser == "ff" and not str(driver_path).endswith("geckodriver.exe"))):
                        multiline_error_handler(["Please select the appropriate driver for the selected browser."])
                    elif delay < 0.1 or delay > 10:
                        multiline_error_handler(["Please ensure that the delay is between 0.1 and 10 seconds."])
                    else:
                        try:
                            pages_window(chapter_urls, delay, driver, manga_directory, options, service)
                            operation_successful("Chapters Downloaded!")
                        except(NoSuchElementException, InvalidArgumentException, ElementClickInterceptedException):
                            multiline_error_handler(["Download failed. Please check the URLs or adjust the delay."])
                except ValueError:
                    multiline_error_handler(["Please ensure that the delay is a number between 0.1 and 10."])
    window.close()

if __name__ == "__main__":
    main()
