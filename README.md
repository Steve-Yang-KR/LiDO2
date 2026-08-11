# LiDO2

LiDO2 is an international digital-twin platform and multi-stakeholder scenario lab. The existing interactive interface remains in `index.html`; FastAPI now serves the website and provides a foundation for future Python APIs, data integrations, simulations, and AI services.

## Project structure

- `app.py` — FastAPI application and API endpoints
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
- `/api/docs` — interactive FastAPI API documentation

## Deploy on Render

Connect this repository as a Render Blueprint. Render reads `render.yaml`, installs the dependencies, starts Uvicorn on the platform-provided port, and checks `/health` before routing traffic.
