import psycopg2

from datetime import datetime
import datetime
from get_leagues import get_leagues
from get_games import get_games
from config import host, user, password, db_name

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
                """SELECT sports.id FROM sports
                INNER JOIN bookmaker_sports ON sports.id = bookmaker_sports.fk_sport_id
                INNER JOIN bookmakers ON bookmaker_sports.fk_bookmaker_id = bookmakers.id
                WHERE sports.name_sport = %s AND bookmakers.name_bookmaker = %s;""",
                (sport, bookmaker)
            )
            sport_id = cursor.fetchone()[0]

        leagues = get_leagues(bookmaker, sport_id)

        for champ in range(0, len(leagues["Value"])):
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO leagues(league_id, name_league, fk_sport_id) 
                    VALUES (%s, %s, %s);""",
                    (leagues["Value"][champ]["LI"], leagues["Value"][champ]["L"], sport_id)
                )
                print("[INFO] Data was successfully inserted")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM bookmakers WHERE name_bookmaker = %s;",
                (bookmaker,)
            )
            result = cursor.fetchone()
            if result:
                bookmaker_id = result[0]

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT league_id FROM leagues;"""
            )
            rows = cursor.fetchall()
            ids = [row[0] for row in rows]
            for champ in range(0, len(ids)):
                games = get_games(ids[champ])
                if len(games["Value"]) > 0:
                    for game in range(0, len(games["Value"])):
                        game_id = games["Value"][game].get("CI")
                        team1 = games["Value"][game].get("O1")
                        team2 = games["Value"][game].get("O2")
                        timestamp = games["Value"][game].get("S") - 4 * 3600
                        game_date = datetime.datetime.fromtimestamp(timestamp)
                        game_date = game_date.strftime('%m-%d %H:%M:%S')
                        if team1 is None or team2 is None or game_id is None:  # проверка на наличие значения
                            continue
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """INSERT INTO games(game_id, game_date, name_team1, name_team2, fk_league_id, fk_bookmaker_id) 
                                VALUES (%s, %s, %s, %s, %s, %s);""",
                                (game_id, game_date, team1, team2, ids[champ], bookmaker_id)
                            )
                            print("[INFO] Data was successfully inserted", ids[champ])

    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        if connection:
            connection.close()
