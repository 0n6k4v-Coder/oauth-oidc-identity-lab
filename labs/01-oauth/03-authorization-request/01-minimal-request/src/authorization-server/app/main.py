from fastapi import FastAPI


app = FastAPI(
    title="OAuth 2.0 Identity Lab — Minimal Authorization Request",
    version="0.1.0",
)


@app.get("/authorize")
def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str | None = None,
    scope: str | None = None,
) -> dict[str, object]:
    return {
        "message": "Authorization Request received",
        "request": {
            "response_type": response_type,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
        },
    }