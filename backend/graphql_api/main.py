import time
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from strawberry.fastapi import GraphQLRouter

from backend.graphql_api.schema import schema
from backend.graphql_api.loaders import get_games_loader
from backend.shared.balldontlie_client import get_team, get_team_games_batch

DEMO_TEAM_IDS = [16, 2, 14, 20, 6]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Warming cache for demo teams...")
    try:
        get_team(DEMO_TEAM_IDS[0])
        get_team_games_batch(DEMO_TEAM_IDS, season=2024, limit_per_team=5)
        print("Cache warm-up complete.")
    except Exception as exc:
        print(f"Cache warm-up failed (non-fatal): {exc}")
    yield


app = FastAPI(title="NBA GraphQL API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kush-graphql-nba.netlify.app"],
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


async def get_context():
    return {"games_loader": get_games_loader()}


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {"message": "GraphQL API is running. Visit /graphql for the playground."}