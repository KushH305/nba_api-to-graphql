from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from backend.graphql_api.schema import schema
from backend.graphql_api.loaders import get_games_loader
import time
import json
from fastapi import Request


async def get_context():
    return {"games_loader": get_games_loader()}

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI(title="NBA GraphQL API")
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {"message": "GraphQL API is running. Visit /graphql for the playground."}


@app.middleware("http")
async def add_metrics_logging(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    # Read the response body to measure size, then reconstruct it
    # (FastAPI response bodies are streams — reading consumes them once)
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

    from starlette.responses import Response
    return Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )