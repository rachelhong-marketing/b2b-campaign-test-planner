import unittest, tempfile, os
from planner import stats, matrix, b2b


class StatsTests(unittest.TestCase):
    def test_sample_size_matches_textbook(self):
        # 5% baseline, detect 20% relative lift (5% -> 6%): about 8,200 per arm at 80% power, 5% alpha
        n = stats.sample_size_per_variant(0.05, 0.20)
        self.assertTrue(7800 <= n <= 8600, n)

    def test_smaller_lift_needs_more_data(self):
        self.assertGreater(stats.sample_size_per_variant(0.04, 0.10), stats.sample_size_per_variant(0.04, 0.30))

    def test_tiny_difference_is_called_noise(self):
        res = stats.read_result(20, 879, 19, 879)
        self.assertGreater(res["p_value"], 0.5)
        self.assertIn("No evidence", res["verdict"])

    def test_big_difference_is_significant(self):
        res = stats.read_result(100, 2000, 160, 2000)
        self.assertLess(res["p_value"], 0.01)
        self.assertIn("Significant", res["verdict"])

    def test_mdl_shrinks_with_more_data(self):
        self.assertGreater(stats.min_detectable_lift(0.04, 1000), stats.min_detectable_lift(0.04, 20000))

    def test_bad_input_is_rejected(self):
        with self.assertRaises(ValueError):
            stats.sample_size_per_variant(1.5, 0.2)


class MatrixTests(unittest.TestCase):
    def _write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        f.write(text); f.close(); self.addCleanup(os.remove, f.name); return f.name

    def test_sample_matrix_is_valid(self):
        here = os.path.dirname(os.path.dirname(__file__))
        self.assertEqual(matrix.validate_file(os.path.join(here, "sample-data", "test-matrix.sample.csv")), [])

    def test_two_variables_in_one_row_is_flagged(self):
        header = ",".join(matrix.REQUIRED)
        row = "T1,Search,Consideration,headline and image,h,a,b,landing page,leads,ctr,4,x,y"
        problems = matrix.validate_file(self._write(header + "\n" + row + "\n"))
        self.assertTrue(any("more than one thing" in p for p in problems))

    def test_identical_utm_is_flagged(self):
        header = ",".join(matrix.REQUIRED)
        row = "T1,Search,Consideration,headline,h,a,b,landing page,leads,ctr,4,same,same"
        problems = matrix.validate_file(self._write(header + "\n" + row + "\n"))
        self.assertTrue(any("utm_content" in p for p in problems))


class B2BTests(unittest.TestCase):
    def plan(self, **kw):
        args = dict(ctr=0.01, lead_rate=0.03, mql_rate=0.20, sql_rate=0.25, lift=0.5, cpc=8,
                    weekly_clicks=1500, lags={"mql": 2, "sql": 8})
        args.update(kw)
        return b2b.funnel_plan(**args)

    def test_deeper_stage_needs_more_clicks_and_budget(self):
        lead, mql, sql = self.plan()
        self.assertLess(lead["clicks"], mql["clicks"])
        self.assertLess(mql["cost"], sql["cost"])

    def test_sales_cycle_lag_delays_the_read(self):
        no_lag = self.plan(lags={})[1]
        lagged = self.plan()[1]
        self.assertEqual(lagged["read_week"], no_lag["read_week"] + 2)

    def test_deepest_fit_skips_stages_that_take_too_long(self):
        self.assertEqual(b2b.deepest_fit(self.plan())["stage"], "mql")
        self.assertIsNone(b2b.deepest_fit(self.plan(weekly_clicks=50)))

    def test_accounts_raise_the_sample_size(self):
        self.assertEqual(b2b.design_effect(1), 1)
        self.assertAlmostEqual(b2b.design_effect(5, 0.1), 1.4)
        plain = self.plan()[0]["clicks"]
        clustered = self.plan(deff=b2b.design_effect(5, 0.1))[0]["clicks"]
        self.assertGreater(clustered, plain)

    def test_audience_below_platform_minimum_is_flagged(self):
        msgs = b2b.audience_check(1500, 1000)
        self.assertTrue(any("platform minimum" in m for m in msgs))
        self.assertEqual(b2b.audience_check(50000, 1000), [])

    def test_small_audience_needs_too_many_views(self):
        msgs = b2b.audience_check(10000, 1000, impressions_per_variant=500000, max_frequency=10)
        self.assertTrue(any("times" in m for m in msgs))

    def test_sample_report_clicks_win_but_qualified_leads_do_not(self):
        here = os.path.dirname(os.path.dirname(__file__))
        _, reads = b2b.read_funnel_file(os.path.join(here, "sample-data", "fake-results.csv"))
        self.assertIn("Significant", reads[0][1]["verdict"])
        self.assertIn("No evidence", reads[-1][1]["verdict"])


if __name__ == "__main__":
    unittest.main()
