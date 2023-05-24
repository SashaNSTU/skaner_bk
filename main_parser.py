from xstavka_get_games import xstavka_update_games
from xstavka_get_live_games import xstavka_update_live_games
from marathon_get_live_games import marathon_update_live_games
from marathon_get_games import marathon_update_games
from functions import update_db, delete_not_repetitive
import threading
import time


while True:
    try:
        update_db()

        start_time = time.time()
        sports = ["Football", "Basketball", "Tennis", "Cybersport"]

        threads = []

        for sport in sports:
            marathon_thread = threading.Thread(target=marathon_update_live_games, args=(sport,))
            xstavka_thread = threading.Thread(target=xstavka_update_live_games, args=(sport,))

            marathon_thread.start()
            xstavka_thread.start()

            threads.append(marathon_thread)
            threads.append(xstavka_thread)

        for thread in threads:
            thread.join()



        delete_not_repetitive()

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Время выполнения программы: {execution_time} секунд")


    except Exception as ex:
        print("[INFO] Error:", ex)
    finally:
        pass

