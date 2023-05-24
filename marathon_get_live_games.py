import time
from datetime import datetime
from get_live_leagues import get_leagues
from config import host, user, password, db_name
import psycopg2
import re
import datetime
import pytz

months_dict = {
        'янв': 'January',
        'фев': 'February',
        'мар': 'March',
        'апр': 'April',
        'мая': 'May',
        'июн': 'June',
        'июл': 'July',
        'авг': 'August',
        'сен': 'September',
        'окт': 'October',
        'ноя': 'November',
        'дек': 'December'
}

def marathon_update_live_games(sport):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True
        bookmaker = 'marathonbet'
        sport_live = sport + 'Live'

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT sports.sport_id FROM sports
                INNER JOIN bookmaker_sports ON sports.id = bookmaker_sports.sport_id
                INNER JOIN bookmakers ON bookmaker_sports.bookmaker_id = bookmakers.id
                WHERE sports.sport_name = %s AND bookmakers.name_bookmaker = %s;""",
                (sport_live, bookmaker)
            )
            sport_live_id = cursor.fetchone()[0]

        leagues = get_leagues(bookmaker, sport_live_id)

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT bookmaker_sports.id 
                FROM bookmaker_sports
                INNER JOIN bookmakers ON bookmaker_sports.bookmaker_id = bookmakers.id
                INNER JOIN sports ON bookmaker_sports.sport_id = sports.id
                WHERE bookmakers.name_bookmaker = %s AND sports.sport_name = %s;""",
                (bookmaker, sport_live)
            )
            result = cursor.fetchone()
            if result:
                fk_bookmaker_sport_id = result[0]


        leagues_containers = leagues.find_all('div', {'id': re.compile('container_(\d+)')})

        for league in leagues_containers:
            leagues_id = league['id'].split('_')[1].strip('\\"')

            span = league.find('span')
            name_league = span.text
            name_league = name_league[:-1]
            if span is not None:

                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO leagues(league_id, league_name, fk_bookmaker_sport_id) 
                                        VALUES (%s, %s, %s);""",
                        (leagues_id, name_league, fk_bookmaker_sport_id)
                    )
                    # print("[INFO] Data was successfully inserted")

                div_league_id = leagues.find("div", {"id": '\\"category' + str(leagues_id) + '\\"'})
                div_game_id = div_league_id.find_all("div", {"data-event-treeid": True})
                for div in div_game_id:
                    game_id = div["data-event-treeid"]
                    game = div.find_all("div", class_=re.compile("command"))
                    member_name = [g.find("b").text[:1] for g in game]
                    date_game = 'LIVE'
                    digits = ''.join(filter(str.isdigit, game_id))
                    team_names = [g.find("span").text for g in game]
                    if (member_name[0] == '1'):
                        team1 = team_names[0]
                        team2 = team_names[1]
                    else:
                        team1 = team_names[1]
                        team2 = team_names[0]
                    if team1 is None or team2 is None or game_id is None:  # проверка на наличие значения
                        continue
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT id FROM leagues WHERE league_id = %s;",
                            (league['id'].split('_')[1].strip('\\"'),)
                        )
                        league_id = cursor.fetchone()[0]
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """INSERT INTO games(game_id, date_game, name_team1, name_team2, league_id, sport_name, bookmaker_name) 
                                                    VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                            (digits, date_game, team1, team2, league_id, sport, bookmaker)
                        )
                        # print("[INFO] Data was successfully inserted", league_id)
                    # ODDS
                    RESULT = div.find_all('td', attrs={'data-market-type': '\\"RESULT_2WAY\\"'})
                    for i in range(0, len(RESULT)):
                        span_element = RESULT[i].find('span')
                        if span_element:
                            odd = span_element.get_text()
                            if odd != '—':
                                if (member_name[0] == '1' and i == 0):
                                    bet_descript = "П1"
                                if (member_name[0] == '1' and i == 1):
                                    bet_descript = "П2"
                                if (member_name[0] == '2' and i == 0):
                                    bet_descript = "П2"
                                if (member_name[0] == '2' and i == 1):
                                    bet_descript = "П1"
                                with connection.cursor() as cursor:
                                    # Получение bet_type_id из таблицы bet_types
                                    cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("РЕЗУЛЬТАТ",))
                                    bet_type_id = cursor.fetchone()[
                                        0]  # Получение значения первого столбца первой строки
                                    # Вставка записи в таблицу odds
                                    cursor.execute(
                                        """INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                                           VALUES (%s, %s, %s, %s, %s);""",
                                        (digits, league_id, bet_type_id, odd, bet_descript)
                                    )

                    RESULT_PNP = div.find_all('td', attrs={'data-market-type': '\\"RESULT\\"'})
                    for i in range(0, len(RESULT_PNP)):
                        span_element = RESULT_PNP[i].find('span')
                        if span_element:
                            odd = span_element.get_text()
                            if odd != '—':
                                if (member_name[0] == '1' and i == 0):
                                    bet_descript = "П1"
                                if (member_name[0] == '1' and i == 2):
                                    bet_descript = "П2"
                                if (member_name[0] == '2' and i == 0):
                                    bet_descript = "П2"
                                if (member_name[0] == '2' and i == 2):
                                    bet_descript = "П1"
                                if i == 1:
                                    bet_descript = "Н"
                                with connection.cursor() as cursor:
                                    # Получение bet_type_id из таблицы bet_types
                                    cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("РЕЗУЛЬТАТ_ПНП",))
                                    bet_type_id = cursor.fetchone()[
                                        0]  # Получение значения первого столбца первой строки
                                    # Вставка записи в таблицу odds
                                    cursor.execute(
                                        """INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                                           VALUES (%s, %s, %s, %s, %s);""",
                                        (digits, league_id, bet_type_id, odd, bet_descript)
                                    )

                    HANDICAP = div.find_all('td', attrs={'data-market-type': '\\"HANDICAP\\"'})
                    for i in range(0, len(HANDICAP)):
                        span_element = HANDICAP[i].find('span')
                        if span_element:
                            odd = span_element.get_text()
                            if odd != '—':
                                if (member_name[0] == '1' and i == 0):
                                    bet_descript = "1 " + HANDICAP[i].contents[0].get_text(strip=True) if HANDICAP[0].contents else ''
                                    bet_descript = bet_descript.replace('(', '').replace(')', '')
                                if (member_name[0] == '1' and i == 1):
                                    bet_descript = "2 " + HANDICAP[i].contents[0].get_text(strip=True) if HANDICAP[0].contents else ''
                                    bet_descript = bet_descript.replace('(', '').replace(')', '')
                                if (member_name[0] == '2' and i == 0):
                                    bet_descript = "2 " + HANDICAP[i].contents[0].get_text(strip=True) if HANDICAP[0].contents else ''
                                    bet_descript = bet_descript.replace('(', '').replace(')', '')
                                if (member_name[0] == '2' and i == 1):
                                    bet_descript = "1 " + HANDICAP[i].contents[0].get_text(strip=True) if HANDICAP[0].contents else ''
                                    bet_descript = bet_descript.replace('(', '').replace(')', '')
                                with connection.cursor() as cursor:
                                    # Получение bet_type_id из таблицы bet_types
                                    cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("ФОРА",))
                                    bet_type_id = cursor.fetchone()[
                                        0]  # Получение значения первого столбца первой строки
                                    # Вставка записи в таблицу odds
                                    cursor.execute(
                                        """INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                                           VALUES (%s, %s, %s, %s, %s);""",
                                        (digits, league_id, bet_type_id, odd, bet_descript)
                                    )

                    TOTAL = div.find_all('td', attrs={'data-market-type': '\\"TOTAL\\"'})
                    for i in range(0, len(TOTAL)):
                        span_element = TOTAL[i].find('span')
                        if span_element:
                            odd = span_element.get_text()
                            if odd != '—':
                                if (i == 0):
                                    bet_descript = TOTAL[i].contents[0].get_text(strip=True) if TOTAL[
                                        0].contents else ''
                                    bet_descript = bet_descript.replace('(', '').replace(')', '') + " М"
                                if (i == 1):
                                    bet_descript = TOTAL[i].contents[0].get_text(strip=True) if HANDICAP[
                                        0].contents else ''
                                    bet_descript = bet_descript.replace('(', '').replace(')', '') + " Б"

                                with connection.cursor() as cursor:
                                    # Получение bet_type_id из таблицы bet_types
                                    cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("ТОТАЛ",))
                                    bet_type_id = cursor.fetchone()[
                                        0]  # Получение значения первого столбца первой строки

                                    # Вставка записей в таблицу odds
                                    query = """
                                        INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                                        VALUES (%s, %s, %s, %s, %s);
                                    """
                                    params = (digits, league_id, bet_type_id, odd, bet_descript)
                                    cursor.execute(query, params)
    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        if connection:
            connection.close()

