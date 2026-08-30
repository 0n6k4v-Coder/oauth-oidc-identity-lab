from fastapi import FastAPI

from .routers import authorization, resource


app = FastAPI(
    title="OAuth 2.0 Identity Lab — Same Process",
    version="0.1.0",
)


app.include_router(
    authorization.router,
    prefix="/oauth",
    tags=["authorization-server"],
)

app.include_router(
    resource.router,
    prefix="/api",
    tags=["resource-server"],
)