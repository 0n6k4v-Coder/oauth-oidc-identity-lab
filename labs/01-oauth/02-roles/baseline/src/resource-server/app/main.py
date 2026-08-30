from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ProfileResponse(BaseModel):
    id: str
    display_name: str
    resource: str


app = FastAPI(
    title="OAuth 2.0 Identity Lab — Resource Server",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/profile", response_model=ProfileResponse)
async def get_profile() -> ProfileResponse:
    return ProfileResponse(
        id="demo-user",
        display_name="Lab User",
        resource="protected",
    )