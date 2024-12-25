import json


def _load_private_data() -> dict:
    PRIVATE_DATA_FILE = "private_data.json"
    with open(PRIVATE_DATA_FILE, "r") as f:
        return json.load(f)


def anthropic_api_key() -> str:
    return _load_private_data()["anthropic_api_key"]


def discord_token() -> str:
    return _load_private_data()["discord_token"]
