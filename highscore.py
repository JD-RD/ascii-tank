"""High score persistence using JSON."""

import json
import os

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")
MAX_LEADERBOARD = 10


def _load_data():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"entries": []}


def _save_data(data):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_highscore():
    data = _load_data()
    entries = data.get("entries", [])
    return entries[0]["score"] if entries else 0


def save_highscore(name, score):
    data = _load_data()
    entries = data.get("entries", [])
    entries.append({"name": name.upper(), "score": score})
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:MAX_LEADERBOARD]
    data["entries"] = entries
    _save_data(data)
    return any(e["name"] == name.upper() and e["score"] == score for e in entries[:1])


def get_leaderboard():
    data = _load_data()
    return data.get("entries", [])
