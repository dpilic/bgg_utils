from boardgamegeek import *
import csv
import datetime

bg_hot_list = BGGClient()

for key in bg_hot_list.hot_items("boardgame")._data['items']:
    print()


dtime = datetime.datetime.today().strftime('%Y%m%d')

file_path = r'data/BGG HOT50/bgg_top50_' + dtime + '.csv'

hot_50_games = bg_hot_list.hot_items("boardgame")._data['items']

fieldnames = list(hot_50_games[0].keys())

print(fieldnames)

with open(file_path, 'w', encoding='utf-8') as csvfile:

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for itm in hot_50_games:
        writer.writerow(itm)
