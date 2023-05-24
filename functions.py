import time

from config import host, user, password, db_name
from telegram_bot import send_telegram
import psycopg2

def jaccard_similarity(str1, str2):
    str1 = str1.lower()
    str2 = str2.lower()
    set1 = set(str1)
    set2 = set(str2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    similarity = len(intersection) / len(union)
    return similarity
def update_db():
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
            # print("[INFO] Table 'odds' has been cleared successfully")
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM games;")
            # print("[INFO] Table 'games' has been cleared successfully")
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM leagues;")
            cursor.execute("ALTER SEQUENCE leagues_id_seq RESTART WITH 1;")
            # print("[INFO] Table 'leagues' has been cleared successfully")

    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        if connection:
            connection.close()

def delete_not_repetitive():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            # Выполнение запроса на выборку данных
            cursor.execute(
                "SELECT name_team1, name_team2, date_game, bookmaker_name, sport_name, game_id, league_id FROM games")
            records = cursor.fetchall()
            games = []

            for record in records:
                game = record[0] + " " + record[1]
                games.append((game, record[2], record[3], record[4], record[5], record[6]))

        result_games = []
        find_games = []
        for i, game1 in enumerate(games):
            for j in range(i + 1, len(games)):
                game2 = games[j]
                similarity = jaccard_similarity(game1[0], game2[0])
                if similarity > 0.74 and game1[1] == game2[1] and game1[2] != game2[2] and game1[3] == game2[3]:
                    result_games.append((game1[4], game1[5]))
                    result_games.append((game2[4], game2[5]))
                    find_games.append(((game1[4], game2[4]), (game1[2], game2[2])))



        with connection.cursor() as cursor:
            # Составление списка значений (game_id, league_id) из переменной records
            values = [f"({result_game[0]}, {result_game[1]})" for result_game in result_games]

            # Удаление записей из таблицы odds, исключая записи из переменной records
            if values:
                query = f"DELETE FROM odds WHERE (game_id, league_id) NOT IN ({','.join(values)});"
                cursor.execute(query)
                # print("[INFO] Records deleted from 'odds' table, except for specified records.")

        with connection.cursor() as cursor:
            # Удаление записей из таблицы games, исключая записи из переменной records
            if values:
                query = f"DELETE FROM games WHERE (game_id, league_id) NOT IN ({','.join(values)});"
                cursor.execute(query)
                # print("[INFO] Records deleted from 'games' table, except for specified records.")

        time.sleep(30)
        find_bets(find_games)
    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        connection.close()

def find_bets(games):
    try:
        # Создание курсора
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True

        for game in games:
            game_ids, bookmaker_names = game

            with connection.cursor() as cursor:
                # Выполнение запроса на выборку данных
                cursor.execute(
                    "SELECT name_team1, name_team2, date_game "
                    "FROM games "
                    "WHERE game_id = %s;",
                    (game_ids[0],)
                )
                records = cursor.fetchone()
            name_team1, name_team2, date_game = records

            odds_result2way_1 = [None, None]  # Создание массива с двумя элементами
            odds_result2way_2 = [None, None]
            odds_result3way_1 = [None, None, None]  # Создание массива с двумя элементами
            odds_result3way_2 = [None, None, None]

            odds1_handicap = []
            odds2_handicap = []
            odds1_total = []
            odds2_total = []


            for index, (game_id, bookmaker_name) in enumerate(zip(game_ids, bookmaker_names)):

                # print(f"Game ID: {game_id}, Bookmaker: {bookmaker_name}")
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT odd_value, bet_description
                        FROM odds
                        WHERE game_id = %s AND (bet_type_id = 1 OR bet_type_id = 4);
                    """, (game_id,))
                    odds_result = cursor.fetchall()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT odd_value, bet_description
                        FROM odds
                        WHERE game_id = %s AND bet_type_id = 3;
                    """, (game_id,))
                    odds_handicap = cursor.fetchall()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT odd_value, bet_description
                        FROM odds
                        WHERE game_id = %s AND bet_type_id = 2;
                    """, (game_id,))
                    odds_total = cursor.fetchall()

                # Поиск вилок на РЕЗУЛЬТАТ
                odds_res = []
                odd_handicap = []
                odd_total = []

                if len(odds_result) == 2:
                    for i in range(len(odds_result)):
                        if (index == 0):
                            if odds_result[i][1] == 'П1':
                                odds_result2way_1[0] = float(
                                    odds_result[i][0])  # Внесение значения в первый элемент массива
                            elif odds_result[i][1] == 'П2':
                                odds_result2way_1[1] = float(
                                    odds_result[i][0])  # Внесение значения во второй элемент массива
                        if (index == 1):
                            if odds_result[i][1] == 'П1':
                                odds_result2way_2[0] = float(
                                    odds_result[i][0])  # Внесение значения в первый элемент массива
                            elif odds_result[i][1] == 'П2':
                                odds_result2way_2[1] = float(
                                    odds_result[i][0])  # Внесение значения во второй элемент массива

                    if odds_result2way_1[-1] is not None and odds_result2way_2[-1] is not None:
                        # print(f"Teams: {name_team1} vs {name_team2}")
                        for i in range(0, len(odds_result2way_1)):
                            if (odds_result2way_1[i] > odds_result2way_2[i]):
                                odds_res.append((odds_result2way_1[i], bookmaker_names[0], odds_result[i][1]))
                                # print(odds_result2way_1[i], bookmaker_names[0])
                            else:
                                odds_res.append((odds_result2way_2[i], bookmaker_names[1], odds_result[i][1]))
                                # print(odds_result2way_2[i], bookmaker_names[1])
                    if len(odds_res) == 2:
                        odd_values = [odd[0] for odd in odds_res]
                        if 1 / odd_values[0] + 1 / odd_values[1] < 1:
                            send_telegram(
                                f"Arbitrage opportunity found for Game:\n"
                                f"{name_team1} vs {name_team2} ({date_game} МСК)\n"
                                f"{odds_res[0][1]} | {odds_res[1][1]}\n"
                                f"Odds: {odds_res[0][2]} {odds_res[0][0]} | {odds_res[1][2]} {odds_res[1][0]}\n"
                            )

                if len(odds_result) == 3:
                    for i in range(len(odds_result)):
                        if (index == 0):
                            if odds_result[i][1] == 'П1':
                                odds_result3way_1[0] = float(odds_result[i][0])
                            elif odds_result[i][1] == 'Н':
                                odds_result3way_1[1] = float(odds_result[i][0])
                            elif odds_result[i][1] == 'П2':
                                odds_result3way_1[2] = float(odds_result[i][0])
                        if (index == 1):
                            if odds_result[i][1] == 'П1':
                                odds_result3way_2[0] = float(odds_result[i][0])
                            elif odds_result[i][1] == 'Н':
                                odds_result3way_2[1] = float(odds_result[i][0])
                            elif odds_result[i][1] == 'П2':
                                odds_result3way_2[2] = float(odds_result[i][0])

                    if odds_result3way_1[-1] is not None and odds_result3way_2[-1] is not None:
                        # print(f"Teams: {name_team1} vs {name_team2}")
                        for i in range(0, len(odds_result3way_1)):
                            if (odds_result3way_1[i] > odds_result3way_2[i]):
                                odds_res.append((odds_result3way_1[i], bookmaker_names[0], odds_result[i][1]))
                            else:
                                odds_res.append((odds_result3way_2[i], bookmaker_names[1], odds_result[i][1]))
                    if len(odds_res) == 3:
                        odd_values = [odd[0] for odd in odds_res]
                        if 1 / odd_values[0] + 1 / odd_values[1] + 1 / odd_values[2] < 1:
                            send_telegram(
                                f"Arbitrage opportunity found for Game:\n"
                                f"{name_team1} vs {name_team2} ({date_game} МСК)\n"
                                f"{odds_res[0][1]} | {odds_res[1][1]} | {odds_res[2][1]}\n"
                                f"Odds: {odds_res[0][2]} {odds_res[0][0]} | {odds_res[1][2]} {odds_res[1][0]} | {odds_res[2][2]} {odds_res[2][0]}\n"
                            )
                # if odds_result:
                #     for odd in odds_result:
                #         if (index == 0):
                #             odds_value = float(odd[0])
                #             odds1_res.append(odds_value)
                #         if (index == 1):
                #             odds_value = float(odd[0])
                #             odds2_res.append(odds_value)
                #
                # odds_res = []
                # if len(odds1_res) == len(odds2_res):
                #     # send_message(name_team1 + " " +  name_team2)
                #     # print(f"Teams: {name_team1} vs {name_team2}")
                #
                #     for i in range(0, len(odds1_res)):
                #         if (odds1_res[i] > odds2_res[i]):
                #             odds_res.append((odds1_res[i], bookmaker_names[0]))
                #             # print(odds1_res[i], bookmaker_names[0])
                #         else:
                #             odds_res.append((odds2_res[i], bookmaker_names[1]))
                #             # print(odds2_res[i], bookmaker_names[1])
                #
                # if len(odds_res) == 3:
                #     odd_values = [odd[0] for odd in odds_res]
                #     if 1 / float(odd_values[0]) + 1 / float(odd_values[1]) + 1 / float(odd_values[2]) < 1:
                #
                #         send_telegram(
                #             f"Arbitrage opportunity found for Teams: {name_team1} vs {name_team2}\nBookmakers: {odds_res[0][1]}, {odds_res[1][1]}, {odds_res[2][1]}\nOdds: {odd_values}\n")
                #
                # if len(odds_res) == 2:
                #     odd_values = [odd[0] for odd in odds_res]
                #     if 1 / float(odd_values[0]) + 1 / float(odd_values[1]) < 1:
                #         send_telegram(
                #             f"Arbitrage opportunity found for Teams: {name_team1} vs {name_team2}\nBookmakers: {odds_res[0][1]}, {odds_res[1][1]}\nOdds: {odd_values}\n")

                # Поиск вилок на ФОРУ
                if odds_handicap:
                    for odd in odds_handicap:
                        if index == 0:
                            odds_value = float(odd[0])
                            odds1_handicap.append((odds_value, odd[1]))  # Добавление кортежа в список odds1
                        if index == 1:
                            odds_value = float(odd[0])
                            odds2_handicap.append((odds_value, odd[1]))  # Добавление кортежа в список odds2

                    if (len(odds1_handicap) > 0 and len(odds2_handicap) > 0):
                        # print(f"Teams: {name_team1} vs {name_team2}")

                        for value1 in odds1_handicap:
                            for value2 in odds2_handicap:
                                if value1[1] == value2[1]:
                                    if value1[0] > value2[0]:
                                        odd_handicap.append((value1[0], value1[1], bookmaker_names[0]))
                                        # print(value1[0], value1[1], bookmaker_names[0])
                                    else:
                                        odd_handicap.append((value2[0], value2[1], bookmaker_names[1]))
                                        # print(value2[0], value2[1], bookmaker_names[1])

                    if len(odd_handicap) == 2:
                        odd_values = [odd[0] for odd in odd_handicap]
                        # Проверка условия арбитража
                        if 1 / float(odd_values[0]) + 1 / float(odd_values[1]) < 1:
                            send_telegram(
                                f"Arbitrage opportunity found for Game:\n"
                                f"{name_team1} vs {name_team2} ({date_game} МСК)\n"
                                f"{odd_handicap[0][2]} | {odd_handicap[1][2]}\n"
                                f"Values: {odd_handicap[0][1]} | {odd_handicap[1][1]}\n"
                                f"Odds: {odd_handicap[0][0]} | {odd_handicap[1][0]}\n"
                            )

                # Поиск вилок на ТОТАЛ
                if odds_total:
                    for odd in odds_total:
                        # print(odd[1])
                        if index == 0:
                            odds_value = float(odd[0])
                            odds1_total.append((odds_value, odd[1]))  # Добавление кортежа в список odds1
                        if index == 1:
                            odds_value = float(odd[0])
                            odds2_total.append((odds_value, odd[1]))  # Добавление кортежа в список odds2

                    if (len(odds1_total) > 0 and len(odds2_total) > 0):
                        # print(f"Teams: {name_team1} vs {name_team2}")

                        for value1 in odds1_total:
                            for value2 in odds2_total:
                                if value1[1] == value2[1]:
                                    if value1[0] > value2[0]:
                                        odd_total.append((value1[0], value1[1], bookmaker_names[0]))
                                        # print(value1[0], value1[1], bookmaker_names[0])
                                    else:
                                        odd_total.append((value2[0], value2[1], bookmaker_names[1]))
                                        # print(value2[0], value2[1], bookmaker_names[1])

                    if len(odd_total) == 2:
                        odd_values = [odd[0] for odd in odd_total]
                        # Проверка условия арбитража
                        if 1 / float(odd_values[0]) + 1 / float(odd_values[1]) < 1:
                            send_telegram(
                                f"Arbitrage opportunity found for Game:\n"
                                f"{name_team1} vs {name_team2} ({date_game} МСК)\n"
                                f"{odd_total[0][2]} | {odd_total[1][2]}\n"
                                f"Values: {odd_total[0][1]} | {odd_total[1][1]}\n"
                                f"Odds: {odd_total[0][0]} | {odd_total[1][0]}\n"
                            )
        # Закрытие курсора
        cursor.close()
    except Exception as ex:
        print("[INFO] Error:", ex)
    finally:
        # Закрытие соединения
        connection.close()

