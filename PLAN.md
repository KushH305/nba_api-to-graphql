Phased roadmap

Phase 1 — Core GraphQL layer (MVP)

Wrap 3-4 nba_api endpoint groups as GraphQL types: Player, Team, Game, BoxScore
Use Strawberry to define a schema where a Player type can resolve nested fields like career_stats, team, recent_games — this is where GraphQL's value shows up (client picks exactly what it needs)
Get one full query working end-to-end: e.g. "give me a player's name, current team, and last 5 games' points" in one request

Phase 2 — REST twin + instrumentation

Stand up the same set of endpoints as plain REST (FastAPI or Flask) hitting the same nba_api calls
Add middleware to both servers that logs: response payload size (bytes), server-side latency, and number of underlying nba_api/network calls triggered
This is the data your "pros and cons" blog and frontend demo will actually run on — without it you're just asserting GraphQL is better, not showing it

Phase 3 — Frontend demo

Plain HTML/JS page with a toggle: same query (e.g. "player search → stat comparison") run through REST vs GraphQL
Show payload size, latency, and request count side by side, live, for each mode
Bonus: a deliberately-designed REST over-fetch example (e.g. REST returns full player object with 40 fields when you only needed 3) vs the equivalent tight GraphQL query — this is the single clearest "aha" moment for a viewer

Phase 4 — Blog

Write as you go, not after — decisions are fresher and you'll have real numbers
Suggested structure below

Phase 5 — Polish & deploy

Deploy backend (Render/Railway/Fly.io all have free tiers friendly to Python) and frontend (Vercel/Netlify/GitHub Pages)
Add a README that reads like a case study, since this doubles as your coffee-chat leave-behind