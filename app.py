"""FastAPI entry point for the LiDO2 digital twin platform."""

from pathlib import Path

from datetime import date
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse

from scenario_engine import ScenarioInput, ScenarioResult, evaluate_scenario
from open_data_service import OpenDataError, get_environmental_data


APP_ROOT = Path(__file__).resolve().parent
INDEX_FILE = APP_ROOT / "index.html"

app = FastAPI(
    title="LiDO2 Digital Twin Platform",
    description="Python web service for the LiDO2 multi-stakeholder scenario lab.",
    version="2.4.0",
    docs_url="/api/docs",
    redoc_url=None,
)


@app.get("/", include_in_schema=False, response_class=FileResponse)
async def home() -> FileResponse:
    """Serve the existing interactive LiDO2 web interface."""
    if not INDEX_FILE.is_file():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="index.html is missing from the application root.",
        )

    return FileResponse(
        INDEX_FILE,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
        },
    )


@app.get("/health", tags=["Operations"])
async def health() -> dict[str, str | bool]:
    """Health check used by Render and external monitors."""
    return {
        "status": "ok" if INDEX_FILE.is_file() else "degraded",
        "service": "lido2",
        "index_available": INDEX_FILE.is_file(),
    }


VINEYARD_SKETCHFAB_SHORT_URL = "https://skfb.ly/pwWWD"
SKETCHFAB_OEMBED_URL = "https://sketchfab.com/oembed"


async def resolve_vineyard_sketchfab_embed() -> dict[str, str]:
    """Resolve the approved Vineyard share link to a frame-safe Sketchfab embed URL."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=12.0) as client:
            shared = await client.get(VINEYARD_SKETCHFAB_SHORT_URL)
            shared.raise_for_status()
            canonical_url = str(shared.url)
            response = await client.get(SKETCHFAB_OEMBED_URL, params={"url": canonical_url})
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Vineyard 3D model could not be resolved from Sketchfab.",
        ) from exc

    html = str(payload.get("html", ""))
    match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Sketchfab returned no embeddable Vineyard model.",
        )

    parts = urlsplit(match.group(1))
    if parts.scheme != "https" or parts.hostname not in {"sketchfab.com", "www.sketchfab.com"} or "/embed" not in parts.path:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Sketchfab returned an unexpected embed address.",
        )

    params = dict(parse_qsl(parts.query, keep_blank_values=True))
    params.update({"autostart": "1", "autospin": "0.12", "ui_theme": "dark", "ui_infos": "0", "ui_hint": "0"})
    embed_url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), ""))
    return {
        "embed_url": embed_url,
        "source_url": VINEYARD_SKETCHFAB_SHORT_URL,
        "title": str(payload.get("title", "Representative Vineyard 3D model")),
        "author_name": str(payload.get("author_name", "See Sketchfab model page")),
        "provider_name": "Sketchfab",
    }


@app.get("/api/models/vineyard-sketchfab", tags=["Models"])
async def vineyard_sketchfab_model() -> dict[str, str]:
    """Return the resolved frame-safe embed URL for the approved Vineyard model."""
    return await resolve_vineyard_sketchfab_embed()


@app.get("/api/platform-info", tags=["Platform"])
async def platform_info() -> dict[str, str]:
    """Expose basic platform metadata for future frontend integrations."""
    return {
        "name": "International Digital Twin Platform",
        "version": app.version,
        "application": "LiDO2 Multi-Stakeholder Scenario Lab",
        "runtime": "FastAPI",
    }


@app.post(
    "/api/scenarios/evaluate",
    response_model=ScenarioResult,
    tags=["Scenarios"],
)
async def evaluate(payload: ScenarioInput) -> ScenarioResult:
    """Validate and evaluate one field-to-market scenario."""
    return evaluate_scenario(payload)


@app.get("/api/open-data/environment", tags=["Open Data"])
async def open_data_environment(
    days: int = Query(default=7, ge=1, le=31),
    start_date: date | None = None,
    end_date: date | None = None,
    latitude: float = Query(default=46.3827, ge=45.8, le=46.9),
    longitude: float = Query(default=11.2881, ge=10.7, le=11.8),
) -> dict:
    """Return ERA5-Land proxy data for the LiDO field-lab location."""
    try:
        return get_environmental_data(start_date=start_date, end_date=end_date, days=days, latitude=latitude, longitude=longitude)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OpenDataError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
