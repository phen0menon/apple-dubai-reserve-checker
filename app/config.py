import os
from typing import Optional
from typing import TypedDict

from dotenv import load_dotenv


class Config(TypedDict):
    country: str
    telegram_chat_id: str
    telegram_bot_id: str
    specific_stores: set[str]
    de_specific_stores: set[str]
    log_path: Optional[str]
    postal_code: Optional[str]
    specific_model: Optional[str]


def get_env_or_raise(env_name: str) -> str:
    value = os.getenv(env_name)
    if not value:
        raise Exception(f"Environment variable {env_name} is not set")
    return value


def init_cfg() -> Config:
    load_dotenv()

    specific_stores = os.getenv("APPLE_SPECIFIC_STORES")
    specific_stores_set = set(specific_stores.split(",") if specific_stores else [])

    de_specific_stores = os.getenv("DE_APPLE_SPECIFIC_STORES")
    de_specific_stores_set = set(de_specific_stores.split(",") if de_specific_stores else [])

    return Config(
        country=get_env_or_raise("COUNTRY"),
        telegram_chat_id=get_env_or_raise("TELEGRAM_CHAT_ID"),
        telegram_bot_id=get_env_or_raise("TELEGRAM_BOT_ID"),
        specific_stores=specific_stores_set,
        de_specific_stores=de_specific_stores_set,
        log_path=os.getenv("LOG_PATH"),
        postal_code=os.getenv("POSTAL_CODE"),
        specific_model=os.getenv("SPECIFIC_MODEL"),
    )
