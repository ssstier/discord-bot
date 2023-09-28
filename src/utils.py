import json


def read_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"time": 20, "difficulty": 5, "choices": 4}


def write_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)
