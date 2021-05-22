from time import sleep
import os
import requests
from bs4 import BeautifulSoup
import html.parser

class Anime:

    def __init__(self):
        pass

    def _get_title(self, title: str) ->str:

        # Dictionary with the words to replace and their replacement
        words_to_replace = [
            {
             'old': ["Episode"],
             'new': "ep"
             },
            {
             'old': ["Subbed", "(Sub)", "Sub"],
             'new': "sub"
             },
            {
             'old': ["Dubbed", "Dub", "(Dub)"],
             'new': "dub"
             },
                            ]
        # Replacing the words 
        for i in words_to_replace:
            for word in i['old']:
                if word in title:
                    title = title.replace(word, i['new'])

        # Spliting it in to a list in order to join it with underscores
        title_parts = title.split()
        title = "_".join(title_parts) + ".mp4"

        return title

    def install_from(self, num: int, base_url: str, resolution: str="HDP") -> dict:
        # Initializing the dictionary
        dicti = {
            'id': num,
            'title': "",
            'size': "",
            'duration': "",
            'default_resolution': "",
            'url': ""
                 }

        # Making the url
        url = f"{base_url}{str(num)}"
        # Getting the html from the page
        page = requests.get(url)

        # Making the soup
        soup = BeautifulSoup(page.content, "html.parser")

        # Finding the link for the downloads page
        tag = soup.find("li", {'class': "dowloads"})
        downloadPageUrl = tag.find("a").attrs['href']

        # Making a new soup
        page = requests.get(downloadPageUrl)
        soup = BeautifulSoup(page.content, "html.parser")

        # Getting information about the episode
        information = soup.find("div", {'class': "sumer_l"})
        li_tag = information.find_all("li")

        # Passing the information to the dictionary
        dicti['title'] = self._get_title(li_tag[0].text.replace("File name:", ""))
        dicti['size'] = li_tag[1].text
        dicti['duration'] = li_tag[2].text
        dicti['default_resolution'] = li_tag[3].text

        # Finding the download link
        tag = soup.find("div", {'class': "mirror_link"})
        div_tags = tag.find_all("div")

        # Passing the link to the dictionary based on the input resolution
        dicti['url'] = [i.find("a").attrs['href'] for i in div_tags if resolution in i.text][0]

        # returning the dictionary
        return dicti
    
    def download(self, title: str, url: str):

        try:
            # Getting the current directory
            CURR_DIR = os.getcwd()
            # Making the directory name by removing the .mp4 and the episode number
            title_parts = title.split("_")
            dir_title = "_".join(title_parts[0: -2])
            folder = os.path.join(CURR_DIR, dir_title)
            # Create the directory if it does not exist
            if not os.path.exists(folder):
                os.mkdir(folder)
            else:
                pass

            print(f"Downloading {title}...")
            video = requests.get(url, stream=True)
            file_size = video.headers.get('Content-Length', None)
            file_size = int(file_size) // 1048576
            with open(os.path.join(folder, title), "wb") as fh:
                for i, chunk in enumerate(video.iter_content(chunk_size=1024*1024)):
                    if chunk:
                        percentage = f"\033[1;32m{str((i * 100) // file_size)}\033[0m%"
                        print(percentage, end='\r')
                        fh.write(chunk) 
            print(f" * {title} installed")
            
        except:
            pass

    def search(self, search: str) -> list:
        results = []

        url = f"https://www1.gogoanime.ai//search.html?keyword={search}"
        base_url = "https://www1.gogoanime.ai"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        ul_tag = soup.find("ul", {'class': "items"})
        items = ul_tag.find_all("li")
        for i, item in enumerate(items):
            p_tag = item.find("p", {'class': "name"})
            a_tag = p_tag.find("a")

            id = i
            title = a_tag.text
            link = base_url + str(a_tag.attrs['href']).replace("category/", "") + "-episode-"
            date_released = item.find("p", {'class': "released"}).text.replace("Released:", "").split()[0]

            dicti = {
                'id': id,
                'title': title,
                'url': link,
                'date_released': date_released,
                    }

            results.append(dicti)

        return results

if __name__=='__main__':
    urls = []
    # base_url = "https://www1.gogoanime.ai/castlevania-season-4-dub-episode-"
    base_url = "https://www1.gogoanime.ai/tensei-shitara-slime-datta-ken-2nd-season-episode-"
    number_of_episodes = 12 ## Put the number of episodes you want installed
    begin_from = 1 ## If you want it to start downloading from a scpecific episode
    # for i in range(number_of_episodes):
    #     num = begin_from + i
    #     test = Anime()
    #     x = test.install_from(num, base_url)
    #     # test.download(x['title'], x['url'])
    #     print(x['url'])

    # test = Anime()
    # print(test._get_title("Castlevania Season 4 (Dub) Episode 1"))

    test = Anime()
    print(test.search("juju"))
