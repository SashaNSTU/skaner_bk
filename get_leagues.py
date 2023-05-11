import requests
from bs4 import BeautifulSoup

def get_leagues(bookmaker, sport_id):
    if (bookmaker == "1xstavka"):
        params = {
            'sport': sport_id,
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