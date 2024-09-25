import datetime
from typing import List
from typing import TypedDict

import requests

from app.config import Config
from app.telegram import send_telegram_message


class Store(TypedDict):
    storeNumber: str
    latitude: str
    longitude: str
    storeName: str
    partsAvailability: dict


# To search for another model, go to https://www.apple.com/de/shop/buy-iphone/iphone-16-pro
# Inspect the page code, search for window.PRODUCT_SELECTION_BOOTSTRAP and find specific model part number
availability_url = "https://www.apple.com/de/shop/fulfillment-messages?pl=true&mts.0=regular&mts.1=compact&cppart=UNLOCKED/WW&parts.0={part}&location={postal}"

buy_link = "https://www.apple.com/de/shop/buy-iphone/iphone-16-pro"


def run_checker(cfg: Config) -> None:
    availability_url_formatted = availability_url.format(part=cfg["specific_model"], postal=cfg["postal_code"])

    res = requests.get(availability_url_formatted).json()
    stores: List[Store] = []
    try:
        stores = res["body"]["content"]["pickupMessage"]["stores"]
    except KeyError as e:
        raise Exception("Invalid JSON response, missing key: ", str(e))

    result_msg = ""
    empty_msg = ""
    for store in stores:
        store_msg = ""
        if cfg["de_specific_stores"] and store["storeNumber"] not in cfg["de_specific_stores"]:
            continue
        if store["partsAvailability"][cfg["specific_model"]]["pickupDisplay"] == "available":
            store_msg += f"🚒🚒🚒 Store: {store['storeName']}\n"
            model_name = store["partsAvailability"][cfg["specific_model"]]["messageTypes"]["compact"][
                "storePickupProductTitle"
            ]
            store_msg += f"Model: {model_name}"
        if not store_msg:
            empty_msg += f"{store['storeNumber']} {store['storeName']}: ... no models available :(\n"
        else:
            if result_msg:
                result_msg += "\n\n"
            result_msg += store_msg

    if not result_msg:
        print(empty_msg)
    else:
        result_msg += "\n\nBuy link: " + buy_link
        send_telegram_message(chat_id=cfg["telegram_chat_id"], bot_id=cfg["telegram_bot_id"], message=result_msg)


def run_deutschland(cfg: Config):
    print("Date: ", datetime.datetime.now())
    if cfg["log_path"]:
        with open(f"{cfg['log_path']}/apple-checker-log-de.log", "a") as f:
            f.write(f"Date: {datetime.datetime.now()}\n")
    run_checker(cfg)
