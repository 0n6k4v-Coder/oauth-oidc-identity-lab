from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import engine


app = FastAPI(
    title="OAuth 2.0 Identity Lab — Authorization Server",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5373"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

@app.get("/health")
def health() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "service": "authorization-server",
        "role": "authorization_server",
    }

@app.get("/database-check")
def database_check() -> dict[str, str]:
    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

    return {
        "service": "authorization-server",
        "database": database_name,
    }