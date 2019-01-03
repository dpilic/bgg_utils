
# imports and some settings
from bs4 import BeautifulSoup
import requests
import re
import csv
import time
import datetime

GAMES_PER_PAGE = 100
BROWSE_URL_BASE = 'http://www.boardgamegeek.com/browse/boardgame/page/'

dtime = datetime.datetime.today().strftime('%Y%m%d')

file_path = r'data/Documents/bgg_ids_' + dtime + '.csv'


def get_game_ids(file_path):
    """Download game-ids & names from BGG.
    """

    file = open(file_path, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter=';')

    INIT_URL = 'https://boardgamegeek.com'
    CURRENT_URL = 'https://boardgamegeek.com/browse/boardgame/page/1'
    STOP = False
    counter = 1

    while not STOP:

        if counter % 100 == 0:
            time.sleep(120)

        # print(CURRENT_URL)

        for _i in range(3):
            try:
                page = requests.get(CURRENT_URL, timeout=30)
                soup = BeautifulSoup(page.content, "html.parser")
                break
            except:
                pass

        for tt in range(3):
            try:
                print("Reading page {0}".format(CURRENT_URL))

                # items are found by 'id=results_objectname*' attribute in 'div' tag
                cntr = 1
                for _ in range(GAMES_PER_PAGE):
                    item = soup.find('div', {'id': 'results_objectname' + str(cntr)})
                    if item:
                        href = item.a.attrs['href']
                        try:
                            game_id = re.search(r'/boardgame/(.*)/', href).groups()[0]
                            # game_ids.append(game_id)
                        except:
                            game_id = re.search(r'/boardgameexpansion/(.*)/', href).groups()[0]
                        name_id = item.a.text
                        csv_writer.writerow([game_id, name_id])
                        cntr += 1
                break
            except:
                time.sleep(10)
                if tt == 2:
                    raise ConnectionError()

        if not (soup.find('a', title="next page") is None):
            CURRENT_URL = INIT_URL + soup.find_all('a', title="next page")[0].attrs.get('href')
            counter += 1
        else:
            print('Stopping..')
            STOP = True

    file.close()
    # return game_ids


get_game_ids(file_path)
