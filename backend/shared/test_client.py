from backend.shared.balldontlie_client import get_team, get_team_games, get_call_count, reset_call_count
from backend.shared.manual_roster_data import HEAT_ROSTER_2025_26, get_player_by_name

HEAT_TEAM_ID = 16  # Miami Heat

reset_call_count()

team = get_team(HEAT_TEAM_ID)
print("Team:", team["full_name"])

print(f"\nRoster ({len(HEAT_ROSTER_2025_26)} players):")
for p in HEAT_ROSTER_2025_26[:5]:
    print(f"  {p['first_name']} {p['last_name']} - {p['position']}")

games = get_team_games(HEAT_TEAM_ID, season=2024, limit=5)
print(f"\nRecent games ({len(games)}):")
for g in games:
    print(f"  {g['date']} - {g['home_team']['abbreviation']} vs {g['visitor_team']['abbreviation']}")

lookup = get_player_by_name("Bam Adebayo")
print(f"\nLookup test: {lookup}")

print(f"\nTotal live API calls made: {get_call_count()}")