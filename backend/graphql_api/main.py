from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from backend.graphql_api.schema import schema
from backend.graphql_api.loaders import get_games_loader

async def get_context():
    return {"games_loader": get_games_loader()}

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI(title="NBA GraphQL API")
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {"message": "GraphQL API is running. Visit /graphql for the playground."}