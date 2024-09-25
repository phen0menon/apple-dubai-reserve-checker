import requests


def send_telegram_message(*, chat_id: str, bot_id: str, message: str) -> requests.Response:
    res = requests.get(f"https://api.telegram.org/bot{bot_id}/sendMessage?chat_id={chat_id}&text={message}")
    if res.status_code != 200:
        raise Exception(f"Failed to send telegram message: {res.text}")
    print("✔️\tMessage sent successfully")
