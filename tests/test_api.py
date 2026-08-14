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

    def test_homepage_exposes_pilot_manager(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Experiment & Pilot Manager", response.text)
        self.assertIn("PILOT_STORAGE_KEY", response.text)
        self.assertIn("Export JSON", response.text)

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
