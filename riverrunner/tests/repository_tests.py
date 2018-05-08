from riverrunner import context
from riverrunner.repository import Repository
from riverrunner.tests.test_context import TContext
from unittest import TestCase


class TestRepository(TestCase):
    def setUp(self):
        self.context = TContext()
        self.session = self.context.Session()
        self.repo = Repository(self.session)

        self.context.clear_all_tables()

    def tearDown(self):
        self.context.clear_all_tables()
        self.session.close()

    def test_put_predictions_adds_one(self):
        # setup
        predictions = self.context.get_predictions_for_test(1, self.session)

        # assert
        result = self.repo.put_predictions(predictions[0])
        self.assertTrue(result)

        # cleanup
        self.session.query(context.Prediction).delete()

    def test_put_predictions_adds_many(self):
        # setup
        predictions = self.context.get_predictions_for_test(10, self.session)

        # assert
        result = self.repo.put_predictions(predictions)
        self.assertTrue(result)

        # cleanup
        self.session.query(context.Prediction).delete()

    def test_clear_predictions_empties_table(self):
        # setup
        predictions = self.context.get_predictions_for_test(10, self.session)
        self.repo.put_predictions(predictions)

        # assert
        self.repo.clear_predictions()
        predictions = self.session.query(context.Prediction).all()
        self.assertEqual(len(predictions), 0)

    def test_get_measurements_returns_all_if_no_params(self):
        self.fail()

    def test_get_measurements_returns_with_correct_runs(self):
        self.fail()

    def test_get_measurements_returns_with_correct_date_range(self):
        self.fail()

    def test_get_measurements_throws_if_start_is_later_than_end(self):
        self.fail()

    def test_get_measurements_throws_if_start_is_later_than_today(self):
        self.fail()

    def test_get_measurements_throws_if_end_is_supplied_without_start(self):
        self.fail()
