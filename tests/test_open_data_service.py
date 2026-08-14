import unittest
from datetime import date

from open_data_service import OpenDataError, calculate_vpd, get_environmental_data


def fixture_payload():
    return {
        "latitude": 46.4,
        "longitude": 11.3,
        "elevation": 226.0,
        "timezone": "Europe/Rome",
        "utc_offset_seconds": 7200,
        "hourly_units": {
            "time": "iso8601",
            "temperature_2m": "°C",
            "relative_humidity_2m": "%",
            "precipitation": "mm",
            "shortwave_radiation": "W/m²",
            "soil_temperature_0_to_7cm": "°C",
            "soil_moisture_0_to_7cm": "m³/m³",
            "et0_fao_evapotranspiration": "mm",
            "wind_speed_10m": "km/h",
        },
        "hourly": {
            "time": ["2026-07-01T12:00", "2026-07-01T13:00"],
            "temperature_2m": [20.0, 22.0],
            "relative_humidity_2m": [60.0, 50.0],
            "precipitation": [1.0, 2.0],
            "shortwave_radiation": [400.0, 500.0],
            "soil_temperature_0_to_7cm": [18.0, 19.0],
            "soil_moisture_0_to_7cm": [0.22, 0.24],
            "et0_fao_evapotranspiration": [0.2, 0.3],
            "wind_speed_10m": [4.0, 6.0],
        },
    }


class OpenDataServiceTests(unittest.TestCase):
    def test_vpd_is_calculated_from_temperature_and_humidity(self):
        self.assertAlmostEqual(calculate_vpd(20, 60), 0.935, places=3)

    def test_proxy_payload_is_normalized_and_labelled(self):
        requested_urls = []
        result = get_environmental_data(
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 1),
            fetcher=lambda url: requested_urls.append(url) or fixture_payload(),
        )
        self.assertEqual(result["source"], "Open-Meteo / ERA5-Land")
        self.assertIn("not validated", result["validationStatus"])
        self.assertEqual(result["summary"]["precipitation"], 3.0)
        self.assertEqual(result["summary"]["soilMoisture"], 23.0)
        self.assertEqual(len(result["series"]), 2)
        self.assertIn("models=era5_land", requested_urls[0])
        self.assertTrue(result["provenance"]["modelPinned"])
        self.assertTrue(result["provenance"]["responseMetadataValidated"])
        self.assertEqual(result["provenance"]["requestedModel"], "era5_land")

    def test_unexpected_response_metadata_is_rejected(self):
        payload = fixture_payload()
        payload["timezone"] = "UTC"
        with self.assertRaises(OpenDataError):
            get_environmental_data(
                start_date=date(2026, 7, 2),
                end_date=date(2026, 7, 2),
                fetcher=lambda _: payload,
            )

    def test_missing_unit_metadata_is_rejected(self):
        payload = fixture_payload()
        del payload["hourly_units"]["soil_moisture_0_to_7cm"]
        with self.assertRaises(OpenDataError):
            get_environmental_data(
                start_date=date(2026, 7, 3),
                end_date=date(2026, 7, 3),
                fetcher=lambda _: payload,
            )

    def test_custom_coordinates_are_requested_and_reported(self):
        requested_urls = []
        result = get_environmental_data(
            start_date=date(2026, 7, 4),
            end_date=date(2026, 7, 4),
            latitude=46.4,
            longitude=11.3,
            fetcher=lambda url: requested_urls.append(url) or fixture_payload(),
        )
        self.assertIn("latitude=46.4", requested_urls[0])
        self.assertIn("longitude=11.3", requested_urls[0])
        self.assertEqual(result["location"]["latitude"], 46.4)
        self.assertEqual(result["location"]["longitude"], 11.3)

    def test_coordinates_outside_analysis_boundary_are_rejected(self):
        with self.assertRaises(ValueError):
            get_environmental_data(
                start_date=date(2026, 7, 5),
                end_date=date(2026, 7, 5),
                latitude=44.0,
                longitude=11.3,
                fetcher=lambda _: fixture_payload(),
            )

    def test_date_range_over_31_days_is_rejected(self):
        with self.assertRaises(ValueError):
            get_environmental_data(
                start_date=date(2026, 6, 1),
                end_date=date(2026, 7, 2),
                fetcher=lambda _: fixture_payload(),
            )


if __name__ == "__main__":
    unittest.main()
