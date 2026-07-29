import asyncio
from strawberry.dataloader import DataLoader
from backend.shared.balldontlie_client import get_team_games_batch


async def batch_load_games(team_ids: list[int]) -> list[list[dict]]:
    """
    Strawberry's DataLoader collects all the individual `.load(team_id)`
    calls made during a single request into one batch, then calls this
    function ONCE with all the keys together — instead of once per key.

    Note: since all keys in a batch share one query, we apply a single
    fixed limit per team (5) rather than per-call limits — a reasonable
    simplification since our demo always requests the same limit across
    a batch anyway.
    """
    loop = asyncio.get_event_loop()
    all_games = await loop.run_in_executor(
        None, get_team_games_batch, list(team_ids), 2024, 5
    )

    # Group the combined results back out per team_id, in the SAME order as the input keys
    result = []
    for team_id in team_ids:
        team_games = [
            g for g in all_games
            if g["home_team"]["id"] == team_id or g["visitor_team"]["id"] == team_id
        ]
        result.append(team_games[:5])
    return result


def get_games_loader() -> DataLoader:
    return DataLoader(load_fn=batch_load_games)