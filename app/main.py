"""Webový server aplikace Noví pravopis (FastAPI)."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StrictStr

from .converter import convert

MAX_CHARS = 100_000
MAX_BODY_BYTES = 1_000_000  # ~1 MB
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

CSP = "default-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"

app = FastAPI(title="Noví pravopis", docs_url=None, redoc_url=None, openapi_url=None)


class ConvertRequest(BaseModel):
    text: StrictStr


@app.middleware("http")
async def limits_and_security_headers(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        response = JSONResponse({"error": "Text je příliš dlouhý."}, status_code=413)
    else:
        response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = CSP
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # Chybějící text, špatný typ i neplatný JSON.
    return JSONResponse({"error": "Chybí text k převodu."}, status_code=400)


# Běžná (ne async) funkce: FastAPI ji spustí ve vláknu, takže delší převod
# neblokuje ostatní požadavky.
@app.post("/api/convert")
def api_convert(body: ConvertRequest):
    if len(body.text) > MAX_CHARS:
        return JSONResponse(
            {"error": f"Text je příliš dlouhý (maximum je {MAX_CHARS} znaků)."},
            status_code=413,
        )
    return convert(body.text)


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    return "ok"


# Musí být připojeno jako poslední, aby nepřebilo API.
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")
