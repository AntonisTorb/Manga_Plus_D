# Manga + D
A script that downloads manga chapters from MangaPlus using Selenium.
Simply provide the chapter URL and let the script run until you get the confirmation that the download is finished. This might take a while, due to the way that images are loaded in MangaPlus, so the app has to wait for a short amount of time for the images to load.

## Disclaimer
I am not giving permission to any one person or legal entity to use this code for any purpose other than to read some manga chapters. If you want to use part of the code for your own prject please contact me with a description of what you want to do.

Do not distribute the results of this script without approval from the owners of their distribution rights.

If anyone from Shueisha or the MangaPlus team wants me to take this down, please contact me and I will make this private. This is only intended as a showcase of a personal scraping project.

## How to use (Windows):

**IMPORTANT!**
This script only works using Google Chrome at the moment, so you will need to have it installed.

- Visit the [ChromeDriver download page](https://chromedriver.chromium.org/downloads) and download the appropriate version depending on your Goggle Chrome browser version.
- Unpack the downloaded zip file and transfer the "chromedriver.exe" file in the same folder as the "main.py" script.
- Open your command terminal and install the requirements by running the following command:
  - pip install -r requirements.txt
- Set the current working directory to the folder contating the "main.py" script by running the command:
  - cd 'directory path goes here'
- Run the script with the following command:
  - python main.py

There is a chance the script will show a confirmation message, while nothing was downloaded, possibly due to  the timing of the delay. In that case, you can increase the delay on line 15 and try again.

## In case of failure
Please note that if this crashes for some reason I have missed, please make sure to check your task manager for any remaining Google Chrome or chromedriver.exe processes that did not close properly. I am using a context manager, so this should not happen, but just in case.

## Future
I will explore if it's possible to use other browsers. Also, planning to create a simple GUI that accepts multiple URLs and downloads the chapters in succession and also make an executable file.