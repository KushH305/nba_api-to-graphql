import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BALLDONTLIE_API_KEY")
BASE_URL = "https://api.balldontlie.io"
HEADERS = {"Authorization": API_KEY}

# --- Simple in-memory TTL cache, protects the free tier's 5 req/min limit ---
_cache = {}
CACHE_TTL_SECONDS = 60

def _get_cached(key):
    entry = _cache.get(key)
    if entry and (time.time() - entry["timestamp"] < CACHE_TTL_SECONDS):
        return entry["data"]
    return None

def _set_cache(key, data):
    _cache[key] = {"data": data, "timestamp": time.time()}

# --- Call counter, used to prove the N+1 problem in Ticket 5 ---
_call_count = {"count": 0}

def get_call_count():
    return _call_count["count"]

def reset_call_count():
    _call_count["count"] = 0

# --- Public functions ---
def get_team(team_id: int):
    cache_key = f"team:{team_id}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    _call_count["count"] += 1
    response = requests.get(f"{BASE_URL}/v1/teams/{team_id}", headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()["data"]
    _set_cache(cache_key, data)
    return data

def get_team_games(team_id: int, season: int = 2024, limit: int = 10):
    cache_key = f"games:{team_id}:{season}:{limit}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    _call_count["count"] += 1
    response = requests.get(
        f"{BASE_URL}/v1/games",
        headers=HEADERS,
        params={"team_ids[]": team_id, "seasons[]": season, "per_page": limit},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()["data"]
    _set_cache(cache_key, data)
    return data

def get_team_games_batch(team_ids: list, season: int = 2024, limit_per_team: int = 5):
    """
    Batched version — fetches games for multiple teams in ONE HTTP call
    instead of one call per team. This is the fix we'll wire in for Ticket 5.
    """
    cache_key = f"games_batch:{'-'.join(map(str, sorted(team_ids)))}:{season}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    _call_count["count"] += 1
    response = requests.get(
        f"{BASE_URL}/v1/games",
        headers=HEADERS,
        params={"team_ids[]": team_ids, "seasons[]": season, "per_page": limit_per_team * len(team_ids)},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()["data"]
    _set_cache(cache_key, data)
    return data