import json
import os
import requests
import urllib3
import urllib.parse
import re
import collections
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global Vars
app_config = None
anime_list = []  # Stores the full info name
anime_url_list = []  # Stores the URLs
anime_search_list = []  # Stores the simplified name


# Functions
def pause_IO():
    input("Press Enter to continue.")


def clear():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def is_tool(name):
    from shutil import which

    return which(name) is not None


def show_menu():
    clear()
    print("---------------Anime-Watch-CLI---------------")
    print("1. Show All Animes")
    print("2. Anime Search")
    print("0. Exit")
    print("-----------------------------------------------")
    opc = input("Option: ")
    return opc


def search_anime(query):
    results = []

    i = 0
    for item in anime_search_list:
        if SequenceMatcher(None, item.lower(), query.lower()).ratio() >= 0.6:
            results.append(i)
        i += 1

    # Show search results
    i = 1
    for item in results:
        print(f"{str(i)}. {anime_list[item]}")
        i += 1
    print("Type \"back\" to go back or \"exit\" to leave.")

    while True:
        opc = input("Option: ")

        # Check if input is valid
        if opc.lower() == 'exit':
            clear()
            print("\nBye Bye!")
            exit()
        elif opc.lower() == 'back':
            return None
        elif opc.isdigit():
            if 0 < int(opc) <= len(results):
                return results[int(opc)-1]


def get_all_anime():
    clear()
    print("Loading...")

    # Request page
    r = requests.get(app_config['url'] + 'all-releases/')

    # Start bs4
    soup = BeautifulSoup(r.content, 'lxml')
    post_content = soup.find("div", class_='post-content')
    wrapper_p = post_content.find_all("p")  # The 3rd is the one we want
    anime_items = wrapper_p[2].find_all("a")

    # Add items to list
    for item in anime_items:
        anime_list.append(item.get_text())
        anime_url_list.append(item['href'])
        anime = item['href'].rsplit('/', 1)[-2]
        formatted_anime = anime.split('-', 1)[1]
        anime_search_list.append(formatted_anime.replace('-', ' ').title())


def select_all_anime():
    i = 1
    for item in anime_list:
        print(f"{str(i)}. {item}")
        i += 1
    print("Type \"back\" to go back or \"exit\" to leave.")

    while True:
        opc = input("Option: ")

        # Check if input is valid
        if opc.lower() == 'exit':
            clear()
            print("\nBye Bye!")
            exit()
        elif opc.lower() == 'back':
            return None
        elif opc.isdigit():
            if 0 < int(opc) <= len(anime_list):
                return opc


def select_episodes(i):
    clear()
    print("Fetching Episodes...")

    episodes = {}
    ep_urls = []

    # Request page
    r = requests.get(anime_url_list[i])

    # Start bs4
    soup = BeautifulSoup(r.content, 'lxml')
    post_content = soup.find("div", class_='post-content')
    a_tags = post_content.find_all("a")

    # Get episodes
    for item in a_tags:
        try:
            if item['href'] != 'https://app.animewat.ch/' and item['href'][:27] == 'https://store.animewat.ch//':
                episodes[re.sub("[\(\[].*?[\)\]]", "", item['href'].rsplit('/', 1)[-1]
                                       .replace('[1080pp]', '1080pp').replace('[720pp]', '720pp')
                                       .replace('[480pp]', '480p')).replace(' .', '.').replace('1080pp1080pp', '1080pp')
                                .replace('1080pp 1080pp', '1080pp').replace('720pp 720pp', '720pp')
                                .replace('720pp720pp', '720pp').strip()] = item['href']

        except KeyError:
            pass

    # Sort episodes
    sort_eps = collections.OrderedDict(sorted(episodes.items()))

    # Show available episodes
    clear()
    j = 1
    for k, v in sort_eps.items():
        print(f"{str(j)}. {k}")
        ep_urls.append(v)
        j += 1

    print("Type \"back\" to go back or \"exit\" to leave.")

    while True:
        opc = input("Option: ")

        # Check if input is valid
        if opc.lower() == 'exit':
            clear()
            print("\nBye Bye!")
            exit()
        elif opc.lower() == 'back':
            return None
        elif opc.isdigit():
            if 0 < int(opc) <= len(anime_list):
                break

    play_episode(ep_urls[int(opc) - 1])
    return 'OK'


def play_episode(url):
    clear()
    print("Launching player...")

    if os.name in ('nt', 'dos'):  # If running Windows
        os.system(app_config["mpv_path_win"] + ' ' + urllib.parse.quote(url).replace('https%3A', 'https:'))
    else:
        if is_tool('mpv'):
            os.system('mpv \'' + url + '\'')
        else:
            print("Please make sure mpv is installed in your system!")

    pause_IO()


def main():
    while True:
        opc = show_menu()
        if opc == "1":  # Show all anime
            clear()
            while True:
                index = select_all_anime()
                if index is not None:
                    while True:
                        res = select_episodes(int(index)-1)
                        if res is None:
                            break
                else:
                    break

        elif opc == "2":  # Anime Search
            clear()

            # Make search query
            search = input("Insert anime title: ")
            while True:
                index = search_anime(search)
                if index is not None:
                    while True:
                        res = select_episodes(index)
                        if res is None:
                            break
                else:
                    break

        elif opc == "0" or opc.lower() == 'exit':  # Exit
            clear()
            print("\nBye Bye!")
            exit()
        else:
            print("Invalid Input")


if __name__ == '__main__':
    # Check for config
    if not os.path.exists("config/conf.json"):
        # Create blank file and exit
        if not os.path.exists('config'):
            os.makedirs('config')
        with open("config/conf.json", "w") as config_file:
            blank_config = {
                "url": "https://animewat.ch/",
                "mpv_path_win": "win-mpv\\mpvnet.exe"
            }
            obj = json.dumps(blank_config, indent=4)

            config_file.write(obj)
            config_file.close()

        print("Config file not found, a blank one has been created.\nPlease make sure the " +
              "settings are correct first.")
        exit()

    with open("config/conf.json", "r") as cfg:
        app_config = json.load(cfg)
        cfg.close()

    # Correct URL if needed
    if app_config['url'][-1] != '/':
        app_config['url'] += '/'

    # Scrap all anime
    get_all_anime()

    main()
