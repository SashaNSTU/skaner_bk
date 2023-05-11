import psycopg2
import requests
import re
from datetime import datetime
import datetime
from bs4 import BeautifulSoup
from get_leagues import get_leagues
from config import host, user, password, db_name
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

def marathon_update_games(sport):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True

        bookmaker = 'marathonbet'

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT sports.id FROM sports
                INNER JOIN bookmaker_sports ON sports.id = bookmaker_sports.fk_sport_id
                INNER JOIN bookmakers ON bookmaker_sports.fk_bookmaker_id = bookmakers.id
                WHERE sports.name_sport = %s AND bookmakers.name_bookmaker = %s;""",
                (sport, bookmaker)
            )
            sport_id = cursor.fetchone()[0]

        leagues = get_leagues(bookmaker, sport_id)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM bookmakers WHERE name_bookmaker = %s;",
                (bookmaker,)
            )
            result = cursor.fetchone()
            if result:
                bookmaker_id = result[0]

        leagues_containers = leagues.find_all('div', {'id': re.compile('container_(\d+)')})

        for league in leagues_containers:
            leagues_id = league['id'].split('_')[1].strip('\\"')
            span = league.find('span')
            name_league = span.text
            name_league = name_league[:-1]
            if span is not None:

                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO leagues(league_id, name_league, fk_sport_id) 
                        VALUES (%s, %s, %s);""",
                        (leagues_id, name_league, sport_id)
                    )
                    print("[INFO] Data was successfully inserted")

                div_league_id = leagues.find("div", {"id": '\\"category' + str(leagues_id) + '\\"'})
                div_game_id = div_league_id.find_all("div", {"data-event-treeid": True})
                for div in div_game_id:
                    game_id = div["data-event-treeid"]
                    game = div.find_all("div", class_=re.compile("member-name"))
                    game_time = div.find("td", {"class": '\\"date'})
                    date_str = game_time.text.strip()
                    if (len(date_str) < 6):
                        today = datetime.datetime.now()
                        today_month_day = today.strftime("%m-%d")
                        formatted_date = today_month_day + " " + date_str + ":00"
                    else:
                        for k, v in months_dict.items():
                            date_str = date_str.replace(k, v)
                        date = datetime.datetime.strptime(date_str, '%d %B %H:%M')
                        formatted_date = date.strftime('%m-%d %H:%M:%S')
                    digits = ''.join(filter(str.isdigit, game_id))
                    team_names = [g.find("span").text for g in game]
                    team1 = team_names[1]
                    team2 = team_names[0]
                    if team1 is None or team2 is None or game_id is None:  # проверка на наличие значения
                        continue
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """INSERT INTO games(game_id, game_date, name_team1, name_team2, fk_league_id, fk_bookmaker_id) 
                            VALUES (%s, %s, %s, %s, %s, %s);""",
                            (digits, formatted_date, team1, team2, leagues_id, bookmaker_id)
                        )
                        print("[INFO] Data was successfully inserted", leagues_id)



    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        if connection:
            connection.close()

