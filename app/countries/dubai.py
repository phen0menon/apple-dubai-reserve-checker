import datetime
import json
import re
from typing import Any
from typing import Dict
from typing import List
from typing import TypedDict

import requests
from bs4 import BeautifulSoup

from app.config import Config
from app.telegram import send_telegram_message

stores_url = "https://reserve-prime.apple.com/AE/en_AE/reserve/A/stores.json"
availability_url = "https://reserve-prime.apple.com/AE/en_AE/reserve/A/availability.json"
fast_link = "https://reserve-prime.apple.com/AE/en_AE/reserve/A/availability"


class GetStoresResponseStore(TypedDict):
    storeNumber: str
    enabled: bool
    latitude: str
    longitude: str
    storeName: str


class GetStoresResponse(TypedDict):
    config: Any
    stores: List[GetStoresResponseStore]


StoresById = dict[str, GetStoresResponseStore]


class GetAvailabilityResponseAvailability(TypedDict):
    contract: bool
    unlocked: bool


class GetAvailabilityResponseStore(TypedDict):
    availability: GetAvailabilityResponseAvailability


class GetAvailabilityResponse(TypedDict):
    stores: Dict[str, Dict[str, GetAvailabilityResponseStore]]


class Product(TypedDict):
    partNumber: str
    description: str
    color: str
    capacity: str
    subfamily: str
    price: str


def get_stores() -> StoresById:
    data: GetStoresResponse = requests.get(stores_url).json()
    stores_by_id: StoresById = {store["storeNumber"]: store for store in data["stores"]}
    return stores_by_id


def get_availability() -> GetAvailabilityResponse:
    data: GetAvailabilityResponse = requests.get(availability_url).json()
    return data


def get_models_from_apple_website() -> Dict[str, Product]:
    response = requests.get(fast_link)
    if response.status_code != 200:
        raise Exception(f"Failed to get models from Apple website: {response.text}")

    soup = BeautifulSoup(response.text, "html.parser")
    json_data = {}
    for script in soup.find_all("script"):
        if "data.products =" in script.text:
            json_data_match = re.search(r"data\.products\s*=\s*({.*?});", script.text, re.DOTALL)
            if json_data_match:
                json_str = json_data_match.group(1)
                # For some reason, Apple uses single quotes in their JSON and some invalid colon separators
                json_str = json_str.replace("'", '"')
                json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
                json_data = json.loads(json_str)
            else:
                raise Exception("Could not find JSON data in the script")
            break
    return json_data


def get_models():
    try:
        models = get_models_from_apple_website()
    except Exception as e:
        print(f"Failed to get models from Apple website: {e}, contunuing with cached data")
        models = json.loads(open("data.json").read())
    products_by_id: Dict[str, Product] = {product["partNumber"]: product for product in models["products"]}
    return products_by_id


emojis_by_color = {
    "black": "⚫️",
    "white": "⚪️",
    "natural": "🔶",
    "desert": "🟤",
}


def extract_model_color(model_name: str) -> str:
    for color in emojis_by_color.keys():
        if color in model_name.lower():
            return color
    return ""


def run_checker(cfg: Config) -> None:
    stores_by_id = get_stores()
    available_models = get_availability()
    products_by_id = get_models()

    for store in available_models["stores"].keys():
        msg = ""
        if cfg["specific_stores"] and store not in cfg["specific_stores"]:
            continue
        for model in available_models["stores"][store].keys():
            if available_models["stores"][store][model]["availability"]["unlocked"]:
                product = products_by_id[model]
                if not msg:
                    msg += f"🚒🚒🚒 Store: {stores_by_id[store]['storeName']}\n\n"
                else:
                    msg += "\n"
                emoji = emojis_by_color.get(extract_model_color(product["color"]), "")
                if emoji:
                    emoji += " "
                msg += f"{emoji}Model: {product['description']}"
        if msg:
            msg += f"\n\n{fast_link}"
            send_telegram_message(
                chat_id=cfg["telegram_chat_id"],
                bot_id=cfg["telegram_bot_id"],
                message=msg,
            )
        else:
            print(f"{store} {stores_by_id[store].get('storeName')}: ... no models available :(")


def run_dubai(cfg: Config):
    print("Date: ", datetime.datetime.now())
    if cfg["log_path"]:
        with open(f"{cfg['log_path']}/apple-checker-log.log", "a") as f:
            f.write(f"Date: {datetime.datetime.now()}\n")
    run_checker(cfg)
