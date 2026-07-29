import strawberry
from typing import List, Optional
from backend.shared.manual_roster_data import get_player_by_name, get_player_by_id, HEAT_ROSTER_2025_26
from backend.shared.balldontlie_client import get_team, get_team_games

HEAT_TEAM_ID = 16  # Miami Heat

@strawberry.type
class Player:
    id: int
    first_name: str
    last_name: str
    position: str
    height: str
    weight: str
    jersey_number: str
    college: str
    country: str

@strawberry.type
class Game:
    date: str
    home_team_abbr: str
    visitor_team_abbr: str
    home_score: int
    visitor_score: int
    status: str

@strawberry.type
class Team:
    id: int
    full_name: str
    conference: str
    division: str

    @strawberry.field
    def roster(self) -> list[Player]:
        return [_to_player_type(p) for p in HEAT_ROSTER_2025_26]

    @strawberry.field
    async def recent_games(self, info: strawberry.Info, limit: int = 5) -> list[Game]:
        games_loader = info.context["games_loader"]
        team_games_list = await games_loader.load(self.id)
        return [_to_game_type(g) for g in team_games_list]


def _to_player_type(data: dict) -> Player:
    return Player(
        id=data["id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        position=data["position"],
        height=data["height"],
        weight=data["weight"],
        jersey_number=data["jersey_number"],
        college=data["college"],
        country=data["country"],
    )

def _to_game_type(data: dict) -> Game:
    return Game(
        date=data["date"],
        home_team_abbr=data["home_team"]["abbreviation"],
        visitor_team_abbr=data["visitor_team"]["abbreviation"],
        home_score=data["home_team_score"],
        visitor_score=data["visitor_team_score"],
        status=data["status"],
    )


def _to_team_type(data: dict) -> Team:
    return Team(
        id=data["id"],
        full_name=data["full_name"],
        conference=data["conference"],
        division=data["division"],
    )

@strawberry.type
class Query:
    @strawberry.field
    def player(self, name: str) -> Optional[Player]:
        data = get_player_by_name(name)
        if not data:
            return None
        return _to_player_type(data) if data else None

    @strawberry.field
    def player_by_id(self, id: int) -> Optional[Player]:
        data = get_player_by_id(id)
        if not data:
            return None
        return _to_player_type(data) if data else None

    @strawberry.field
    def team(self, id: int) -> Optional[Team]:
        data = get_team(id)
        if not data:
            return None
        return _to_team_type(data) if data else None

    @strawberry.field
    def teams(self, ids: List[int]) -> list[Team]:
        teams = []
        for team_id in ids:
            data = get_team(team_id)
            if data:
                teams.append(_to_team_type(data))
        return teams


schema = strawberry.Schema(query=Query)