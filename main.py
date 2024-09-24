import json
import os
import re
from typing import Any
from typing import Dict
from typing import List
from typing import TypedDict

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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


class Config(TypedDict):
    telegram_chat_id: str
    telegram_bot_id: str


class Product(TypedDict):
    partNumber: str
    description: str
    color: str
    capacity: str
    subfamily: str
    price: str


def get_env_or_raise(env_name: str) -> str:
    value = os.getenv(env_name)
    if not value:
        raise Exception(f"Environment variable {env_name} is not set")
    return value


def init_cfg() -> Config:
    load_dotenv()

    return Config(
        telegram_chat_id=get_env_or_raise("TELEGRAM_CHAT_ID"),
        telegram_bot_id=get_env_or_raise("TELEGRAM_BOT_ID"),
    )


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


def send_telegram_message(*, chat_id: str, bot_id: str, message: str) -> requests.Response:
    res = requests.get(f"https://api.telegram.org/bot{bot_id}/sendMessage?chat_id={chat_id}&text={message}")
    if res.status_code == 200:
        raise Exception(f"Failed to send telegram message: {res.text}")
    print("✔️\tMessage sent successfully")


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
        for model in available_models["stores"][store].keys():
            if available_models["stores"][store][model]["availability"]["unlocked"]:
                product = products_by_id[model]
                if not msg:
                    msg += f"🚒🚒🚒 Store: {stores_by_id[store]['storeName']}\n\n"
                else:
                    msg += "\n\n"
                emoji = emojis_by_color.get(extract_model_color(product["color"]), "")
                if emoji:
                    emoji += " "
                msg += f"{emoji}Model: {product['description']}\nPrice: {product['price']}"
        if msg:
            msg += f"\n\n{fast_link}"
            send_telegram_message(
                chat_id=cfg["telegram_chat_id"],
                bot_id=cfg["telegram_bot_id"],
                message=msg,
            )
        else:
            print(f"{store}: ... no models available :(")


if __name__ == "__main__":
    cfg = init_cfg()

    run_checker(cfg)
