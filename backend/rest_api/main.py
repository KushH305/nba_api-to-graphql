import time
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from backend.shared.manual_roster_data import get_player_by_name, get_player_by_id, get_team_roster
from backend.shared.balldontlie_client import get_team, get_team_games, get_team_games_batch

DEMO_TEAM_IDS = [16, 2, 14, 20, 6]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Warming cache for demo teams...")
    try:
        get_team(DEMO_TEAM_IDS[0])  # one call fetches ALL teams, covers every id
        get_team_games_batch(DEMO_TEAM_IDS, season=2024, limit_per_team=5)  # seeds both batch + individual caches
        print("Cache warm-up complete.")
    except Exception as exc:
        # Don't let a warm-up failure prevent the server from starting —
        # real requests will just populate the cache on-demand instead.
        print(f"Cache warm-up failed (non-fatal): {exc}")
    yield


app = FastAPI(title="NBA REST API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_metrics_logging(request: Request, call_next):
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        error_body = json.dumps({"error": str(exc)}).encode()

        log_entry = {
            "timestamp": time.time(),
            "path": request.url.path,
            "method": request.method,
            "duration_ms": round(duration_ms, 2),
            "payload_bytes": len(error_body),
            "error": True,
        }
        with open("benchmark_log.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return Response(content=error_body, status_code=500, media_type="application/json")

    duration_ms = (time.perf_counter() - start) * 1000
    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    log_entry = {
        "timestamp": time.time(),
        "path": request.url.path,
        "method": request.method,
        "duration_ms": round(duration_ms, 2),
        "payload_bytes": len(body),
    }
    with open("benchmark_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.get("/")
def root():
    return {"message": "REST API is running."}


@app.get("/players/{name}")
def player_by_name(name: str):
    data = get_player_by_name(name)
    if not data:
        raise HTTPException(status_code=404, detail="Player not found")
    return data


@app.get("/players/id/{player_id}")
def player_by_id(player_id: int):
    data = get_player_by_id(player_id)
    if not data:
        raise HTTPException(status_code=404, detail="Player not found")
    return data


@app.get("/teams/{team_id}")
def team(team_id: int):
    data = get_team(team_id)
    if not data:
        raise HTTPException(status_code=404, detail="Team not found")
    return data


@app.get("/teams/{team_id}/roster")
def team_roster(team_id: int):
    return get_team_roster(team_id)


@app.get("/teams/{team_id}/games")
def team_games(team_id: int, limit: int = 5):
    return get_team_games(team_id, season=2024, limit=limit)