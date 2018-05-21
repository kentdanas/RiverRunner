import datetime
import pandas as pd
from riverrunner.arima import Arima
from riverrunner.context import Context, Prediction
from riverrunner import continuous_noaa, settings
from riverrunner.scrape_usgs_data import *
from riverrunner.repository import Repository
import sys
import time


def get_weather_observations(session, attempt=0):
    """input the past 24 hr observations and write to log"""
    try:
        if attempt >= settings.DARK_SKY_RETRIES:
            return 1
        added = continuous_noaa.put_24hr_observations(session)

        print(f'{datetime.datetime.now().isoformat()}: added {added} observations to db')
        return True
    except Exception as e:
        print(f'{datetime.datetime.now().isoformat()}: failed to gather daily observations - {str(e.args)}')
        time.sleep(600)
        get_weather_observations(attempt+1)
        return False


def get_usgs_observations():
    today = datetime.date.today()
    end_date = today - datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=1)
    end_date = end_date.isoformat()
    start_date = start_date.isoformat()

    csv_files = scrape_usgs_data(start_date=start_date, end_date=end_date)
    for csv_file in csv_files:
        print("uploading {}...".format(csv_file))
        upload_data_from_file(csv_file)


def compute_predictions(session):
    """compute and cache predictions for all runs"""
    try:
        arima = Arima()
        repo = Repository(session)
        repo.clear_predictions()

        runs = repo.get_all_runs_as_list()
        for run in runs:
            try:
                predictions = arima.arima_model(run.run_id)

                to_add = [
                    Prediction(
                        run_id=run.run_id,
                        timestamp=pd.to_datetime(d),
                        fr_lb=round(p, 1),
                        fr=round(p, 1),
                        fr_ub=round(p, 1)
                    )
                    for p, d in zip(predictions.values, predictions.index.values)
                ]

                repo.put_predictions(to_add)
                print(f'{datetime.datetime.now().isoformat()}: predictions for {run.run_id}-{run.run_name} added to db')
            except Exception as e:
                print(f'{datetime.datetime.now().isoformat()}: predictions for {run.run_id}-{run.run_name} failed')
    except Exception as e:
        print(f'{datetime.datetime.now().isoformat()}: failed to compute daily predictions- {str(e.args)}')
        return False


def daily_run():
    context = Context(settings.DATABASE)
    session = context.Session()

    #get_weather_observations(session)
    #get_usgs_observations()
    compute_predictions(session)

    session.close()


if __name__ == '__main__':
    daily_run()