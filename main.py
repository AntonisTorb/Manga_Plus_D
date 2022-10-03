from binascii import a2b_base64
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from pathlib import Path
import re
import sys


TITLE_XPATH = "/html/body/div[1]/div[2]/div/div[3]/div[1]/div[2]/a/h1"
CHAPTER_XPATH = "/html/body/div[1]/div[2]/div/div[3]/div[1]/div[2]/div/p"
PAGES_XPATH = "/html/body/div[1]/div[2]/div/div[2]/div[2]/p/span"
ILLEGAL_CHARACTERS = re.compile(r"([\\/:*?\"<>|])")
SLEEP_SECONDS = 0.5  # Need to sleep so the pages have time to load.


def get_URL() -> str:
    '''Requests the URL from the user, exits if "X" provided.'''

    url = input("Please provide the chapter URL, or exit with 'X': ")
    if url == "X":
        print("Exiting...")
        sys.exit(0)
    else:
        return url


def get_manga_directory() -> Path:
    '''Creates the Manga directory if it does not exist and returns its path object.'''

    app_directory = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    manga_directory = app_directory / "Manga"
    if not manga_directory.exists():
        manga_directory.mkdir()
    return manga_directory


def set_options() -> Options:
    '''Sets the driver options and returns the related object.'''

    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-site-isolation-trials")
    chrome_options.add_argument("--headless")  # Comment this line out for debugging.
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Comment this line out for debugging.
    return chrome_options


def initiate_driver(driver: webdriver, url: str) -> None:
    '''Loads the provided URL into the webdriver.'''

    print("Loading URL...")
    driver.get(url)


def get_elements(driver: webdriver) -> tuple[str, str, int]:
    '''Gets the manga title, chapter number and the declared page amount from the URL and returns them.'''

    title = driver.find_element("xpath", TITLE_XPATH).text
    chapter_no = driver.find_element("xpath", CHAPTER_XPATH).text[1:]  # Remove the # from the chapter number representation.
    total_pages = int(driver.find_element("xpath", PAGES_XPATH).text[2:])  # Not real page amount, there are adds at the end. Amount of adds changes between series, so cannot just subtract a number.
    return title, chapter_no, total_pages


def get_title_and_directory(manga_directory: Path, title: str) -> tuple[str, Path]:
    '''Modifes the title if it contains illegal filesystem characters.
    Creates the title directory and returns the new title and the title directory's Path object.
    '''

    final_title = re.sub(ILLEGAL_CHARACTERS, "", title)

    title_directory = manga_directory / final_title
    if not title_directory.exists():
        title_directory.mkdir()

    return final_title, title_directory


def get_chapter_directory(chapter_no: str, title_directory: Path):
    '''Creates the chapter directory if it does not exist and returns its Path object.'''

    chapter_directory = title_directory / chapter_no

    if not chapter_directory.exists():
        chapter_directory.mkdir()

    return chapter_directory


def get_real_pages_no(driver: webdriver, total_pages: int) -> int:
    '''Determines and returns the real amount of pages ofthe chapter, without any ads.
    This loop is necessary, since different manga titles have different amount of ads after the chapter ends apparently.'''

    real_pages = 0
    for page_no in range(1, total_pages + 1):
        
        try:
            page = driver.find_element("xpath", f"/html/body/div[1]/div[2]/div/div[1]/div/div[{page_no}]/div/div/div/img")
            real_pages += 1
            sleep(SLEEP_SECONDS)
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


def get_filename_format(real_pages: int):
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


def get_pages(chapter_directory: Path, chapter_no: str, driver: webdriver, final_title: str, format: str, real_pages: int) -> None:
    '''Get and save the chapter pages in the specified directory.'''

    print(f"Getting {final_title} chapter {chapter_no}...")
    for page_no in range(1, real_pages + 1):
        print(f"Getting page {page_no:{format}}/{real_pages}")
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
        sleep(SLEEP_SECONDS)


def main() -> None:
    '''Main function.'''

    url = get_URL()
    manga_directory = get_manga_directory()
    chrome_options = set_options()

    with webdriver.Chrome(options=chrome_options) as driver:
        try:
            initiate_driver(driver, url)
        except InvalidArgumentException:
            print("Invalid URL!")
            url = get_URL()
            initiate_driver(driver, url)
        sleep(SLEEP_SECONDS * 2)
        try:
            title, chapter_no, total_pages = get_elements(driver)
        except NoSuchElementException:
            print("Elements not found, possibly wrong url provided. Closing app...")
            sys.exit(0)

        final_title, title_directory = get_title_and_directory(manga_directory, title)
        chapter_directory = get_chapter_directory(chapter_no, title_directory)
        real_pages = get_real_pages_no(driver, total_pages)
        format = get_filename_format(real_pages)

        get_pages(chapter_directory, chapter_no, driver, final_title, format, real_pages)
        print("-" * 50)
        print(f"Finished downloading {title} chapter {chapter_no}!")
        print("-" * 50)

if __name__ == "__main__":
    main()
