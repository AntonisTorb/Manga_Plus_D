# Manga + D
A script that downloads manga chapters from MangaPlus using Selenium.
Simply provide the browser to use and the chapter URL and let the script run until you get the confirmation that the download is finished. This might take a while, due to the way that images are loaded in MangaPlus, so the app has to wait for a short amount of time for the images to load.

For a simplified version without a GUI, please check the [noGUI branch](https://github.com/AntonisTorb/Manga_Plus_D/tree/noGUI).

## WARNING!
This application uses PySimpleGUI for the GUI frontend. PySimpleGUI has recently become closed source in a disappointing decision, thus I would advise you to use the PySimpleGUI version specified in the `requirements.txt` file. For any future versions, I can guarantee neither the integrity nor the security of the package.

## Disclaimer
I am not giving permission to any one person or legal entity to use this code for any purpose other than to read some manga chapters. If you want to use part of the code for your own project please contact me with a description of what you want to do.

Do not distribute the results of running this script without approval from the owners of their distribution rights.

If anyone from Shueisha or the MangaPlus team wants me to take this down, please contact me and I will make this private. This is only intended as a showcase of a personal scraping project.

## How to use (Windows):

**IMPORTANT!**
This script supports Google Chrome and Mozilla Firefox only.

- Depending on your preferred browser and it's version, you will need to download the correct driver:
  - **For Google Chrome:** Visit the [ChromeDriver download page](https://chromedriver.chromium.org/downloads) and download the appropriate version depending on your Goggle Chrome browser version and your OS.
  - **For Mozilla Firefox:** Visit the [geckodriver release page](https://github.com/mozilla/geckodriver/releases) and download the appropriate version depending on your Mozilla Firefox browser version and your OS.
- Unpack the downloaded zip file and transfer the driver executable file ("chromedriver.exe" or "geckodriver.exe") to the same directory as the "main.py" script.
- Open your command terminal and install the requirements by running the following command:
  - pip install -r requirements.txt
- Set the current working directory to the folder contating the "main.py" script by running the command:
  - cd 'directory path goes here'
- Run the script with the following command:
  - python main.py

## In case of failure
There is a chance the script will show a confirmation message, while nothing was downloaded, possibly due to  the timing of the delay. In that case, you can increase the delay on line 18 and try again.

Additionally, if the app crashes, it does not necessarily mean that it will always fail, so please try again with a longer delay on line 18.

## Future
~~I will explore if it's possible to use other browsers. Also, planning to create a simple GUI that accepts multiple URLs/manga title URL, and downloads the chapters in succession~~. Finally, create an executable file.

## Credits
Big part of the code by [H.Lima in StackOverflow](https://stackoverflow.com/questions/64172105/acess-data-image-url-when-the-data-url-is-only-obtain-upon-rendering).
