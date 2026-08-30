from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    role: str


app = FastAPI(
    title="OAuth 2.0 Identity Lab — Authorization Server",
    version="0.1.0",
)


@app.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="authorization-server",
        role="authorization_server",
    )