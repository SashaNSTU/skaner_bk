from xstavka_get_games import xstavka_update_games
from marathon_get_games import marathon_update_games
from functions import find_bets, update_db, delete_not_repetitive
import threading
import time


while True:
    update_db()

    start_time = time.time()

    sports = ["Football", "Basketball", "Tennis", "Cybersport"]

    threads = []

    for sport in sports:
        marathon_thread = threading.Thread(target=marathon_update_games, args=(sport,))
        xstavka_thread = threading.Thread(target=xstavka_update_games, args=(sport,))

        marathon_thread.start()
        xstavka_thread.start()

        threads.append(marathon_thread)
        threads.append(xstavka_thread)

    for thread in threads:
        thread.join()

    delete_not_repetitive()

    find_bets()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения программы: {execution_time} секунд")

    time.sleep(4)
    break
