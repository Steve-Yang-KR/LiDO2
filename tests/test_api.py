import unittest

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


if __name__ == "__main__":
    unittest.main()
