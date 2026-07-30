import time
import json
import requests

GRAPHQL_URL = "http://127.0.0.1:8000/graphql"
REST_BASE = "http://127.0.0.1:8001"
LOG_FILE = "benchmark_log.jsonl"
OUTLIER_THRESHOLD_MS = 5000

SCENARIOS = {
    "scenario_1_player_bio": {
        "graphql": '{ player(name: "Bam Adebayo") { firstName lastName position jerseyNumber } }',
        "rest": [f"{REST_BASE}/players/Bam%20Adebayo"],
    },
    "scenario_2_team_roster_games": {
        "graphql": '{ team(id: 16) { fullName roster { firstName lastName } recentGames(limit: 5) { date homeScore visitorScore } } }',
        "rest": [
            f"{REST_BASE}/teams/16",
            f"{REST_BASE}/teams/16/roster",
            f"{REST_BASE}/teams/16/games?limit=5",
        ],
    },
    "scenario_3_five_teams_games": {
        "graphql": '{ teams(ids: [16, 2, 14, 20, 6]) { fullName recentGames(limit: 5) { date homeScore visitorScore } } }',
        "rest": [f"{REST_BASE}/teams/{tid}/games?limit=5" for tid in [16, 2, 14, 20, 6]],
    },
}

RUNS_PER_SCENARIO = 3


def fire_requests():
    for name, scenario in SCENARIOS.items():
        for _ in range(RUNS_PER_SCENARIO):
            requests.post(GRAPHQL_URL, json={"query": scenario["graphql"]})
            time.sleep(1)
            for url in scenario["rest"]:
                requests.get(url)
            time.sleep(1)


def analyze_log(start_time):
    with open(LOG_FILE) as f:
        entries = [json.loads(line) for line in f if line.strip()]
    entries = [e for e in entries if e["timestamp"] >= start_time]

    graphql_entries = [e for e in entries if e["path"] == "/graphql"]
    rest_entries = [e for e in entries if e["path"] != "/graphql"]

    results = {}
    for name, scenario in SCENARIOS.items():
        rest_call_count = len(scenario["rest"])

        gql_slice = graphql_entries[:RUNS_PER_SCENARIO]
        graphql_entries = graphql_entries[RUNS_PER_SCENARIO:]

        rest_slice = rest_entries[:rest_call_count * RUNS_PER_SCENARIO]
        rest_entries = rest_entries[rest_call_count * RUNS_PER_SCENARIO:]

        gql_clean = [e for e in gql_slice if e["duration_ms"] < OUTLIER_THRESHOLD_MS]
        gql_excluded = len(gql_slice) - len(gql_clean)

        rest_run_totals = []
        rest_excluded = 0
        for i in range(RUNS_PER_SCENARIO):
            run_calls = rest_slice[i * rest_call_count:(i + 1) * rest_call_count]
            clean_calls = [c for c in run_calls if c["duration_ms"] < OUTLIER_THRESHOLD_MS]
            rest_excluded += len(run_calls) - len(clean_calls)
            if clean_calls:
                rest_run_totals.append(sum(c["duration_ms"] for c in clean_calls))

        results[name] = {
            "graphql_avg_ms": round(sum(e["duration_ms"] for e in gql_clean) / max(len(gql_clean), 1), 2),
            "graphql_avg_bytes": round(sum(e["payload_bytes"] for e in gql_slice) / max(len(gql_slice), 1)),
            "graphql_requests": 1,
            "graphql_excluded_outliers": gql_excluded,
            "rest_avg_ms": round(sum(rest_run_totals) / max(len(rest_run_totals), 1), 2),
            "rest_avg_bytes": round(sum(e["payload_bytes"] for e in rest_slice) / RUNS_PER_SCENARIO),
            "rest_requests": rest_call_count,
            "rest_excluded_outliers": rest_excluded,
        }

    return results


def main():
    start_time = time.time()
    fire_requests()
    results = analyze_log(start_time)

    print(f"\n{'Scenario':<30}{'GQL ms':<10}{'REST ms':<10}{'GQL B':<10}{'REST B':<10}{'GQL req':<9}{'REST req':<9}{'Outliers (GQL/REST)'}")
    for name, r in results.items():
        outlier_note = f"{r['graphql_excluded_outliers']}/{r['rest_excluded_outliers']}"
        print(f"{name:<30}{r['graphql_avg_ms']:<10}{r['rest_avg_ms']:<10}{r['graphql_avg_bytes']:<10}{r['rest_avg_bytes']:<10}{r['graphql_requests']:<9}{r['rest_requests']:<9}{outlier_note}")


if __name__ == "__main__":
    main()