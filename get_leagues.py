import requests
from bs4 import BeautifulSoup

def get_leagues(bookmaker, sport_id):
    if (bookmaker == "1xstavka"):
        params = {
            'sports': sport_id,
            'count': '50',
            'tf': '2200000',
            'tz': '7',
            'antisports': '188',
            'mode': '4',
            'country': '1',
            'partner': '51',
            'getEmpty': 'true',
        }
        response = requests.get('https://1xstavka.ru/LineFeed/Get1x2_VZip', params=params)
        result = response.json()
        return result
    if (bookmaker == "marathonbet"):
        params = {
            'pageAction': 'default',
            '_': '1683634845180',
        }
        response = requests.get('https://www.marathonbet.ru/su/betting/' + str(sport_id), params=params)
        result = BeautifulSoup(response.text, 'html.parser')
        return result
    else:
        print("Error")