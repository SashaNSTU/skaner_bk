import re
import requests
from datetime import datetime
import datetime
from bs4 import BeautifulSoup
params = {
    'pageAction': 'default',
    '_': '1683634845180',
}
months_dict = {
        'января': 'January',
        'февраля': 'February',
        'марта': 'March',
        'апреля': 'April',
        'мая': 'May',
        'июня': 'June',
        'июля': 'July',
        'августа': 'August',
        'сентября': 'September',
        'октября': 'October',
        'ноября': 'November',
        'декабря': 'December'
    }

response = requests.get('https://www.marathonbet.ru/su/betting/6', params=params )
soup = BeautifulSoup(response.text, 'html.parser')


containers = soup.find_all('div', {'id': re.compile('container_(\d+)')})


for container in containers:
    container_id = container['id'].split('_')[1].strip('\\"')
    span = container.find('span')
    name_league = span.text
    name_league = name_league[:-1]
    if span is not None:
        print(container_id, "|", name_league)
        div_league_id = soup.find("div", {"id": '\\"category' + str(container_id) + '\\"'})
        div_game_id = div_league_id.find_all("div", {"data-event-treeid": True})
        for div in div_game_id:
            game_id = div["data-event-treeid"]
            game = div.find_all("div", class_=re.compile("member-name"))
            game_time = div.find("td", {"class": '\\"date'})
            date_str = game_time.text.strip()
            if(len(date_str) < 6):
                today = datetime.datetime.now()
                today_month_day = today.strftime("%m-%d")
                formatted_date = today_month_day + " " + date_str+":00"
            else:
                for k, v in months_dict.items():
                    date_str = date_str.replace(k, v)
                date = datetime.datetime.strptime(date_str, '%d %B %H:%M')
                formatted_date = date.strftime('%m-%d %H:%M:%S')
            print(formatted_date)
            digits = ''.join(filter(str.isdigit, game_id))
            team_names = [g.find("span").text for g in game]
            if len(team_names) >= 2:
                team1 = team_names[0]
                team2 = team_names[1]
                print(digits, " | ", team1, " - ", team2)
            else:
                print(digits, " | Error: team names not found")



