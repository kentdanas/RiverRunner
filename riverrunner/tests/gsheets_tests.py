from riverrunner import gsheets
from riverrunner import models
from riverrunner import settings
from unittest import TestCase
import datetime


class TestGSheets(TestCase):
    def setUp(self):
        self.gs = gsheets.Sheets(settings.SHEET_ID_TEST)

    def test_get_all_runs_returns_correct_rows_and_col(self):
        runs = self.gs.get_all_runs()

        self.assertEquals(310, runs.shape[0])
        self.assertEquals(10, runs.shape[1])
        self.assertEquals(set(runs.columns), {
            'run_id',
            'rating',
            'min_fr',
            'max_fr',
            'put_in_lat',
            'put_in_lon',
            'distance',
            'run_name',
            'take_out_lat',
            'take_out_lon'
        })

    def test_get_all_runs_caches_as_expected(self):
        start = time.time()
        self.gs.get_all_runs(force=True)
        d1 = time.time() - start

        start = time.time()
        self.gs.get_all_runs()
        d2 = time.time()-start

        self.assertTrue(d2 < d1)

    def test_get_all_stations_returns_correct_rows_and_cols(self):
        stations = self.gs.get_all_stations()

        self.assertEquals(873, stations.shape[0])
        self.assertEquals(5, stations.shape[1])
        self.assertEquals(set(stations.columns), {
            'station_id',
            'source',
            'name',
            'latitude',
            'longitude'
        })

    def test_get_all_stations_caches_as_expected(self):
        start = time.time()
        self.gs.get_all_stations(force=True)
        d1 = time.time() - start

        start = time.time()
        self.gs.get_all_stations()
        d2 = time.time() - start

        self.assertTrue(d2 < d1)

    def test_put_predictions_puts_one(self):
        p = models.Prediction(
            run_id=0,
            timestamp=datetime.datetime.now(),
            fr_lb=0,
            fr=5,
            fr_ub=10
        )
        rows = self.gs.put_new_predictions([p])

        self.assertEquals(rows, 1)

    def test_put_predictions_puts_many(self):
        predictions = [
            models.Prediction(
                run_id=i,
                timestamp=datetime.datetime.now(),
                fr_lb=0,
                fr=1,
                fr_ub=2
            )
            for i in range(100)
        ]
        rows = self.gs.put_new_predictions(predictions)

        self.assertEquals(rows, 100)

    def test_clear_predictions_clears_all_rows(self):
        self.assertTrue(self.gs.clear_predictions())