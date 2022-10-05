import re


FONT = ("Arial", 14)
ROOT_TITLE_URL = "https://mangaplus.shueisha.co.jp/titles/"
ROOT_CHAPTER_URL = "https://mangaplus.shueisha.co.jp/viewer/"
TITLE_XPATH = "/html/body/div[1]/div[2]/div/div[3]/div[1]/div[2]/a/h1"
CHAPTER_NO_XPATH = "/html/body/div[1]/div[2]/div/div[3]/div[1]/div[2]/div/p"
PAGES_XPATH = "/html/body/div[1]/div[2]/div/div[2]/div[2]/p/span"
PAGE_XPATH = "/html/body/div[1]/div[2]/div/div[1]/div/div[{page_no}]/div/div/div/img"
CHAPTER_XPATH = "/html/body/div[1]/div[2]/div/div[2]/div/div/div[2]/main/div/div[{element}]"
COOKIE_XPATH = '//*[@id="onetrust-reject-all-handler"]'
ILLEGAL_CHARACTERS = re.compile(r"([\\/:*?\"<>|])")
SLEEP_SECONDS = 0.8  # Need to sleep so the pages have time to load.