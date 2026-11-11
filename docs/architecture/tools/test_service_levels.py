import unittest

import service_levels as model


class ServiceLevelsTest(unittest.TestCase):
    def test_delivery_budget_is_a_few_alerts(self):
        self.assertAlmostEqual(model.delivery_budget("normal"), 1.4)
        self.assertAlmostEqual(model.delivery_budget("harvest"), 3.0)

    def test_availability_budget_in_lookups(self):
        self.assertAlmostEqual(model.availability_budget("normal"), 675)
        self.assertAlmostEqual(model.availability_budget("harvest"), 2700)

    def test_budget_is_ninety_minutes_of_peak_outage(self):
        for month in ("normal", "harvest"):
            self.assertAlmostEqual(model.outage_minutes_in_budget(month), 90)

    def test_a_full_recovery_outage_at_the_peak_misses_the_objective(self):
        self.assertAlmostEqual(model.recovery_outage_lookups("harvest"), 7200)
        self.assertGreater(model.recovery_outage_lookups("harvest"), model.availability_budget("harvest"))

    def test_window_fits_in_log_retention(self):
        self.assertLessEqual(model.WINDOW_DAYS, model.LOG_RETENTION_DAYS)

    def test_saved_queries_cost_less_than_managed_objectives(self):
        self.assertLess(model.saved_query_cost(), 0.02)
        self.assertAlmostEqual(model.managed_slo_cost(), 1.06, places=2)


if __name__ == "__main__":
    unittest.main()
