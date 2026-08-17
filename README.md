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

## Interactive 3D crop twin

The 3D Crop Twin workspace uses a dependency-free procedural canvas renderer for reliable deployment. Users can rotate and zoom apple-tree or Chardonnay-vine geometry, animate a past/current/future timeline, select 7/14/30-day horizons and change temperature, rainfall and irrigation scenarios. Canopy condition, apple/cluster development, stress, quality and yield indices respond visually and numerically. The visualization is explicitly labelled as an open-data/model estimate—not a live LiDO sensor twin or a calibrated biological reconstruction.

## Representative hologram tree

Until a real LiDO photogrammetry or LiDAR scan is available, the apple twin uses a clearly labelled representative orchard model. Its denser procedural canopy supports low/medium/high detail levels and realistic, hologram and point-cloud display modes. Hologram mode adds cyan edge glow, horizontal scan lines and a moving scan beam; point-cloud mode renders sparse evidence-style geometry. This is presentation geometry—not field-scanned evidence—and can later be replaced without changing the growth, stress and forecast controls.

## Detailed representative mesh renderer

Realistic and Hologram display modes use the embedded [Apple Tree model by rhcreations](https://sketchfab.com/3d-models/apple-tree-e5e1208e7e734f88b02c5f45c70f8db1), a 67.6k-triangle Sketchfab asset licensed under Creative Commons Attribution. The native mesh viewer provides proper depth, perspective, orbit and zoom. LiDO2 adds cyan hologram colour treatment, scan lines, a moving scan beam, provenance and loading status. The mesh iframe is shown immediately whenever Realistic or Hologram mode is selected; it is not gated on a potentially missed load event and uses eager loading even though the workspace starts hidden. Point Cloud mode continues to use the local procedural renderer. This remains a representative asset, not a LiDO scan.

## Run tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the scenario-engine and API-validation test jobs for every pull request and every push to `main`.

## Deploy on Render

Connect this repository as a Render Blueprint. Render reads `render.yaml`, installs the dependencies, starts Uvicorn on the platform-provided port, and checks `/health` before routing traffic.


## Apple nursery and training-system twin

The 3D crop view includes a parametric **Training-system Twin** for representative modern apple orchards. Users can independently choose cultivar (Rosy Glow, Gala, Fuji, or Honeycrisp), rootstock (M.9, M.26, or G.41), training system (Tall Spindle, Slender Spindle, Super Spindle, or Biaxis/Fruiting Wall), and tree age. These selections change leaders, branch density and spread, tree scale, fruit colour, trellis geometry, spacing, and the displayed orchard-density assumptions.

The geometry is a configurable representative model, not a LiDO tree scan or a cultivar-identification model. Default Tall Spindle assumptions are aligned with Cornell Cooperative Extension guidance describing approximately 900–1,200 trees per acre and highly feathered nursery trees. The M.9 support warning follows University of Minnesota Extension guidance that M.9 trees require permanent support.

Primary references:

- [Cornell Cooperative Extension — Tall Spindle Planting System](https://rvpadmin.cce.cornell.edu/uploads/doc_156.pdf)
- [University of Minnesota Extension — Apple rootstocks](https://extension.umn.edu/apple-production/apple-rootstocks)


### Scientific visualization refinements

The representative renderer distinguishes structural variables instead of treating every selection as a different tree species. Cultivar changes fruit colour; rootstock modifies vigor and trunk scale; training system controls leader count, canopy profile and spacing; age controls feathering and crop load. The Biaxis option is constrained to exactly two leaders in one fruiting plane. Nursery trees are displayed as feathered trees with no crop, while Year 1, Year 3 and Mature stages progressively increase managed crop load. Density is calculated from the displayed in-row and row spacing rather than stored as an unrelated fixed value. These remain representative planning assumptions that must be calibrated with LiDO measurements before research or production use.


### Connected factor interaction

Apple cultivar, rootstock, training-system and tree-age changes now automatically switch fixed representative mesh modes to the parametric Training-system Twin. The interface reports the active combination and maps each factor to its visible effect. When a user deliberately selects the external realistic or hologram mesh, a warning explains that the fixed asset cannot be reshaped by the selected factors or forecast scenario. Timeline and environmental controls also switch to the parametric renderer before animation so the visual response is observable.


## Laimburg viticulture meeting default

The 3D Crop Twin now opens in Vineyard mode for the Laimburg discussion. Chardonnay is the representative default, with selectors for cultivar, trial-block geometry and phenology stage. Apple configuration remains available as a secondary crop and is hidden while Vineyard is active. The meeting view prominently states that Laimburg/LiDO measurements are not connected: geometry is representative, phenology is synthetic and environmental values are open-data proxies. Selecting the pending Laimburg block does not imply access to field data.


### Responsive Vineyard Hologram Twin

Vineyard mode now supports a live procedural hologram rather than reusing the fixed apple mesh. The hologram includes trellis rows, posts and wires, depth rows, animated scan lines, canopy particles and cultivar-coloured grape clusters. Cultivar, trial block, phenology, detail level, timeline and environmental scenario remain connected while the hologram is active. The Apple hologram continues to use its separately attributed representative mesh; the Vineyard hologram is generated geometry and remains explicitly labelled as synthetic, not a Laimburg scan.


### Vineyard hologram intelligence layers

The 3D Vineyard view now contains an interactive intelligence panel beneath the hologram. Users can toggle canopy, soil moisture, cluster maturity, microclimate sensor and terrain/block layers. A spatial canvas draws representative vineyard rows, trial boundaries, three moisture zones and sensor nodes. A second canvas shows a growth trajectory and indicative harvest window. Cultivar, block, phenology and scenario controls update maturity, moisture, harvest timing and synthetic confidence. Validation remains explicitly NOT VALIDATED or WAITING FOR LAIMBURG DATA; none of these values are presented as field measurements.


### Detailed spatial vineyard rendering

The Vineyard intelligence canvas has been enlarged and upgraded from simple circles and lines to a layered spatial scene. The foreground row includes curved trunks, bilateral cordons, vertical shoots, shaped leaves and multi-berry clusters; background rows fade into a cyan point-cloud wireframe. Trellis posts and four wire levels, a sloped trial-block outline, animated scan beam, three pulsing sensor nodes, canopy/terrain fields and a stratified soil cross-section share one coordinate system. The rendering remains procedural and representative rather than photogrammetry or a LiDO field scan.
