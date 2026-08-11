# LiDO2

LiDO2 is an international digital-twin platform and multi-stakeholder scenario lab. FastAPI serves the interactive interface and evaluates field-to-market scenarios with a validated Python request model and a transparent deterministic engine.

## Project structure

- `app.py` — FastAPI application and API endpoints
- `scenario_engine.py` — validated scenario inputs and calculation engine
- `index.html` — existing interactive LiDO2 frontend
- `requirements.txt` — Python dependencies
- `.python-version` — Python runtime version for Render
- `render.yaml` — Render Blueprint configuration

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`.

## Endpoints

- `/` — LiDO2 web interface
- `/health` — deployment health check
- `/api/platform-info` — platform metadata
- `POST /api/scenarios/evaluate` — validate and evaluate a Scenario Lab state
- `/api/docs` — interactive FastAPI API documentation

The Scenario Lab keeps the interface responsive with an immediate browser preview, then replaces it with the validated Python result. A baseline can be captured at any time to compare quality, yield, water efficiency, waste, value, and confidence.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Deploy on Render

Connect this repository as a Render Blueprint. Render reads `render.yaml`, installs the dependencies, starts Uvicorn on the platform-provided port, and checks `/health` before routing traffic.
