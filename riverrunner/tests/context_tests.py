from riverrunner import context
from riverrunner.tests.test_context import TContext
from unittest import TestCase


class TestContext(TestCase):
    def setUp(self):
        self.context = TContext()
        self.session = self.context.Session()

        self.context.clear_all_tables()

    def tearDown(self):
        self.context.clear_all_tables()
        self.session.close()

    def test_add_prediction(self):
        # setup
        predictions = self.context.get_predictions_for_test(1, self.session)
        self.session.add(predictions[0])
        self.session.commit()

        # assert
        predictions = self.session.query(context.Prediction).all()
        self.assertEqual(len(predictions), 1)

        # cleanup
        self.session.query(context.Prediction).delete()

    def test_add_many_predictions(self):
        # setup
        predictions = self.context.get_predictions_for_test(10, self.session)
        self.session.add_all(predictions)
        self.session.commit()

        # assert
        predictions = self.session.query(context.Prediction).all()
        self.assertEqual(len(predictions), 10)

        # cleanup
        self.session.query(context.Prediction).delete()

    def test_remove_prediction(self):
        # setup
        predictions = self.context.get_predictions_for_test(2, self.session)
        self.session.add_all(predictions)
        self.session.commit()

        # assert
        self.session.query(context.Prediction).delete(predictions[0])
        predictions = self.session.query(context.Prediction).all()
        self.assertEqual(len(predictions), 1)

        # cleanup
        self.session.query(context.Prediction).delete()

    def test_remove_all_predictions(self):
        # setup
        predictions = self.context.get_predictions_for_test(10, self.session)
        self.session.add_all(predictions)
        self.session.commit()

        # assert
        self.session.query(context.Prediction).delete()
        predictions = self.session.query(context.Prediction).all()
        self.assertEqual(len(predictions), 0)

    def test_add_one_measurement(self):
        # setup
        measurement = self.context.get_measurements_for_test(1, self.session)[0]
        self.session.add(measurement)
        self.session.commit()

        # assert
        measurements = self.session.query(context.Measurement).all()
        self.assertEqual(len(measurements), 1)

        # cleanup
        self.context.clear_all_tables()

    def test_add_many_measurements(self):
        # setup
        measurements = self.context.get_measurements_for_test(10, self.session)
        self.session.add_all(measurements)
        self.session.commit()

        # assert
        measurements = self.session.query(context.Measurement).all()
        self.assertEqual(len(measurements), 10)

        # cleanup
        self.context.clear_all_tables()

    def test_remove_measurement(self):
        # setup
        measurements = self.context.get_measurements_for_test(1, self.session)
        self.session.add(measurements[0])
        self.session.commit()

        # run
        self.session.delete(measurements[0])

        # assert
        measurements = self.session.query(context.Measurement).all()
        self.assertEqual(len(measurements), 0)
