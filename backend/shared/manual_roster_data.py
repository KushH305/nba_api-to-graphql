"""
Miami Heat 2025-26 roster — manually created.

Why manual: BallDontLie's free-tier Players endpoint has no `seasons`
filter and returns every player ever associated with a franchise,
active or retired. The `Active Players` endpoint that would solve this
is paid-tier only.
"""

HEAT_TEAM_ID = 16


HEAT_ROSTER_2025_26 = [
    # Core Players
    {"id": 1, "first_name": "Bam", "last_name": "Adebayo", "position": "C-F", "height": "6-9", "weight": "255", "jersey_number": "13", "college": "Kentucky", "country": "USA"},
    {"id": 2, "first_name": "Tyler", "last_name": "Herro", "position": "G", "height": "6-5", "weight": "195", "jersey_number": "14", "college": "Kentucky", "country": "USA"},
    {"id": 3, "first_name": "Terry", "last_name": "Rozier", "position": "G", "height": "6-1", "weight": "190", "jersey_number": "2", "college": "Louisville", "country": "USA"},
    {"id": 4, "first_name": "Nikola", "last_name": "Jovic", "position": "F", "height": "6-10", "weight": "240", "jersey_number": "5", "college": "—", "country": "Serbia"},
    {"id": 5, "first_name": "Jaime", "last_name": "Jaquez Jr.", "position": "F-G", "height": "6-6", "weight": "230", "jersey_number": "11", "college": "UCLA", "country": "USA"},
    {"id": 6, "first_name": "Andrew", "last_name": "Wiggins", "position": "F-G", "height": "6-7", "weight": "210", "jersey_number": "22", "college": "Kansas", "country": "Canada"},
    {"id": 7, "first_name": "Norman", "last_name": "Powell", "position": "G", "height": "6-3", "weight": "215", "jersey_number": "24", "college": "UCLA", "country": "USA"},
    {"id": 8, "first_name": "Davion", "last_name": "Mitchell", "position": "G", "height": "6-0", "weight": "210", "jersey_number": "15", "college": "Baylor", "country": "USA"},
    {"id": 9, "first_name": "Kel'el", "last_name": "Ware", "position": "C", "height": "7-0", "weight": "250", "jersey_number": "7", "college": "Indiana", "country": "USA"},

    # Bench / role players
    {"id": 10, "first_name": "Simone", "last_name": "Fontecchio", "position": "F", "height": "6-7", "weight": "220", "jersey_number": "16", "college": "—", "country": "Italy"},
    {"id": 11, "first_name": "Keshad", "last_name": "Johnson", "position": "F", "height": "6-6", "weight": "230", "jersey_number": "16", "college": "Arizona", "country": "USA"},
    {"id": 12, "first_name": "Myron", "last_name": "Gardner", "position": "F", "height": "6-5", "weight": "225", "jersey_number": "15", "college": "Little Rock", "country": "USA"},
    {"id": 13, "first_name": "Pelle", "last_name": "Larsson", "position": "G-F", "height": "6-5", "weight": "215", "jersey_number": "9", "college": "Arizona", "country": "Sweden"},
    {"id": 14, "first_name": "Vladislav", "last_name": "Goldin", "position": "C", "height": "7-0", "weight": "255", "jersey_number": "50", "college": "Michigan", "country": "Russia"},

    # Guards / prospects
    {"id": 15, "first_name": "Kasparas", "last_name": "Jakucionis", "position": "G", "height": "6-5", "weight": "205", "jersey_number": "25", "college": "Illinois", "country": "Lithuania"},
    {"id": 16, "first_name": "Jahmir", "last_name": "Young", "position": "G", "height": "6-0", "weight": "185", "jersey_number": "1", "college": "Maryland", "country": "USA"},
    {"id": 17, "first_name": "Trevor", "last_name": "Keels", "position": "G", "height": "6-4", "weight": "221", "jersey_number": "8", "college": "Duke", "country": "USA"},
    {"id": 18, "first_name": "Dru", "last_name": "Smith", "position": "G", "height": "6-2", "weight": "200", "jersey_number": "12", "college": "Missouri", "country": "USA"}

]

def get_player_by_name(name: str):
    name_lower = name.lower()
    for p in HEAT_ROSTER_2025_26:
        full_name = f"{p['first_name']} {p['last_name']}".lower()
        if full_name == name_lower:
            return p
    return None

def get_player_by_id(player_id: int):
    for p in HEAT_ROSTER_2025_26:
        if p["id"] == player_id:
            return p
    return None

def get_team_roster(team_id: int):
    if team_id == HEAT_TEAM_ID:  # Miami Heat
        return HEAT_ROSTER_2025_26
    return []