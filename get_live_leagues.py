import requests
from bs4 import BeautifulSoup

proxies = {
    'http': 'https://user118643:7y3szh@91.147.122.72:6278'
}

def get_leagues(bookmaker, sport_id):
    try:
        if (bookmaker == "1xstavka"):
            params = {
                'sports': sport_id,
                'count': '50',
                'antisports': '188',
                'mode': '4',
                'country': '1',
                'partner': '51',
                'getEmpty': 'true',
                'noFilterBlockEvent': 'true',
            }

            response = requests.get('https://1xstavka.ru/LiveFeed/Get1x2_VZip', params=params, proxies=proxies)
            result = response.json()
            return result
        if (bookmaker == "marathonbet"):
            params = {
                'siteStyle': 'MULTIMARKETS',
                'oddsType': 'Decimal',
                'timeZone': 'Europe/Moscow',
                'pageAction': 'default',
            }
            response = requests.get('https://www.marathonbet.ru/su/live/' + str(sport_id), params=params, proxies=proxies)
            result = BeautifulSoup(response.text, 'html.parser')
            return result
    except Exception as ex:
        print("[INFO] Error:", ex)
    finally:
        pass