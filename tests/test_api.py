import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app


class ApiValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health_endpoint_reports_ready(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertTrue(response.json()["index_available"])

    def test_homepage_exposes_data_trust_center(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Data Trust Center", response.text)
        self.assertIn("trustMetadata", response.text)
        self.assertIn("renderDataTrust", response.text)

    def test_homepage_exposes_sensor_comparison_workspace(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Open Data vs Sensor Comparison", response.text)
        self.assertIn("parseSensorCsv", response.text)
        self.assertIn("Synthetic demo", response.text)

    def test_homepage_exposes_spatial_field_twin(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Apple Orchard & Vineyard Field Twin", response.text)
        self.assertIn("renderSpatialField", response.text)
        self.assertIn("Conceptual layout", response.text)

    def test_homepage_exposes_pilot_manager(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Experiment & Pilot Manager", response.text)
        self.assertIn("PILOT_STORAGE_KEY", response.text)
        self.assertIn("Export JSON", response.text)

    def test_homepage_exposes_monthly_field_yield_analytics(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Apple & Vineyard Field and Yield Analytics", response.text)
        self.assertIn("yieldTrend", response.text)
        self.assertIn("Model forecast", response.text)

    @patch("app.get_environmental_data")
    def test_open_data_endpoint_accepts_coordinates(self, mocked) -> None:
        mocked.return_value = {"series": [], "location": {"latitude": 46.4, "longitude": 11.3}}
        response = self.client.get("/api/open-data/environment?days=7&latitude=46.4&longitude=11.3")
        self.assertEqual(response.status_code, 200)
        kwargs = mocked.call_args.kwargs
        self.assertEqual(kwargs["latitude"], 46.4)
        self.assertEqual(kwargs["longitude"], 11.3)

    def test_scientific_chart_controls_are_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("scientificTooltip", response.text)
        self.assertIn("chartScale", response.text)
        self.assertIn("Export CSV", response.text)
        self.assertIn('data-export-svg="appleEnvChart"', response.text)
        self.assertIn("Crop-specific range", response.text)

    def test_open_data_replay_controls_are_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("OPEN-DATA REPLAY", response.text)
        self.assertIn("Not a live LiDO sensor feed", response.text)
        self.assertIn('id="replayPlay"', response.text)
        self.assertIn('id="replayPause"', response.text)
        self.assertIn('id="replaySpeed"', response.text)
        self.assertIn("renderReplayFrame", response.text)

    def test_smooth_replay_animation_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("interpolateReplayDay", response.text)
        self.assertIn("requestAnimationFrame", response.text)
        self.assertIn("SMOOTH REPLAY", response.text)
        self.assertIn("domainDays=days", response.text)

    def test_crop_specific_phenology_models_are_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("CROP_GROWTH_MODELS", response.text)
        self.assertIn("cropPhenology", response.text)
        self.assertIn("Fruit enlargement", response.text)
        self.assertIn("Véraison", response.text)
        self.assertIn("baseTemperature:4", response.text)
        self.assertIn("baseTemperature:10", response.text)
        self.assertIn("Quality index", response.text)

    def test_interactive_3d_crop_twin_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('data-view="crop3d"', response.text)
        self.assertIn('id="cropTwinCanvas"', response.text)
        self.assertIn("renderCropTwin", response.text)
        self.assertIn("drawAppleTwin", response.text)
        self.assertIn("drawVineTwin", response.text)
        self.assertIn("NOT A LIVE LiDO SENSOR TWIN", response.text)
        self.assertIn('id="cropTwinHorizon"', response.text)

    def test_representative_hologram_tree_modes_are_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("REPRESENTATIVE APPLE-TREE MODEL", response.text)
        self.assertIn('id="cropTwinMode"', response.text)
        self.assertIn('id="cropTwinDetail"', response.text)
        self.assertIn("drawAppleDetail", response.text)
        self.assertIn("Hologram", response.text)
        self.assertIn("Point cloud", response.text)
        self.assertIn("NOT A LiDO FIELD SCAN", response.text)

    def test_detailed_mesh_hologram_renderer_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="cropMeshFrame"', response.text)
        self.assertIn("e5e1208e7e734f88b02c5f45c70f8db1", response.text)
        self.assertIn("67.6k-triangle CC BY mesh", response.text)
        self.assertIn("Apple Tree by rhcreations", response.text)
        self.assertIn("syncCropMeshMode", response.text)
        self.assertIn("procedural fallback", response.text)

    def test_mesh_viewer_is_not_blocked_by_load_event(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(".twin3d-stage.mesh-mode .crop-mesh-frame", response.text)
        self.assertNotIn(".mesh-ready.mesh-mode", response.text)
        self.assertIn('loading="eager"', response.text)
        self.assertIn("MESH VIEWER ACTIVE", response.text)


    def test_apple_training_system_twin_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="appleTwinCultivar"', response.text)
        self.assertIn('id="appleTwinRootstock"', response.text)
        self.assertIn('id="appleTwinTraining"', response.text)
        self.assertIn('id="appleTwinAge"', response.text)
        self.assertIn("drawTrainingAppleTwin", response.text)
        self.assertIn("Tall Spindle", response.text)
        self.assertIn("Biaxis / Fruiting Wall", response.text)
        self.assertIn("PARAMETRIC TRAINING SYSTEM", response.text)

    def test_scientifically_refined_apple_architecture_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("rowSpacing", response.text)
        self.assertIn("fruitLoad", response.text)
        self.assertIn("exactly 2 leaders", response.text)
        self.assertIn("No crop", response.text)
        self.assertIn("Managed full crop", response.text)
        self.assertIn("rootSpread", response.text)
        self.assertIn("flat two-leader wall", response.text)

    def test_apple_factors_are_connected_to_parametric_mode(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="factorLinkNotice"', response.text)
        self.assertIn('id="appleFactorImpact"', response.text)
        self.assertIn("ensureParametricTwin", response.text)
        self.assertIn("Fixed representative mesh", response.text)
        self.assertIn("Display automatically switched", response.text)
        self.assertIn("Live factor connection", response.text)
        self.assertIn("Current selection:", response.text)

    def test_viticulture_meeting_mode_is_the_default(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Laimburg viticulture discussion mode", response.text)
        self.assertIn('<option value="vineyard" selected>Vineyard</option>', response.text)
        self.assertIn('id="vineyardTwinCultivar"', response.text)
        self.assertIn('id="vineyardTwinBlock"', response.text)
        self.assertIn('id="vineyardTwinStage"', response.text)
        self.assertIn("Chardonnay · representative", response.text)
        self.assertIn("LAIMBURG / LiDO DATA — NOT CONNECTED", response.text)
        self.assertIn("VINEYARD PARAMETRIC TWIN", response.text)
        self.assertIn("syncCropControlVisibility", response.text)
        self.assertIn("VINEYARD_CULTIVARS", response.text)
        self.assertIn("VINEYARD_STAGES", response.text)

    def test_responsive_vineyard_hologram_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Responsive Hologram Twin", response.text)
        self.assertIn("drawVineHologramDetail", response.text)
        self.assertIn("VINEYARD HOLOGRAM LIVE", response.text)
        self.assertIn("Responsive Vineyard Hologram", response.text)
        self.assertIn("cropTwinCrop.value==='apple'&&cropTwinMode.value==='hologram'", response.text)
        self.assertIn("particles=cropTwinDetail.value", response.text)

    def test_vineyard_hologram_intelligence_layers_are_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="vineyardIntelligence"', response.text)
        self.assertIn('id="vineIntelligenceCanvas"', response.text)
        self.assertIn('id="vineGrowthCanvas"', response.text)
        self.assertIn("Vineyard Hologram Intelligence Layers", response.text)
        self.assertIn("renderVineyardIntelligence", response.text)
        self.assertIn("vineLayerState", response.text)
        self.assertIn('data-vine-layer="soil"', response.text)
        self.assertIn('data-vine-layer="clusters"', response.text)
        self.assertIn("WAITING FOR LAIMBURG DATA", response.text)
        self.assertIn("DATA NOT CONNECTED · REPRESENTATIVE MODEL", response.text)

    def test_sidebar_is_independently_scrollable(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("overflow-y:auto", response.text)
        self.assertIn("overscroll-behavior:contain", response.text)
        self.assertIn("scrollbar-gutter:stable", response.text)
        self.assertIn(".sidebar::-webkit-scrollbar-thumb", response.text)
        self.assertIn("overflow-y:visible", response.text)

    def test_detailed_spatial_vineyard_hologram_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("drawDetailedVine", response.text)
        self.assertIn("vineLeaf", response.text)
        self.assertIn("vineCluster", response.text)
        self.assertIn("sizeTwinCanvas(vineIntelligenceCanvas,430)", response.text)
        self.assertIn("rgba(89,63,38,.46)", response.text)
        self.assertIn("scanY=(twinClock*.04)%ch", response.text)
        self.assertIn("bezierCurveTo", response.text)

    def test_vineyard_sketchfab_model_connection_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="vineyardMeshFrame"', response.text)
        self.assertIn("https://skfb.ly/6R7wy", response.text)
        self.assertIn("resolveVineyardSketchfabModel", response.text)
        self.assertIn("sketchfab.com/oembed", response.text)
        self.assertIn("active-mesh-frame", response.text)
        self.assertIn("VINEYARD 3D MODEL ACTIVE", response.text)
        self.assertIn("creator and licence shown by Sketchfab", response.text)
        self.assertIn("vineyardMeshFrame.src=shortUrl", response.text)

    def test_default_scenario_endpoint(self) -> None:
        response = self.client.post("/api/scenarios/evaluate", json={})
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertGreater(payload["quality"], 80)
        self.assertGreater(payload["yieldIndex"], 80)
        self.assertGreaterEqual(payload["confidence"], 0.7)
        self.assertEqual(payload["engineVersion"], "python-rules-v1")

    def test_camel_case_payload_is_accepted(self) -> None:
        response = self.client.post(
            "/api/scenarios/evaluate",
            json={"cropLoad": 120, "waterCost": 90, "harvestDelay": 12},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("yieldIndex", response.json())

    def test_out_of_range_payload_is_rejected(self) -> None:
        response = self.client.post(
            "/api/scenarios/evaluate",
            json={"temperature": 30},
        )

        self.assertEqual(response.status_code, 422)

    @patch("app.get_environmental_data")
    def test_open_data_endpoint_exposes_proxy_labels(self, mocked) -> None:
        mocked.return_value = {
            "source": "Open-Meteo / ERA5-Land",
            "dataType": "Reanalysis / model estimate",
            "validationStatus": "Proxy data — not validated against LiDO sensors",
            "series": [],
        }
        response = self.client.get("/api/open-data/environment?days=7")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["dataType"], "Reanalysis / model estimate")

    def test_open_data_date_range_requires_both_dates(self) -> None:
        response = self.client.get("/api/open-data/environment?start_date=2026-07-01")
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
