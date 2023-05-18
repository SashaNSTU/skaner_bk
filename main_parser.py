import psycopg2
import time
import numpy as np

from xstavka_get_games import xstavka_update_games
from marathon_get_games import marathon_update_games
from config import host, user, password, db_name
from difflib import SequenceMatcher

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM odds;")
        print("[INFO] Table 'odds' has been cleared successfully")
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM games;")
        print("[INFO] Table 'games' has been cleared successfully")
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM leagues;")
        cursor.execute("ALTER SEQUENCE leagues_id_seq RESTART WITH 1;")
        print("[INFO] Table 'leagues' has been cleared successfully")

except Exception as ex:
    print("[INFO] Error", ex)
finally:
    if connection:
        connection.close()

marathon_update_games("Football")
xstavka_update_games("Football")
marathon_update_games("Basketball")
xstavka_update_games("Basketball")
marathon_update_games("Tennis")
xstavka_update_games("Tennis")

# marathon_update_games("Football")


# try:
#     connection = psycopg2.connect(
#                 host=host,
#                 user=user,
#                 password=password,
#                 database=db_name
#             )
#
#     with connection.cursor() as cursor:
#     # выполнение запроса на выборку данных
#         cursor.execute("SELECT name_team1, name_team2 FROM games")
#         records = cursor.fetchall()
#         games = []
#
#         for record in records:
#             games.append(record[0] + " " + record[1])
#
#     for i, game1 in enumerate(games):
#         for j in range(i + 1, len(games)):
#             game2 = games[j]
#             similarity = SequenceMatcher(None, game1, game2).ratio()
#             if(similarity > 0.73):
#                 print(f"Similarity between {game1} and {game2}: {similarity}")
#
#
#
# except Exception as ex:
#     print("[INFO] Error", ex)
# finally:
#     connection.close()



# try:
#     connection = psycopg2.connect(
#         host=host,
#         user=user,
#         password=password,
#         database=db_name
#     )
#     connection.autocommit = True
#
#     with connection.cursor() as cursor:
#         # выполнение запроса на выборку данных
#         cursor.execute("""
#                 SELECT g1.game_id, g1.name_team1, g1.name_team2, g1.date_game, g1.bookmaker_name, g1.league_id
#                 FROM games g1
#                 INNER JOIN games g2 ON (g1.name_team1 = g2.name_team1 AND g1.name_team2 = g2.name_team2 AND g1.game_id != g2.game_id)
#                 WHERE g1.bookmaker_name != g2.bookmaker_name
#                 ORDER BY g1.name_team1, g1.name_team2, g1.date_game
#             """)
#         records = cursor.fetchall()
#
#         with connection.cursor() as cursor:
#             cursor.execute("DELETE FROM games;")
#             print("[INFO] Table 'games' has been cleared successfully")
#         for record in records:
#             game_id, name_team1, name_team2, date_time, bookmaker_name, league_id = record
#             # print(f"Game {game_id}: {name_team1} vs {name_team2} at {date_time}, bookmaker_id: {bookmaker_name}, league_id: {league_id}")
#             with connection.cursor() as cursor:
#                 cursor.execute(
#                     "INSERT INTO games (game_id, name_team1, name_team2, date_game, bookmaker_name, league_id) "
#                     "VALUES (%s, %s, %s, %s, %s, %s)",
#                     (game_id, name_team1, name_team2, date_time, bookmaker_name, league_id))
# except Exception as ex:
#     print("[INFO] Error", ex)
# finally:
#     connection.close()

