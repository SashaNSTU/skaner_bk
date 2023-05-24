from get_leagues import get_leagues
from config import host, user, password, db_name
from datetime import datetime
import psycopg2
import datetime


def xstavka_update_games(sport):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True

        bookmaker = '1xstavka'

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT sports.sport_id FROM sports
                INNER JOIN bookmaker_sports ON sports.id = bookmaker_sports.sport_id
                INNER JOIN bookmakers ON bookmaker_sports.bookmaker_id = bookmakers.id
                WHERE sports.sport_name = %s AND bookmakers.name_bookmaker = %s;""",
                (sport, bookmaker)
            )
            sport_id = cursor.fetchone()[0]


        leagues = get_leagues(bookmaker, sport_id)

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT bookmaker_sports.id 
                FROM bookmaker_sports
                INNER JOIN bookmakers ON bookmaker_sports.bookmaker_id = bookmakers.id
                INNER JOIN sports ON bookmaker_sports.sport_id = sports.id
                WHERE bookmakers.name_bookmaker = %s AND sports.sport_name = %s;""",
                (bookmaker, sport)
            )
            result = cursor.fetchone()

            if result:
                fk_bookmaker_sport_id = result[0]

        for champ in range(0, len(leagues["Value"])):
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT league_id FROM leagues 
                    WHERE league_id = %s """,
                    (leagues["Value"][champ]["LI"],)
                )
                result = cursor.fetchone()
                if result is None:
                    cursor.execute(
                    """INSERT INTO leagues(league_id, league_name, fk_bookmaker_sport_id) 
                                        VALUES (%s, %s, %s);""",
                    (leagues["Value"][champ]["LI"], leagues["Value"][champ]["L"], fk_bookmaker_sport_id)
                    )
                    # print("[INFO] Data was successfully inserted")
                else:
                    pass

                game_id = leagues["Value"][champ].get("CI")
                team1 = leagues["Value"][champ].get("O1")
                team2 = leagues["Value"][champ].get("O2")
                timestamp = leagues["Value"][champ].get("S") - 4 * 3600
                date_game = datetime.datetime.fromtimestamp(timestamp)
                date_game = date_game.strftime('%m-%d %H:%M:%S')
                if team1 is None or team2 is None or game_id is None:  # проверка на наличие значения
                    continue
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM leagues WHERE league_id = %s;",
                        (leagues["Value"][champ]["LI"],)
                    )
                    league_id = cursor.fetchone()[0]
                    cursor.execute(
                        """INSERT INTO games(game_id, date_game, name_team1, name_team2, league_id, sport_name, bookmaker_name) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                        (game_id, date_game, team1, team2, league_id, sport,  bookmaker)
                    )
                    # print("[INFO] Data was successfully inserted", league_id)



                RESULT = leagues["Value"][champ].get("E")
                odds = [odd["C"] for odd in RESULT if odd.get("G") == 1 or odd.get("G") == 2766]
                for i in range(0, len(odds)):
                    if (len(odds) == 3):
                        if i == 0:
                            odd = odds[i]
                            bet_descript = "П1"
                        if i == 1:
                            odd = odds[i]
                            bet_descript = "Н"
                        if i == 2:
                            odd = odds[i]
                            bet_descript = "П2"
                        with connection.cursor() as cursor:
                            # Получение bet_type_id из таблицы bet_types
                            cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("РЕЗУЛЬТАТ_ПНП",))
                            bet_type_id = cursor.fetchone()[0]  # Получение значения первого столбца первой строки
                            # Вставка записи в таблицу odds
                            cursor.execute(
                                """INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                                   VALUES (%s, %s, %s, %s, %s);""",
                                (game_id, league_id, bet_type_id, odd, bet_descript)
                            )
                    if (len(odds) == 2):
                        if i == 0:
                            odd = odds[i]
                            bet_descript = "П1"
                        if i == 1:
                            odd = odds[i]
                            bet_descript = "П2"
                        with connection.cursor() as cursor:
                            # Получение bet_type_id из таблицы bet_types
                            cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("РЕЗУЛЬТАТ",))
                            bet_type_id = cursor.fetchone()[0]  # Получение значения первого столбца первой строки
                            # Вставка записи в таблицу odds
                            cursor.execute(
                                """INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                                   VALUES (%s, %s, %s, %s, %s);""",
                                (game_id, league_id, bet_type_id, odd, bet_descript)
                            )

                AE = leagues["Value"][champ].get("AE")
                TOTAL_BLOCK = [block for block in AE if block["G"] == 17 and "ME" in block]
                TOTALS = TOTAL_BLOCK[0]["ME"] if TOTAL_BLOCK else []
                for i in range(0, len(TOTALS)):
                    if (TOTALS[i].get("T") == 9):
                        odd = TOTALS[i].get("C")
                        bet_descript = str(float(TOTALS[i].get("P"))) + ' Б'
                    if (TOTALS[i].get("T") == 10):
                        odd = TOTALS[i].get("C")
                        bet_descript = str(float(TOTALS[i].get("P"))) + ' М'
                    with connection.cursor() as cursor:
                        # Получение bet_type_id из таблицы bet_types
                        cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("ТОТАЛ",))
                        bet_type_id = cursor.fetchone()[0]  # Получение значения первого столбца первой строки
                        # Вставка записи в таблицу odds
                        cursor.execute(
                            """INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                               VALUES (%s, %s, %s, %s, %s);""",
                            (game_id, league_id, bet_type_id, odd, bet_descript)
                        )

                HANDICAP_BLOCK = [block for block in AE if block["G"] == 2 and "ME" in block]
                HANDICAPS = HANDICAP_BLOCK[0]["ME"] if HANDICAP_BLOCK else []
                for i in range(0, len(HANDICAPS)):
                    if (HANDICAPS[i].get("T") == 7):
                        odd = HANDICAPS[i].get("C")
                        bet_descript = '1 +' + str(float(HANDICAPS[i].get("P"))) if HANDICAPS[i].get("P") is not None and float(HANDICAPS[i].get("P")) > 0 else '1 ' + str(float(HANDICAPS[i].get("P"))) if HANDICAPS[i].get("P") is not None else '1 0'
                    if (HANDICAPS[i].get("T") == 8):
                        odd = HANDICAPS[i].get("C")
                        bet_descript = '2 +' + str(float(HANDICAPS[i].get("P"))) if HANDICAPS[i].get("P") is not None and float(HANDICAPS[i].get("P")) > 0 else '2 ' + str(float(HANDICAPS[i].get("P"))) if HANDICAPS[i].get("P") is not None else '2 0'
                    with connection.cursor() as cursor:
                        # Получение bet_type_id из таблицы bet_types
                        cursor.execute("SELECT id FROM bet_types WHERE name = %s", ("ФОРА",))
                        bet_type_id = cursor.fetchone()[0]  # Получение значения первого столбца первой строки
                        # Вставка записи в таблицу odds
                        cursor.execute(
                            """INSERT INTO odds (game_id, league_id, bet_type_id, odd_value, bet_description)
                               VALUES (%s, %s, %s, %s, %s);""",
                            (game_id, league_id, bet_type_id, odd, bet_descript)
                        )
                        # print(bet_descript)

    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        if connection:
            connection.close()
