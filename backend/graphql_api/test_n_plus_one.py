import asyncio
from backend.graphql_api.schema import schema
from backend.graphql_api.loaders import get_games_loader
from backend.shared.balldontlie_client import get_call_count, reset_call_count

QUERY = """
{
  teams(ids: [16, 2, 14, 20, 6]) {
    fullName
    recentGames(limit: 5) {
      date
      homeScore
      visitorScore
    }
  }
}
"""

async def main():
    reset_call_count()
    #result = await schema.execute(QUERY)
    result = await schema.execute(QUERY, context_value={"games_loader": get_games_loader()})
    if result.errors:
        print("Errors:", result.errors)
    else:
        for team in result.data["teams"]:
            print(team["fullName"], "-", len(team["recentGames"]), "games")
    print(f"\nTotal live API calls made: {get_call_count()}")

asyncio.run(main())