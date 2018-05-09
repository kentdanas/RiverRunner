import datetime
import pandas as pd
from riverrunner import context
from riverrunner.context import Measurement, Prediction, RiverRun, Station, StationRiverDistance


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

    def get_measurements(self, run_id, start_date=None, end_date=None, min_distance=0.):
        """ get a set of measurements from the db
        behavior:
        1) not supplying a start and end date will return measurements covering the
        previous 30 days. add a start date to retrieve older

        2) supplying a start date without and end date will pull all measurements
        up to the current day

        3) if no min distance (or a negative distance) is provided the method will
        return measurements associated with the closest NOAA and USGS station

        4) supplying a distance will NOT guarantee both NOAA and USGS stations are
        retrieved

        5) supplying an end date without a start will raise an exception
        6) supplying an end date earlier than the start will raise an exception

        :param run_id: int, retrieve measurements associated with a specific run
        :param start_date: datetime (optional), beginning of date range for which
               to retrieve measurements. if None is supplied the function will
               default to retrieving the past thirty days
        :param end_date: datetime (optional), end of date range for which to
               retrieve measurements
        :param min_distance: float, distance from run for which to retrieve measurements
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
            start_date = datetime.datetime.now() - datetime.timedelta(days=30)

        if end_date is None:
            end_date = datetime.datetime.now()

        # ensure the run_id exists if it was supplied
        if run_id > -1:
            try:
                run = self.__session.query(RiverRun.run_id).filter(RiverRun.run_id == run_id).first()
            except Exception as e:
                raise ValueError('run_id does not exist: %s' % [str(a) for a in e.args])
        else:
            raise ValueError('run_id does not exist: %s' % run_id)

        # define the stations we need to reference
        stations = self.__session.query(StationRiverDistance.station_id,
                                        StationRiverDistance.put_in_distance,
                                        Station.source)\
            .join(Station, (Station.station_id == StationRiverDistance.station_id))\
            .filter(StationRiverDistance.run_id == run_id)\
            .order_by(StationRiverDistance.put_in_distance)\
            .all()
        station_ids = [s[0] for s in stations]

        # make sure both a NOAA and USGS weather station are retrieved
        tmp = []
        if min_distance <= 0.:
            noaa, usgs = False, False
            for station in stations:
                if 'NOAA' == station[2]:
                    tmp.append(station)
                    noaa = True
                elif 'USGS' == station[2]:
                    tmp.append(station)
                    usgs = True

                if noaa and usgs:
                    break
        else:
            stations = [s for s in stations if s[1] < min_distance]
            station_ids = [s[0] for s in stations]

        # make the query
        measurements = self.__session.query(Measurement)\
            .filter(Station.station_id.in_(station_ids),
                    Measurement.date_time >= start_date,
                    Measurement.date_time < end_date)\
            .all()

        df = pd.DataFrame([m.dict for m in measurements])
        return df
