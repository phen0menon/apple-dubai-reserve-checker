import argparse

from app.config import init_cfg
from app.countries import countries

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Apple-Store-Reservation-Checker", description="")
    parser.add_argument("-chat_id", type=int, help="Telegram chat id")
    parser.add_argument("-country", type=str, help="Country")
    args = parser.parse_args()
    chat_id = args.chat_id
    country = args.country
    cfg = init_cfg()
    if chat_id:
        cfg["telegram_chat_id"] = chat_id
    if country:
        cfg["country"] = country
    country = cfg["country"]
    if country not in countries:
        raise Exception(f"Country {country} is not supported")
    countries[country](cfg)
