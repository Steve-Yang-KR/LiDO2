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
- `GET /api/open-data/environment` — retrieve and normalize Open-Meteo/ERA5-Land proxy data for bounded user-supplied coordinates near the LiDO field-lab area
- `/api/docs` — interactive FastAPI API documentation

The **System Validation** workspace runs four live checks against the deployed API: the default profile, Heat Wave KPI reduction, frontend camelCase aliases, and rejection of out-of-range inputs. The global API badge also reports whether the Python service is connected or the interface is using its browser fallback.

The Scenario Lab keeps the interface responsive with an immediate browser preview, then replaces it with the validated Python result. A baseline can be captured at any time to compare quality, yield, water efficiency, waste, value, and confidence.

The **Open Data Twin** uses hourly ERA5-Land reanalysis supplied through Open-Meteo for the LiDO field-lab coordinates. The adapter explicitly requests `models=era5_land`, validates the returned grid coordinates, timezone, hourly columns, and unit metadata, and exposes the result in the API `provenance` object. It visualizes weather, radiation, soil moisture, VPD, ET₀, growing degree days, and a transparent water-stress proxy, and can apply compatible environmental values to Scenario Lab. The interface always identifies these values as `Reanalysis / model estimate` and `Proxy data — not validated against LiDO sensors`; they must not be described as LiDO measurements.

## Monthly field and yield analytics

The Field & Yield Analytics workspace compares separate user-entered apple and vineyard coordinates over a 30-day ERA5-Land window. Environmental charts show model estimates; editable crop-density and fruit/cluster assumptions drive transparent low/base/high yield forecasts. Default coordinates are explicitly labelled as unverified proxies, and all yield results are labelled as model forecasts rather than measured LiDO yields.

## Scientific chart controls

The analytics charts use explicit shared scales, labelled axes, date ticks and hover tooltips. Environment plots combine temperature, soil-moisture and precipitation views with visible frost (0 °C) and heat (32 °C) reference thresholds. Yield plots keep low/base/high forecasts on one scale and shade the ±10% model range. Loaded daily data can be exported as CSV, and each chart can be downloaded as PNG for reports.

## Open-data replay mode

After loading the 30-day dataset, Field & Yield Analytics automatically replays daily ERA5-Land observations as a smoothly interpolated animated stream. Browser-frame animation eases between observations while fixed 30-day axes prevent visual jumping. Operators can play, pause, reset and select the replay speed while live-style KPI cards, progress, timestamps and frost/heat/dry-soil alerts update. The interface permanently identifies this as historical open-data replay and never presents it as a live LiDO sensor feed. The same control surface is designed to accept a genuine sensor stream later without changing the provenance labels.

## Crop-specific phenology models

Apple and Chardonnay no longer share one generic yield curve. The transparent browser model uses separate calendar phenology, GDD bases (apple 4 °C; vineyard 10 °C), sigmoid biomass/yield accumulation, stage-specific water/heat/VPD sensitivity and crop-specific uncertainty (apple ±8%; vineyard ±12%). Apple stages include flowering, fruit set, fruit enlargement and ripening; Chardonnay includes budbreak, flowering/fruit set, berry growth, véraison and ripening. A separate 0–100 quality-index curve is shown against the right axis. These are exploratory model estimates, not calibrated LiDO crop-model outputs or measured growth.

## Run tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the scenario-engine and API-validation test jobs for every pull request and every push to `main`.

## Deploy on Render

Connect this repository as a Render Blueprint. Render reads `render.yaml`, installs the dependencies, starts Uvicorn on the platform-provided port, and checks `/health` before routing traffic.
