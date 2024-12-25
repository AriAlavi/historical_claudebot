import json


def _load_private_data() -> dict:
    PRIVATE_DATA_FILE = "private_data.json"
    with open(PRIVATE_DATA_FILE, "r") as f:
        return json.load(f)


def anthropic_api_key() -> str:
    return _load_private_data()["anthropic_api_key"]


def discord_token(personality: str) -> str:
    personality_name = personality.replace(" ", "_").lower()

    return _load_private_data()[f"discord_token_{personality_name}"]
