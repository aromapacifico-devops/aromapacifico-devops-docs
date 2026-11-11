import unittest
from pathlib import Path

import campaign_cost as model


class CampaignCostTest(unittest.TestCase):
    def test_frequency_is_reused_without_drift(self):
        self.assertEqual(model.annual_cost(model.SCENARIOS["base"], 1)["missions"], 936)
        self.assertEqual(model.annual_cost(model.SCENARIOS["base"], 2)["missions"], 756)

    def test_harvest_images_reconcile_to_approved_total(self):
        volumes = {"Delimit the lot": 0, "Estimate the harvest": 50,
                   "Confirm the alert": 40, "Fumigate": 25, "Verify": 25}
        self.assertAlmostEqual(model.image_count_by_service(volumes), 9000)

    def test_one_verification_per_fumigation(self):
        for year in (1, 2):
            volumes = model.yearly(year)
            self.assertEqual(volumes["Fumigate"], volumes["Verify"])

    def test_scenarios_and_years_are_ordered(self):
        for year in (1, 2):
            totals = [model.annual_cost(model.SCENARIOS[name], year)["total"]
                      for name in ("low", "base", "high")]
            self.assertLess(totals[0], totals[1])
            self.assertLess(totals[1], totals[2])
        self.assertGreater(
            model.annual_cost(model.SCENARIOS["base"], 1)["total"],
            model.annual_cost(model.SCENARIOS["base"], 2)["total"],
        )

    def test_monthly_periods_reconcile_first_year(self):
        scenario = model.SCENARIOS["base"]
        monthly = (
            2 * model.period_cost(scenario, "startup", 1)["total"]
            + 4 * model.period_cost(scenario, "harvest", 1)["total"]
            + 6 * model.period_cost(scenario, "outside", 1)["total"]
        )
        self.assertAlmostEqual(monthly, model.annual_cost(scenario, 1)["total"])

    def test_labor_rates_follow_the_references(self):
        self.assertAlmostEqual(model.PILOT_HOUR_USD, 12.26, places=2)
        self.assertAlmostEqual(model.SUPPORT_HOUR_USD, 4.89, places=2)

    def test_dedicated_brigades_cost_more_than_hourly_work(self):
        base = model.SCENARIOS["base"]
        self.assertGreater(model.dedicated_brigades_total(base, 2),
                           model.annual_cost(base, 2)["total"])

    def test_department_period_adds_up_to_pilot_month(self):
        base = model.SCENARIOS["base"]
        self.assertAlmostEqual(
            model.department_period(base, "harvest", 2)["total"] * model.DEPARTMENTS,
            model.period_cost(base, "harvest", 2)["total"],
        )

    def test_inference_and_agrochemical_are_not_cost_inputs(self):
        source = Path(model.__file__).read_text(encoding="utf-8")
        self.assertNotIn("inference_rate", source)
        self.assertNotIn("agrochemical_price", source)


if __name__ == "__main__":
    unittest.main()
