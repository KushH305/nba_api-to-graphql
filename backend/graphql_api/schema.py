import strawberry
from typing import Optional
from backend.shared.manual_roster_data import get_player_by_name, get_player_by_id

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

@strawberry.type
class Query:
    @strawberry.field
    def player(self, name: str) -> Optional[Player]:
        data = get_player_by_name(name)
        if not data:
            return None
        return _to_player_type(data)

    @strawberry.field
    def player_by_id(self, id: int) -> Optional[Player]:
        data = get_player_by_id(id)
        if not data:
            return None
        return _to_player_type(data)


schema = strawberry.Schema(query=Query)