"""FastAPI entry point for the LiDO2 digital twin platform."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse

from scenario_engine import ScenarioInput, ScenarioResult, evaluate_scenario


APP_ROOT = Path(__file__).resolve().parent
INDEX_FILE = APP_ROOT / "index.html"

app = FastAPI(
    title="LiDO2 Digital Twin Platform",
    description="Python web service for the LiDO2 multi-stakeholder scenario lab.",
    version="2.3.0",
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
