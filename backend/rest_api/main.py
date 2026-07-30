from fastapi import FastAPI, HTTPException
from backend.shared.manual_roster_data import get_player_by_name, get_player_by_id, get_team_roster
from backend.shared.balldontlie_client import get_team, get_team_games

app = FastAPI(title="NBA REST API")


@app.get("/")
def root():
    return {"message": "REST API is running."}


@app.get("/players/{name}")
def player_by_name(name: str):
    data = get_player_by_name(name)
    if not data:
        raise HTTPException(status_code=404, detail="Player not found")
    return data  # full object, every field — typical REST "everything" response


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
    return get_team_roster(team_id)  # separate call, separate round trip


@app.get("/teams/{team_id}/games")
def team_games(team_id: int, limit: int = 5):
    return get_team_games(team_id, season=2024, limit=limit)  # separate call, separate round trip