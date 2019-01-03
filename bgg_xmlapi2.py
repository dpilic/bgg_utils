import pandas as pd
import numpy
import requests
from xml.etree import ElementTree
import time
import datetime


def xml_attrib(elem,
               attr=None,
               subattr=None,
               subval=None,
               attrib_val='value'):

    if subattr is None:
        return elem.find(f'.//{attr}').attrib[attrib_val]
    elif subval is None:
        return elem.find(f'.//{attr}[@{subattr}]').attrib[attrib_val]
    else:
        return elem.find(f'.//{attr}[@{subattr}="{subval}"]').attrib[attrib_val]


def xml_attrib_list(elem,
                    attr=None,
                    subattr=None,
                    subval=None,
                    attrib_val='value'):

    ch_list = []
    if subattr is None:
        for chrs in elem.findall(f'.//{attr}'):
            ch_list.append(chrs.attrib[attrib_val])
    elif subval is None:
        for chrs in elem.findall(f'.//{attr}[@{subattr}]'):
            ch_list.append(chrs.attrib[attrib_val])
    else:
        for chrs in elem.findall(f'.//{attr}[@{subattr}="{subval}"]'):
            ch_list.append(chrs.attrib[attrib_val])
    return ch_list


URL = "http://www.boardgamegeek.com/xmlapi2/thing?id={}&stats=1&videos=1&page=1000&pagesize=100"


def get_bgg_meta(df,
                 id='objectid',
                 stepsize=100,
                 url="http://www.boardgamegeek.com/xmlapi2/thing?id={}&stats=1&videos=1&page=1000&pagesize=100"):

    queue = df[id].tolist()

    dfc = df.copy()

    _count = 0

    _data = {}

    for _i in range(0, len(queue), stepsize):

        print('Next Chunk:', datetime.datetime.now().time())
        for _ in range(3):
            try:
                req = requests.get(url.format(','.join([str(x) for x in queue[_i:_i + stepsize]])))

                root = ElementTree.fromstring(req.content)

                print('xml worked:', datetime.datetime.now().time())
                for _g in root:
                    # ID:
                    currentid = int(_g.attrib['id'])
                    _data[currentid] = {}
                    dummy = _data[currentid]

                    # Type:
                    dummy['type'] = (_g.attrib['type'])
                    # Name:
                    dummy['name'] = (xml_attrib(_g, 'name', 'type', 'primary'))
                    # Year:
                    dummy['year'] = (xml_attrib(_g, 'yearpublished'))
                    # MinPlayers:
                    minplayers = xml_attrib(_g, 'minplayers')
                    dummy['minplayers'] = (minplayers)
                    # MaxPlayers:
                    maxplayers = xml_attrib(_g, 'maxplayers')
                    dummy['maxplayers'] = (maxplayers)
                    # playingtime:
                    dummy['playingtime'] = (xml_attrib(_g, 'playingtime'))
                    # minplaytime:
                    dummy['minplaytime'] = (xml_attrib(_g, 'minplaytime'))
                    # maxplaytime:
                    dummy['maxplaytime'] = (xml_attrib(_g, 'maxplaytime'))
                    # numvideos:
                    dummy['num_videos'] = (xml_attrib(_g, 'videos', None, None, 'total'))
                    # avg_rating:
                    dummy['avg_rating'] = (xml_attrib(_g, 'statistics/ratings/average'))
                    # bayes_avg_rating:
                    dummy['bayes_avg_rating'] = (xml_attrib(_g, 'statistics/ratings/bayesaverage'))
                    # usersrated:
                    dummy['usersrated'] = (xml_attrib(_g, 'statistics/ratings/usersrated'))
                    # bgg_rank exclude 'Not Ranked':
                    dummy['bgg_rank'] = (xml_attrib(_g, 'statistics/ratings/ranks/rank', 'type', 'subtype'))
                    # owned:
                    dummy['num_owned'] = (xml_attrib(_g, 'statistics/ratings/owned'))
                    # wanting:
                    dummy['num_wanting'] = (xml_attrib(_g, 'statistics/ratings/wanting'))
                    # wishing:
                    dummy['num_wishing'] = (xml_attrib(_g, 'statistics/ratings/wishing'))
                    # trading;
                    dummy['num_trading'] = (xml_attrib(_g, 'statistics/ratings/trading'))
                    # numcomments:
                    dummy['num_comments'] = (xml_attrib(_g, 'statistics/ratings/numcomments'))
                    # numweights:
                    dummy['num_weights'] = (xml_attrib(_g, 'statistics/ratings/numweights'))
                    # averageweight
                    dummy['averageweight'] = (xml_attrib(_g, 'statistics/ratings/averageweight'))

                    # mechanics:
                    dummy['mechanics'] = ','.join(xml_attrib_list(_g, 'link', 'type', 'boardgamemechanic'))
                    # boardgamecategory:
                    dummy['category'] = ','.join(xml_attrib_list(_g, 'link', 'type', 'boardgamecategory'))
                    # boardgamefamily:
                    dummy['family'] = ','.join(xml_attrib_list(_g, 'link', 'type', 'boardgamefamily'))
                    # boardgamedesigner:
                    dummy['designer'] = ','.join(xml_attrib_list(_g, 'link', 'type', 'boardgamedesigner'))
                    # boardgameartist:
                    dummy['artists'] = ','.join(xml_attrib_list(_g, 'link', 'type', 'boardgameartist'))
                    # boardgameexpansion
                    dummy['expansions'] = ','.join(xml_attrib_list(_g, 'link', 'type', 'boardgameexpansion', 'id'))
                    # playerpoll
                    num_branch = _g.find('.//poll[@name="suggested_numplayers"]')
                    numplayer_dict = {}
                    for lv1 in num_branch.findall('.//results[@numplayers]'):
                        numplayer_dict[lv1.attrib['numplayers']] = []
                        numplayer_vec = numplayer_dict[lv1.attrib['numplayers']]
                        for lv2 in lv1.findall('.//result'):
                            numplayer_vec.append(lv2.attrib['numvotes'])
                    try:
                        dummy['two_player_rating'] = ','.join(numplayer_dict['2'])
                    except Exception as e:
                        dummy['two_player_rating'] = np.nan
                    try:
                        dummy['two_player_quota'] = sum([int(x) for x in numplayer_dict['2'][0:2]]) / sum([int(x) for x in numplayer_dict['2']])
                    except Exception as e:
                        dummy['two_player_quota'] = np.nan

                break
            except Exception as e:
                print('Fetching-Error:', _ + 1, '. try.')
                time.sleep(2)
                if _ == 2:
                    raise ConnectionError
        _count += stepsize
        print('PROGRESS:', min(_count, len(df)), r'/', len(df))

    return pd.DataFrame(_data).T.reset_index().rename(columns={'index': id})
