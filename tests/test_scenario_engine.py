import unittest

from pydantic import ValidationError

from scenario_engine import ScenarioInput, evaluate_scenario


class ScenarioEngineTests(unittest.TestCase):
    def test_default_scenario_matches_expected_profile(self) -> None:
        result = evaluate_scenario(ScenarioInput())

        self.assertGreater(result.quality, 80)
        self.assertGreater(result.yield_index, 80)
        self.assertEqual(result.waste_risk, "Medium")
        self.assertAlmostEqual(result.waste_score, 19.242, places=3)
        self.assertGreaterEqual(result.confidence, 0.7)

    def test_heat_and_stress_reduce_outcomes(self) -> None:
        baseline = evaluate_scenario(ScenarioInput())
        heat = evaluate_scenario(
            ScenarioInput(
                temperature=7,
                vpd=3.2,
                soil=18,
                irrigation=12,
                stress=62,
            )
        )

        self.assertLess(heat.quality, baseline.quality)
        self.assertLess(heat.yield_index, baseline.yield_index)
        self.assertLess(heat.confidence, baseline.confidence)

    def test_frontend_camel_case_aliases_are_supported(self) -> None:
        scenario = ScenarioInput.model_validate(
            {"cropLoad": 120, "waterCost": 90, "harvestDelay": 12}
        )

        self.assertEqual(scenario.crop_load, 120)
        self.assertEqual(scenario.water_cost, 90)
        self.assertEqual(scenario.harvest_delay, 12)

    def test_out_of_range_values_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ScenarioInput(temperature=30)


if __name__ == "__main__":
    unittest.main()
