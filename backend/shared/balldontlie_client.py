import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BALLDONTLIE_API_KEY")
BASE_URL = "https://api.balldontlie.io"
HEADERS = {"Authorization": API_KEY}

# --- Simple in-memory TTL cache. Games are historical (completed seasons),
# so a long TTL is safe and correct, not just a rate-limit workaround. ---
_cache = {}
CACHE_TTL_SECONDS = 3600

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


# --- Retry wrapper, handles BallDontLie's 5 req/min rate limit ---
def _request_with_retry(url, params=None, max_retries=3, backoff_seconds=15, timeout=15):
    for attempt in range(max_retries):
        response = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        if response.status_code == 429:
            print(f"Rate limited, waiting {backoff_seconds}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(backoff_seconds)
            continue
        response.raise_for_status()
        return response
    raise Exception("Max retries exceeded due to rate limiting")


# --- Teams: static-ish data, fetch the full list once, filter locally ---
_all_teams_cache = {"data": None, "timestamp": 0}
ALL_TEAMS_CACHE_TTL_SECONDS = 3600

def _get_all_teams():
    now = time.time()
    if _all_teams_cache["data"] and (now - _all_teams_cache["timestamp"] < ALL_TEAMS_CACHE_TTL_SECONDS):
        return _all_teams_cache["data"]

    _call_count["count"] += 1
    response = _request_with_retry(f"{BASE_URL}/v1/teams", params={"per_page": 30})
    data = response.json()["data"]
    _all_teams_cache["data"] = data
    _all_teams_cache["timestamp"] = now
    return data


def get_team(team_id: int):
    all_teams = _get_all_teams()
    return next((t for t in all_teams if t["id"] == team_id), None)


def get_team_games(team_id: int, season: int = 2024, limit: int = 5):
    """
    Individual per-team games lookup. Checks cache first — if the batch
    function already populated this exact key, this never makes a live call.
    """
    cache_key = f"games:{team_id}:{season}:{limit}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    _call_count["count"] += 1
    response = _request_with_retry(
        f"{BASE_URL}/v1/games",
        params={"team_ids[]": team_id, "seasons[]": season, "per_page": limit},
    )
    data = response.json()["data"]
    _set_cache(cache_key, data)
    return data


def get_team_games_batch(team_ids: list, season: int = 2024, limit_per_team: int = 5):
    """
    Fetches games for multiple teams in ONE live HTTP call, then populates
    BOTH the batch cache key AND each team's individual cache key from that
    single response. This means warming this once also warms get_team_games()
    for each team — no duplicate live calls for the same underlying data.
    """
    batch_cache_key = f"games_batch:{'-'.join(map(str, sorted(team_ids)))}:{season}"
    cached = _get_cached(batch_cache_key)
    if cached is not None:
        return cached

    _call_count["count"] += 1
    response = _request_with_retry(
        f"{BASE_URL}/v1/games",
        params={"team_ids[]": team_ids, "seasons[]": season, "per_page": limit_per_team * len(team_ids)},
    )
    all_games = response.json()["data"]
    _set_cache(batch_cache_key, all_games)

    # Slice results per team and seed the individual cache too
    for team_id in team_ids:
        team_games = [
            g for g in all_games
            if g["home_team"]["id"] == team_id or g["visitor_team"]["id"] == team_id
        ][:limit_per_team]
        individual_key = f"games:{team_id}:{season}:{limit_per_team}"
        _set_cache(individual_key, team_games)

    return all_games