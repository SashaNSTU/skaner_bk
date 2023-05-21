from xstavka_get_games import xstavka_update_games
from marathon_get_games import marathon_update_games
from config import host, user, password, db_name
from find_arbitrage import find_bets
import psycopg2
import threading
import time


while True:
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

    start_time = time.time()
    # Ваш код программы
    sports = ["Football", "Basketball", "Tennis", "Cybersport"]

    threads = []

    # Создаем и запускаем потоки для каждого спорта
    for sport in sports:
        marathon_thread = threading.Thread(target=marathon_update_games, args=(sport,))
        xstavka_thread = threading.Thread(target=xstavka_update_games, args=(sport,))

        marathon_thread.start()
        xstavka_thread.start()

        threads.append(marathon_thread)
        threads.append(xstavka_thread)

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()


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
                    print("[INFO] Records deleted from 'odds' table, except for specified records.")

            with connection.cursor() as cursor:
                # Удаление записей из таблицы games, исключая записи из переменной records
                if values:
                    query = f"DELETE FROM games WHERE (game_id, league_id) NOT IN ({','.join(values)});"
                    cursor.execute(query)
                    print("[INFO] Records deleted from 'games' table, except for specified records.")

    except Exception as ex:
        print("[INFO] Error", ex)
    finally:
        connection.close()

    # time.sleep(30)

    find_bets()


    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Время выполнения программы: {execution_time} секунд")

    time.sleep(4)
    break
