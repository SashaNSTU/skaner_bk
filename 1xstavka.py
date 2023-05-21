import requests
from datetime import datetime
import datetime
import locale

def GameName(result):
    for game in range(0, len(result)):
        params = {
            'id': result[game],
            'lng': 'ru',
            'cfview': '0',
            'isSubGames': 'true',
            'GroupEvents': 'true',
            'allEventsGroupSubGames': 'true',
            'countevents': '250',
            'partner': '51',
            'grMode': '2',
            'marketType': '1',
            'isNewBuilder': 'true',
        }

        response = requests.get('https://1xstavka.ru/LineFeed/GetGameZip', params=params)
        res = response.json()
        #можно экономить память
        try:
            print(res["Value"]["O1"] + " - " + res["Value"]["O2"])
        except:
            print()


    print()

def GameId(result):
    id_games =[]
    params = {
        'champs': result,
        'count': '50',
        'tf': '2200000',
        'tz': '7',
        'antisports': '188',
        'mode': '4',
        'country': '53',
        'partner': '51',
        'getEmpty': 'true',
    }
    response = requests.get('https://1xstavka.ru/LineFeed/Get1x2_VZip', params=params)
    result = response.json()
    for game in range(0, len(result["Value"])):
        # можно экономить память
        id_games.append(result["Value"][game]["CI"])
    GameName(id_games)

    if (len(id_games)>0):
        print(id_games)

def ChampsId(result):
    id_liges = []
    # id_liges = {}
    for champs in range(0, len(result["Value"])):
        #можно экономить память
        id_liges.append(result["Value"][champs]["LI"])
        GameId(id_liges[champs])
        # словарь
        # id_liges[result["Value"][champs]["LI"]] = result["Value"][champs]["L"]

    #print(len(id_liges))


def main():
    params = {
        'sport': '3',
        'tf': '2200000',
        'tz': '7',
        'country': '53',
        'partner': '51',
        'virtualSports': 'true',
        'gr': '44',
        'groupChamps': 'true',
    }
    response = requests.get('https://1xstavka.ru/LineFeed/GetChampsZip', params=params)
    result = response.json()
    ChampsId(result)

if __name__ == '__main__':
    params = {
        'siteStyle': 'MULTIMARKETS',
        'oddsType': 'Decimal',
        'timeZone': 'Europe/Moscow',
        'pageAction': 'default',
    }

    response = requests.get(
        'https://www.marathonbet.ru/su/betting/Basketball/NBA/Play-Offs/Semi+Final/Miami+Heat+%40+Boston+Celtics+-+15983713',
        params=params,
    )
    result = response.text
    print(result)
