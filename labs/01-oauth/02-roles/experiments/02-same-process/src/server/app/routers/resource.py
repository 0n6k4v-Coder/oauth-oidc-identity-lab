from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class HealthResponse(BaseModel):
    status: str


class ProfileResponse(BaseModel):
    id: str
    display_name: str
    resource: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/profile", response_model=ProfileResponse)
async def get_profile() -> ProfileResponse:
    return ProfileResponse(
        id="demo-user",
        display_name="Lab User",
        resource="protected",
    )