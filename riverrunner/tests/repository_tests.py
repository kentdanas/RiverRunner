import datetime
from riverrunner import context
from riverrunner.context import Address, Measurement, Metric, Prediction, RiverRun, Station, StationRiverDistance
from riverrunner.repository import Repository
from riverrunner.tests.test_context import TContext
from unittest import TestCase


class TestRepository(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = TContext()
        cls.session = cls.context.Session()
        cls.repo = Repository(session=cls.session)

        cls.context.clear_dependency_data(cls.session)
        cls.context.generate_addresses(cls.session)

    @classmethod
    def tearDownClass(cls):
        cls.context.clear_dependency_data(cls.session)
        cls.session.close()

    def tearDown(self):
        self.context.clear_all_tables(self.session)

    def test_put_predictions_adds_one(self):
        # setup
        predictions = self.context.get_predictions_for_test(1, self.session)

        # assert
        result = self.repo.put_predictions(predictions[0])
        self.assertTrue(result)

    def test_put_predictions_adds_many(self):
        # setup
        predictions = self.context.get_predictions_for_test(10, self.session)

        # assert
        result = self.repo.put_predictions(predictions)
        self.assertTrue(result)

    def test_clear_predictions_empties_table(self):
        # setup
        predictions = self.context.get_predictions_for_test(10, self.session)
        self.repo.put_predictions(predictions)

        # assert
        self.repo.clear_predictions()
        predictions = self.session.query(context.Prediction).all()
        self.assertEqual(len(predictions), 0)

    def test_get_measurements_returns_with_correct_date_range(self):
        # setup
        now = datetime.datetime.now()

        address = self.session.query(Address).first()
        station = Station(
            station_id='1',
            latitude=address.latitude,
            longitude=address.longitude
        )

        run = RiverRun(
            run_id=1,
            put_in_latitude=address.latitude,
            put_in_longitude=address.longitude,
            class_rating='I',
            max_level=100,
            min_level=10,
            take_out_latitude=address.latitude,
            take_out_longitude=address.longitude,
            distance=10,
            river_name='a river',
            run_name='a run'
        )

        strd = StationRiverDistance(
            station_id=station.station_id,
            run_id=run.run_id,
            put_in_distance=1.,
            take_out_distance=1.
        )

        metric = Metric(
            description='a description',
            metric_id=1,
            name='a name',
            units='a scalar'
        )

        [self.session.merge(instance) for instance in [station, run, strd, metric]]

        # ensure the intersection of measurement dates is
        # within a specified date range
        measurements = []
        for i in range(10):
            measurements.append(Measurement(
                station_id=station.station_id,
                metric_id=metric.metric_id,
                date_time=now - datetime.timedelta(days=15)
                if i < 5 else now - datetime.timedelta(5)
            ))
        self.session.add_all(measurements)
        self.session.commit()

        # assert
        measurements = self.repo.get_measurements(
            run_id=run.run_id,
            start_date=now - datetime.timedelta(days=16),
            end_date=now - datetime.timedelta(14)
        )

        self.assertEqual(len(measurements), 5)
        for measurement in measurements:
            self.assertTrue(now - datetime.timedelta(16) <= measurement.date_time < now - datetime.timedelta(14))

    def test_get_measurements_throws_if_start_is_later_than_end(self):
        # setup
        runs = self.context.get_runs_for_test(1, self.session)
        self.session.add_all(runs)

        # assert
        now = datetime.datetime.now()
        self.assertRaises(ValueError, self.repo.get_measurements,
                          run_id=runs[0].run_id,
                          start_date=now - datetime.timedelta(days=10),
                          end_date=now - datetime.timedelta(days=15))

    def test_get_measurements_throws_if_start_is_later_than_today(self):
        # setup
        runs = self.context.get_runs_for_test(1, self.session)
        self.session.add_all(runs)

        # assert
        now = datetime.datetime.now()
        self.assertRaises(ValueError, self.repo.get_measurements,
                          run_id=runs[0].run_id,
                          start_date=now + datetime.timedelta(days=10))

    def test_get_measurements_throws_if_run_id_does_not_exist(self):
        # assert
        self.assertRaises(ValueError, self.repo.get_measurements,
                          run_id=-1)

    def test_get_measurements_returns_past_thirty_if_no_date_range_is_given(self):
        # setup
        now = datetime.datetime.now()

        address = self.session.query(Address).first()
        station = Station(
            station_id='1',
            latitude=address.latitude,
            longitude=address.longitude
        )

        run = RiverRun(
            run_id=1,
            put_in_latitude=address.latitude,
            put_in_longitude=address.longitude,
            class_rating='I',
            max_level=100,
            min_level=10,
            take_out_latitude=address.latitude,
            take_out_longitude=address.longitude,
            distance=10,
            river_name='a river',
            run_name='a run'
        )

        strd = StationRiverDistance(
            station_id=station.station_id,
            run_id=run.run_id,
            put_in_distance=1.,
            take_out_distance=1.
        )

        metric = Metric(
            description='a description',
            metric_id=1,
            name='a name',
            units='a scalar'
        )

        self.session.add_all([station, run, strd, metric])

        measurements = []
        for i in range(10):
            measurements.append(Measurement(
                station_id=station.station_id,
                metric_id=metric.metric_id,
                date_time=now - datetime.timedelta(days=45)
                if i < 5 else now - datetime.timedelta(days=5)
            ))
        self.session.add_all(measurements)
        self.session.commit()

        # assert
        measurements = self.repo.get_measurements(
            run_id=run.run_id
        )

        self.assertEqual(len(measurements), 5)
        for measurement in measurements:
            self.assertTrue(measurement.date_time >= now - datetime.timedelta(30))
