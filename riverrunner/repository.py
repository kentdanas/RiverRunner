import datetime
import pandas as pd
from riverrunner import context
from riverrunner.context import Measurement, Metric, Prediction, RiverRun, Station, StationRiverDistance
from sqlalchemy import asc, func


class Repository:
    def __init__(self, session=None):
        if session is None:
            self.__context = context.Context()
            self.__session = self.__context.Session()
        else:
            self.__session = session

    def __del__(self):
        self.__session.flush()
        self.__session.close()

    def put_predictions(self, predictions):
        """ add a set of predictions
        session will rollback transaction if commit fails

        :param predictions: list, set of predictions to insert
        :return: bool, success/fail
        :raises: TypeError, if param predictions is not a list
        """
        if not type(predictions) is list:
            predictions = [predictions]

        try:
            self.__session.add_all(predictions)
            self.__session.commit()

            return True
        except:
            self.__session.rollback()

            return False

    def clear_predictions(self):
        """ delete all existing predictions from database

        :return: None
        """
        self.__session.query(Prediction).delete()

    def get_measurements(self, run_id, start_date=None, end_date=None):
        """ get a set of measurements from the db

        :param run_id: int, retrieve measurements associated with a specific run
        :param start_date: datetime (optional), beginning of date range for which
               to retrieve measurements. if None is supplied the function will
               default to retrieving the past thirty days
        :param end_date: datetime (optional), end of date range for which to
               retrieve measurements
        :return: DataFrame, containing measurements within the given set of parameters
        :raises: ValueError, if start date is later than end date or start date is
              later than today
        """
        # ensure dates are correct
        if start_date is not None:
            if start_date > datetime.datetime.now():
                raise ValueError('start date cannot be later than today')

            if end_date is not None and end_date < start_date:
                raise ValueError('end date cannot be before start date')
            else:
                end_date = datetime.datetime.now()
        else:
            pass

        # ensure the run_id exists if it was supplied
        if run_id > -1:
            try:
                run = self.__session.query(RiverRun.run_id).filter(RiverRun.run_id == run_id).execute()
            except:
                raise Exception('run_id does not exist')

        # get the measurements
        measurements = self.__session.query(Measurement).filter(
            RiverRun.run_id == run_id and
            start_date <= Measurement.date_time < end_date and
            StationRiverDistance.put_in_distance <= func.min(StationRiverDistance.put_in_distance)
        ).execute()

        return measurements
