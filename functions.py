import time

from config import host, user, password, db_name
from telegram_bot import send_telegram
import psycopg2

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
            # выполнение запроса на выборку данных
            cursor.execute("""
                    SELECT g1.game_id, g1.name_team1, g1.name_team2, g1.date_game, g1.bookmaker_name, g1.league_id
                    FROM games g1
                    INNER JOIN games g2 ON (g1.name_team1 = g2.name_team1 AND g1.name_team2 = g2.name_team2 AND g1.game_id != g2.game_id)
                    WHERE g1.bookmaker_name <> g2.bookmaker_name
                    ORDER BY g1.name_team1, g1.name_team2, g1.date_game
                """)
            records = cursor.fetchall()

            with connection.cursor() as cursor:
                # Составление списка значений (game_id, league_id) из переменной records
                values = [f"({record[0]}, {record[5]})" for record in records]

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

    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        connection.close()

def find_bets():
    try:
        # Создание курсора
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True

        cursor = connection.cursor()

        # Выполнение запроса для получения game_ids и bookmaker_names
        cursor.execute("""
            SELECT g.name_team1, g.name_team2, g.date_game, ARRAY_AGG(g.game_id) AS game_ids,
            ARRAY_AGG(g.bookmaker_name) AS bookmaker_names
            FROM games g
            JOIN (
              SELECT name_team1, name_team2
              FROM games
              GROUP BY name_team1, name_team2
              HAVING COUNT(*) > 1
            ) AS dup ON g.name_team1 = dup.name_team1 AND g.name_team2 = dup.name_team2
            GROUP BY g.name_team1, g.name_team2, g.date_game;
        """)

        # Получение результатов запроса
        rows = cursor.fetchall()

        for row in rows:
            name_team1, name_team2, date_game, game_ids, bookmaker_names = row
            # print(f"Teams: {name_team1} vs {name_team2}")

            odds_result2way_1 = [None, None]  # Создание массива с двумя элементами
            odds_result2way_2 = [None, None]
            odds_result3way_1 = [None, None, None]  # Создание массива с двумя элементами
            odds_result3way_2 = [None, None, None]

            odds1_handicap= []
            odds2_handicap = []
            odds1_total = []
            odds2_total = []



            for index, (game_id, bookmaker_name) in enumerate(zip(game_ids, bookmaker_names)):

                # print(f"Game ID: {game_id}, Bookmaker: {bookmaker_name}")

                cursor.execute("""
                    SELECT odd_value, bet_description
                    FROM odds
                    WHERE game_id = %s AND (bet_type_id = 1 OR bet_type_id = 4);
                """, (game_id,))
                odds_result = cursor.fetchall()

                cursor.execute("""
                    SELECT odd_value, bet_description
                    FROM odds
                    WHERE game_id = %s AND bet_type_id = 3;
                """, (game_id,))
                odds_handicap = cursor.fetchall()

                cursor.execute("""
                    SELECT odd_value, bet_description
                    FROM odds
                    WHERE game_id = %s AND bet_type_id = 2;
                """, (game_id,))
                odds_total = cursor.fetchall()

                # Поиск вилок на РЕЗУЛЬТАТ
                odds_res = []


                if len(odds_result) == 2:
                    for i in range(len(odds_result)):
                        if (index == 0):
                            if odds_result[i][1] == 'П1':
                                odds_result2way_1[0] = float(odds_result[i][0])  # Внесение значения в первый элемент массива
                            elif odds_result[i][1] == 'П2':
                                odds_result2way_1[1] = float(odds_result[i][0])  # Внесение значения во второй элемент массива
                        if (index == 1):
                            if odds_result[i][1] == 'П1':
                                odds_result2way_2[0] = float(odds_result[i][0])  # Внесение значения в первый элемент массива
                            elif odds_result[i][1] == 'П2':
                                odds_result2way_2[1] = float(odds_result[i][0])  # Внесение значения во второй элемент массива

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
                            print(
                                f"Arbitrage opportunity found for Game: {name_team1} vs {name_team2}\nBookmakers: {odd_values[0]}, {odd_values[1]}\nOdds: \n")

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
                                # print(odds_result2way_1[i], bookmaker_names[0])
                            else:
                                odds_res.append((odds_result3way_2[i], bookmaker_names[1], odds_result[i][1]))
                                # print(odds_result2way_2[i], bookmaker_names[1])
                    if len(odds_res) == 3:
                        odd_values = [odd[0] for odd in odds_res]
                        if 1 / odd_values[0] + 1 / odd_values[1] + 1 / odd_values[2] < 1:
                            print(f"Arbitrage opportunity found for Game: {name_team1} vs {name_team2}\nBookmakers: {odd_values[0]}, {odd_values[1]}\nOdds: {odd_values[2]}\n")




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

                #Поиск вилок на ФОРУ
                if odds_handicap:
                    for odd in odds_handicap:
                        if index == 0:
                            odds_value = float(odd[0])
                            odds1_handicap.append((odds_value, odd[1]))  # Добавление кортежа в список odds1
                        if index == 1:
                            odds_value = float(odd[0])
                            odds2_handicap.append((odds_value, odd[1]))  # Добавление кортежа в список odds2

                odd_handicap = []
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
                            f"{bookmaker_names[0]} | {bookmaker_names[1]}\n"
                            f"Values: {odd_handicap[0][1]} | {odd_handicap[1][1]}\n"
                            f"Odds: {odd_handicap[0][0]} | {odd_handicap[1][0]}\n"
                        )

                #Поиск вилок на ТОТАЛ
                if odds_total:
                    for odd in odds_total:
                        # print(odd[1])
                        if index == 0:
                            odds_value = float(odd[0])
                            odds1_total.append((odds_value, odd[1]))  # Добавление кортежа в список odds1
                        if index == 1:
                            odds_value = float(odd[0])
                            odds2_total.append((odds_value, odd[1]))  # Добавление кортежа в список odds2

                    odd_total = []
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
                                f"{bookmaker_names[0]} | {bookmaker_names[1]}\n"
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

