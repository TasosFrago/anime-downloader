from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import html.parser

def wait(driver, path, click=False):
    if click == False:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, path)))
    else:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, path)))

class Anime:

    def __init__(self, base_url):
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.set_headless
        self.driver = webdriver.Firefox(options=fireFoxOptions)
        self.driver.implicitly_wait(10)
        self.base_url = base_url

    def _connect(self, gurl):
        try:
            self.driver.get(gurl)
        except:
            print("Timeout error: Failed to connect to the website")

    def install_from(self, num):
        # range_list is a list containing two values so it knows at which episode to start and which to end

        dicti = {'id': "", 'title': "", 'url': ""}

        # connect to that url
        url = f"{self.base_url}{str(num)}"
        self._connect(url)

        # Finding the title
        xpath = "//div[@class='anime_video_body']/h1"
        wait(self.driver, xpath)
        elem = self.driver.find_element_by_xpath(xpath)

        # Make the title
        title_parts = elem.text.split()
        title_parts = title_parts[0: -4]
        title = ""
        for i in title_parts:
            title = f"{title}_{i}"
        title = "{}.mp4".format(title[1:])

        # Finding the url
        # Switch to iframe
        frame = "//div[@class='play-video']/iframe"
        wait(self.driver, frame)
        iframe = self.driver.find_element_by_xpath(frame)
        self.driver.switch_to.frame(iframe)

        # Click the play button
        xpath = "//div[@class='jw-icon jw-icon-display jw-button-color jw-reset'][@role='button']"
        wait(self.driver, xpath, click=True)
        elem = self.driver.find_element_by_xpath(xpath)
        self.driver.execute_script("arguments[0].click();", elem)

        # Switch back to first tab after redirect
        self.driver.switch_to.window(self.driver.window_handles[0])

        iframe = self.driver.find_element_by_xpath(frame)
        self.driver.switch_to.frame(iframe)

        xpath = "//div[@class='jw-display-icon-container jw-display-icon-display jw-reset']"
        wait(self.driver, xpath, click=True)
        elem = self.driver.find_element_by_xpath(xpath)
        self.driver.execute_script("arguments[0].scrollIntoView();", elem)
        sleep(1)
        elem.click()

        # Find the url
        xpath = "//video[@class='jw-video jw-reset']"
        wait(self.driver, xpath)
        elem = self.driver.find_element_by_xpath(xpath)
        src = elem.get_attribute('src')

        self.driver.quit()
        dicti = {'id': num, 'title': title, 'url': src}
        return dicti

    def download(self, title, url):
        video = requests.get(url, stream=True)
        with open(title, "wb") as fh:
            for chunk in video.iter_content(chunk_size=1024*1024):
                if chunk:
                    fh.write(chunk)

if __name__=='__main__':
    urls = []
    base_url = "https://www1.gogoanime.ai/one-piece-episode-"
    number_of_episodes = 1 ## Put the number of episodes you want installed
    begin_from = 0 ## If you want it to start downloading from a scpecific episode
    for i in range(number_of_episodes):
        num = begin_from + i
        test = Anime(base_url)
        x = test.install_from(num)
        urls.append(x)

        test.download(x['title'], x['url'])
