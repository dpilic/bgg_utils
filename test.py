import pandas as pd
import datetime
from bgg_xmlapi2 import *

dtime = datetime.datetime.today().strftime('%Y%m%d')

file_path = r'/data/bgg_ids_' + dtime + '.csv'

df = pd.read_csv(file_path, names=['objectid', 'name'], sep=';')


# df = df.loc[0:999, :]

# print(df.head())

print('START')

df_meta = get_bgg_meta(df)

print('END')
print(df_meta.head())

df_meta.to_csv(r'/data/bgg_data_' + dtime + '.csv', sep=';')
