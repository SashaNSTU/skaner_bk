
import random
import requests
from bs4 import BeautifulSoup
import re
import json


def get_game_name(result):
    team1 = result["events"][0]["team1"]
    team2 = result["events"][0]["team2"]
    print(team1 + " - " + team2)

def get_game_kf_win(result):
    team1 = result["customFactors"][0]["factors"][2]["v"]
    team2 = result["customFactors"][0]["factors"][3]["v"]
    print("П1 "+str(team1) + " - " + str(team2)+" П2")

def get_game_id(result):
    soup = BeautifulSoup(result, 'html.parser')
    game_ids = []
    for div in soup.find_all('div', class_='sport-event--3gqipH _inline--3G9Wgh'):
        a_tag = div.find('a')
        href_value = a_tag['href']
        last_element = href_value.split('/')[-2]
        game_ids.append(last_element)
    for eventId in game_ids:
        params = {
            'lang': 'ru',
            'eventId': eventId,
            'scopeMarket': '1600',
            'version': '0',
        }
        response = requests.get('https://line55w.bk6bba-resources.com/events/event', params=params)
        result = response.json()
        get_game_name(result)
        get_game_kf_win(result)

def get_html_ligi(id_lig):

    # Парсинг HTML страницы https://www.fon.bet/sports/basketball/64388/
    # result = '<div class="sport-section-virtual-list--6lYPYe"><div class="sport-section--7jNGXZ _compact--7KyLWd" style="background: rgb(200, 89, 35); border-color: rgb(200, 89, 35);"><div class="table-component-favorite--6fb9HE _light--5qpp6N"></div><div class="table-component-icon--2C8jGg" style="background-image: url(&quot;//origin.bk6bba-resources.com/ContentCommon/Logotypes/SportKinds/new-design/white_new/3-basketball.svg&quot;);"></div><div class="table-component-text--5BmeJU sport-section__caption--7bUR8M">Баскетбол</div><div class="table-component-market-combo--7HIt0I _clickable--1jPpDa sport-section__market--1b352g" style="width: 128px;"><div class="row--52MpZw _clickable--1jPpDa"><span class="caption--4XueAn">Исходы</span><span class="expander--3vdUC6"></span></div></div><div class="table-component-market-combo--7HIt0I _clickable--1jPpDa sport-section__market--1b352g" style="width: 128px;"><div class="row--52MpZw _clickable--1jPpDa"><span class="caption--4XueAn">Двойной исход</span><span class="expander--3vdUC6"></span></div></div><div class="table-component-market-combo--7HIt0I _clickable--1jPpDa sport-section__market--1b352g" style="width: 164px;"><div class="row--52MpZw _clickable--1jPpDa"><span class="caption--4XueAn">Форы</span><span class="expander--3vdUC6"></span></div></div><div class="table-component-market-combo--7HIt0I _clickable--1jPpDa sport-section__market--1b352g" style="width: 133px;"><div class="row--52MpZw _clickable--1jPpDa"><span class="caption--4XueAn">Тоталы</span><span class="expander--3vdUC6"></span></div></div><div></div></div><div class="sport-competition--PvDzHX _compact--6zvh5M" style="background: rgba(200, 89, 35, 0.1);"><div class="table-component-favorite--6fb9HE"></div><div class="table-component-icon--2C8jGg sport-competition__icon--3RoN01" style="background-image: url(&quot;//origin.bk6bba-resources.com/ContentCommon/Logotypes/CompetitionLogos/Basketball/nba_15.svg&quot;);"></div><div class="table-component-text--5BmeJU">NBA. Плей-офф. 1/8 финала. До 4-х побед</div><div class="table-component-text--5BmeJU" style="width: 40px;">1</div><div class="table-component-text--5BmeJU" style="width: 40px;">X</div><div class="table-component-text--5BmeJU" style="width: 40px;">2</div><div class="table-component-text--5BmeJU" style="width: 40px;">1X</div><div class="table-component-text--5BmeJU" style="width: 40px;">12</div><div class="table-component-text--5BmeJU" style="width: 40px;">X2</div><div class="table-component-text--5BmeJU" style="width: 87px;">Фора 1</div><div class="table-component-text--5BmeJU" style="width: 73px;">Фора 2</div><div class="table-component-text--5BmeJU" style="width: 45px;">Тотал</div><div class="table-component-text--5BmeJU" style="width: 40px;">Б</div><div class="table-component-text--5BmeJU" style="width: 40px;">М</div><div></div></div><div class="sport-base-event--pDx9cf _compact--5fB1ok"><div class="table-component-favorite--6fb9HE"></div><div></div><div class="sport-base-event__main--1RA3w5"><div class="sport-base-event__main__caption--11Epy3 _clickable--3VqjxU _inline--4pgDR3"><div class="sport-event--3gqipH _inline--3G9Wgh"><a href="/sports/basketball/64388/40188081/" class="table-component-text--5BmeJU sport-event__name--HefZLq _clickable--G5cwQm _event-view--7J8rEd _compact--7BwYe1">Кливленд Кавальерс — Нью-Йорк Никс</a><span class="event-block-icon-info--6iYMHk"></span></div></div><div class="sport-base-event__main__right--339nJX"><div class="event-block-planned-time--5OxWPy"><span class="event-block-planned-time__time--16Vaws _small--7aWIIP">Завтра в 06:00</span></div><span class="event-block-statistics--4LsCbv _clickable--2Z7MC7"></span></div></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.44</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">2.80</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">-5.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><span class="table-component-factor-value_complex__up-down--3Fn3At _compact--7j5yEe"></span><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">+5.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><div class="table-component-factor-value_param--5xDx2Q _compact--7j5yEe _len-mid--3FZ31B" style="width: 45px;"><span class="table-component-factor-value_param__text--4JCh5D">202.5</span><span class="table-component-factor-value_param__up-down--4CtuwZ"></span></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.90</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.90</div><div class="table-component-text--5BmeJU sport-base-event__other-factors--2AtGXX _clickable--3VqjxU">+253</div></div><div class="sport-event-separator--4McTfM _sub-event--5QuDlF"><div></div></div><div class="sport-base-event--pDx9cf _compact--5fB1ok"><div class="table-component-favorite--6fb9HE"></div><div></div><div class="sport-base-event__main--1RA3w5"><div class="sport-base-event__main__caption--11Epy3 _clickable--3VqjxU _inline--4pgDR3"><div class="sport-event--3gqipH _inline--3G9Wgh"><a href="/sports/basketball/64388/40203703/" class="table-component-text--5BmeJU sport-event__name--HefZLq _clickable--G5cwQm _event-view--7J8rEd _compact--7BwYe1">Мемфис Гриззлис — Лос-Анджелес Лейкерс</a><span class="event-block-icon-info--6iYMHk"></span></div></div><div class="sport-base-event__main__right--339nJX"><div class="event-block-planned-time--5OxWPy"><span class="event-block-planned-time__time--16Vaws _small--7aWIIP">Завтра в 06:30</span></div><span class="event-block-statistics--4LsCbv _clickable--2Z7MC7"></span></div></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.53</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">2.50</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">-4.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><span class="table-component-factor-value_complex__up-down--3Fn3At _compact--7j5yEe"></span><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">+4.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><div class="table-component-factor-value_param--5xDx2Q _compact--7j5yEe _len-mid--3FZ31B" style="width: 45px;"><span class="table-component-factor-value_param__text--4JCh5D">221.5</span><span class="table-component-factor-value_param__up-down--4CtuwZ"></span></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.85</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.95</div><div class="table-component-text--5BmeJU sport-base-event__other-factors--2AtGXX _clickable--3VqjxU">+249</div></div><div class="sport-event-separator--4McTfM _sub-event--5QuDlF"><div></div></div><div class="sport-base-event--pDx9cf _compact--5fB1ok"><div class="table-component-favorite--6fb9HE"></div><div></div><div class="sport-base-event__main--1RA3w5"><div class="sport-base-event__main__caption--11Epy3 _clickable--3VqjxU _inline--4pgDR3"><div class="sport-event--3gqipH _inline--3G9Wgh"><a href="/sports/basketball/64388/40203714/" class="table-component-text--5BmeJU sport-event__name--HefZLq _clickable--G5cwQm _event-view--7J8rEd _compact--7BwYe1">Милуоки Бакс — Майами Хит</a><span class="event-block-icon-info--6iYMHk"></span></div></div><div class="sport-base-event__main__right--339nJX"><div class="event-block-planned-time--5OxWPy"><span class="event-block-planned-time__time--16Vaws _small--7aWIIP">Завтра в 08:30</span></div><span class="event-block-statistics--4LsCbv _clickable--2Z7MC7"></span></div></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.14</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">5.75</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">-11.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><span class="table-component-factor-value_complex__up-down--3Fn3At _compact--7j5yEe"></span><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">+11.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><div class="table-component-factor-value_param--5xDx2Q _compact--7j5yEe _len-mid--3FZ31B" style="width: 45px;"><span class="table-component-factor-value_param__text--4JCh5D">219.5</span><span class="table-component-factor-value_param__up-down--4CtuwZ"></span></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.90</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.90</div><div class="table-component-text--5BmeJU sport-base-event__other-factors--2AtGXX _clickable--3VqjxU">+245</div></div><div class="sport-event-separator--4McTfM _sub-event--5QuDlF"><div></div></div><div class="sport-base-event--pDx9cf _compact--5fB1ok _last--pyxoxA"><div class="table-component-favorite--6fb9HE"></div><div></div><div class="sport-base-event__main--1RA3w5"><div class="sport-base-event__main__caption--11Epy3 _clickable--3VqjxU _inline--4pgDR3"><div class="sport-event--3gqipH _inline--3G9Wgh"><a href="/sports/basketball/64388/40188092/" class="table-component-text--5BmeJU sport-event__name--HefZLq _clickable--G5cwQm _event-view--7J8rEd _compact--7BwYe1">Сакраменто Кингз — Голден Стэйт Уорриорз</a><span class="event-block-icon-info--6iYMHk"></span></div></div><div class="sport-base-event__main__right--339nJX"><div class="event-block-planned-time--5OxWPy"><span class="event-block-planned-time__time--16Vaws _small--7aWIIP">Завтра в 09:00</span></div><span class="event-block-statistics--4LsCbv _clickable--2Z7MC7"></span></div></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">2.00</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.80</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-empty--19sHrm value-state-empty--5jICeJ" style="width: 40px;">-</div><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">+1.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><span class="table-component-factor-value_complex__up-down--3Fn3At _compact--7j5yEe"></span><div class="table-component-factor-value_complex--25G2ok _compact--7j5yEe cell-state-normal--iYJc0x" style="width: 73px;"><span class="table-component-factor-value_complex__text--1T1vuN text-state-normal--1L40o3">-1.5</span><span class="table-component-factor-value_complex__text--1T1vuN value-state-normal--4JL4xN">1.90</span></div><div class="table-component-factor-value_param--5xDx2Q _compact--7j5yEe _len-mid--3FZ31B" style="width: 45px;"><span class="table-component-factor-value_param__text--4JCh5D">233.5</span><span class="table-component-factor-value_param__up-down--4CtuwZ"></span></div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.85</div><div class="table-component-factor-value_single--6nfox5 _compact--7j5yEe cell-state-normal--iYJc0x value-state-normal--4JL4xN" style="width: 40px;">1.95</div><div class="table-component-text--5BmeJU sport-base-event__other-factors--2AtGXX _clickable--3VqjxU">+248</div></div></div>'
    # get_game_id(result)
    url = "https://www.fon.bet/sports/basketball/" + str(id_lig[0])
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.37",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"
    ]

    # Выбор случайного User-Agent из списка
    user_agent = random.choice(user_agents)
    headers = {
        "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / avif, image / webp, image / apng, * / *;q = 0.8, application / signed - exchange;v = b3;q = 0.7",
        "Accept - Encoding": "gzip, deflate, br",
        "Accept - Language": "ru - RU, ru;q = 0.9, en - US;q = 0.8, en;q = 0.7",
        "Cache - Control": "max - age = 0",
        "Connection": "keep - alive",
        "User-Agent": user_agent
    }
    response = requests.get(url = url, headers = headers)
    with open("index.html", "w") as file:
        file.write(response.text)

    # user_agents = [
    #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.37",
    #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"
    # ]
    #
    # # Выбор случайного User-Agent из списка
    # user_agent = random.choice(user_agents)
    #
    # # Заголовки запроса с User-Agent
    # headers = {'User-Agent': user_agent}
    #
    # # Загрузка страницы с использованием заголовков
    # response = requests.get(url, headers=headers)
    #
    # # Парсинг страницы
    # soup = BeautifulSoup(response.content, "html.parser")
    # print(soup)
    # div_block = soup.find("div", {"class": "sport-section-virtual-list--6lYPYe"})
    # print(div_block)
    # # Извлечение нужной информации
    # # Например, найдем заголовок страницы
    # get_game_id(div_block)


def main():

    response = requests.get('https://line53w.bk6bba-resources.com/events/list')
    result = response.json()

    try:
        i = [i for i, sport in enumerate(result["sports"]) if sport["name"] == "Баскетбол"][0]
        j = [j for j, sport in enumerate(result["sports"]) if sport["name"] == "Волейбол"][0]
    except IndexError:
        print("Элемент с ключом 'name' равным 'Баскетбол' не найден.")

    id_lig = [result["sports"][i]['id'] for i in range(i+1, j)]
    print(id_lig)
    print(len(id_lig))
    get_html_ligi(id_lig)


if __name__ == '__main__':
    main()
