import requests
def get_games(leagues):
    params = {
        'champs': leagues,
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
    games = response.json()
    return games