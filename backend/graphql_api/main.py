from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from backend.graphql_api.schema import schema

graphql_app = GraphQLRouter(schema)

app = FastAPI(title="NBA GraphQL API")
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {"message": "GraphQL API is running. Visit /graphql for the playground."}