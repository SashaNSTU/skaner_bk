import psycopg2
from xstavka_get_games import xstavka_update_games
from marathon_get_games import marathon_update_games
from config import host, user, password, db_name
import numpy as np
from difflib import SequenceMatcher

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    distances = np.zeros((len(s1) + 1, len(s2) + 1))
    for i in range(len(s1) + 1):
        distances[i][0] = i
    for j in range(len(s2) + 1):
        distances[0][j] = j
    for j in range(1, len(s2) + 1):
        for i in range(1, len(s1) + 1):
            if s1[i - 1] == s2[j - 1]:
                distances[i][j] = distances[i - 1][j - 1]
            else:
                distances[i][j] = min(distances[i - 1][j], distances[i][j - 1], distances[i - 1][j - 1]) + 1
    return distances[len(s1)][len(s2)]


try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM games;")
        print("[INFO] Table 'games' has been cleared successfully")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM leagues;")
        print("[INFO] Table 'leagues' has been cleared successfully")
except Exception as ex:
    print("[INFO] Error", ex)
finally:
    if connection:
        connection.close()

marathon_update_games("Basketball")
xstavka_update_games("Basketball")


# print(SequenceMatcher(None, "Зенит Санкт-Петербург ЦСКА Москва", "Зенит ЦСКА").ratio())

try:
    connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )

    with connection.cursor() as cursor:
    # выполнение запроса на выборку данных
        cursor.execute("SELECT name_team1, name_team2 FROM games")
        records = cursor.fetchall()
        games = []

        for record in records:
            games.append(record[0] + " " + record[1])

    for i, game1 in enumerate(games):
        for j in range(i + 1, len(games)):
            game2 = games[j]
            similarity = SequenceMatcher(None, game1, game2).ratio()
            if(similarity > 0.73):
                print(f"Similarity between {game1} and {game2}: {similarity}")



except Exception as ex:
    print("[INFO] Error", ex)
finally:
    connection.close()

# try:
#     connection = psycopg2.connect(
#         host=host,
#         user=user,
#         password=password,
#         database=db_name
#     )
#     connection.autocommit = True
#     with connection.cursor() as cursor:
#         # выбираем все записи из таблицы games
#         cursor.execute("SELECT DISTINCT name_team1 FROM games")
#         team_names = cursor.fetchall()
#         for game in team_names:
#             team1 = game[0]
#             cursor.execute("SELECT game_id, name_team1, name_team2, fk_bookmaker_id FROM games WHERE name_team1 = %s", (team1,))
#             games_with_team = cursor.fetchall()
#             for game1 in games_with_team:
#                 for game2 in games_with_team:
#                     if game1[0] != game2[0] and game1[3] != game2[3]:
#                         if levenshtein_distance(game1[1], game2[1]) < 15.0 and levenshtein_distance(game1[2], game2[2]) < 15.0:
#                             break
#                 else:
#                     cursor.execute("DELETE FROM games WHERE game_id = %s", (game1[0],))
# except Exception as ex:
#     print("[INFO] Error", ex)
# finally:
#     connection.close()
