import requests


def send_telegram(text: str):
    token = '5842114499:AAFWr3inq9764dht5_p41hNbFxeZ7TGmmJY'
    url = "https://api.telegram.org/bot"
    channel_id = '871286871'
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
        "chat_id": channel_id,
        "text": text,
        "parse_mode": "HTML"
    })

    if r.status_code != 200:
        raise Exception("post_text error")


def main():
    send_telegram('Привет, чувак!')


if __name__ == '__main__':
    main()