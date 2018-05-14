"""
Module for exploring river run flow rate data and exogenous predictors to determine
best parameters for ARIMA model.

Functions:
    daily_avg: takes time series with measurements of different timeframes and creates
    dataframe with daily averages

    test_stationarity: implements Dickey-Fuller test and rolling average plots to check
    for stationarity of the time series

    plot_autocorrs: creates plots of autocorrelation function and partial autocorrelation
    function to help determine p and q parameters for ARIMA model
"""

import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from riverrunner.repository import Repository
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import arma_order_select_ic

repo = Repository()

# get data
start = datetime.datetime(2006, 1, 1)
end = datetime.datetime(2016, 1, 1)
test_measures = repo.get_measurements(run_id=599, start_date=start, end_date=end)

def daily_avg(time_series):
    """
    Takes output from get_measurements function and creates dataframe containing
    daily averages
    :param time_series: dataframe with flow rates, assumes output from
    get_measurements function
    :return: time_series_daily: dataframe with daily flow rate averages
    """

    time_series['date_time'] = pd.to_datetime(time_series['date_time'], utc=True)
    time_series.index = time_series['date_time']
    time_series_daily = time_series.resample('D').mean()
    time_series_daily = time_series_daily.dropna()
    return time_series_daily

def test_stationarity(time_series):
    """
    Performs Dickey-Fuller test for stationarity and plots rolling mean and standard
    deviation for visual check
    :param time_series: dataframe with daily flow rate averages
    :return: bool, returns True if data is stationary according to Dickey-Fuller test at
    0.05 level of significance
    """
    # Determine rolling statistics
    rollmean = time_series.rolling(window=30, center=False).mean()
    rollstd = time_series.rolling(window=30, center=False).std()

    # Plot rolling statistics
    plt.plot(time_series, color='blue', label='Raw Data')
    plt.plot(rollmean, color='red', label='Rolling Mean')
    plt.plot(rollstd, color='orange', label='Rolling Standard Deviation')
    plt.title('Rolling Statistics')
    plt.legend()
    plt.show();

    # Dickey-Fuller test
    dftest = adfuller(time_series.iloc[:, 0], autolag='AIC')

    if dftest[0] < dftest[4]['5%']:
        return True
    else:
        return False


def plot_autocorrs(time_series):
    """
    Creates plots of auto-correlation function (acf) and partial auto-correlation function
    (pacf) to help determine p and q parameters for ARIMA model
    :param time_series: dataframe with daily flow rate averages
    :return: plots of acf and pacf
    """
    lag_acf = acf(time_series, nlags=400)
    lag_pacf = pacf(time_series, method='ols')

    plt.subplot(121)
    plt.plot(lag_acf)
    plt.axhline(y=0, linestyle='--', color='gray')
    plt.axhline(y=-1.96 / np.sqrt(len(time_series)), linestyle='--', color='gray')
    plt.axhline(y=1.96 / np.sqrt(len(time_series)), linestyle='--', color='gray')
    plt.title('ACF')
    plt.subplot(122)
    plt.plot(lag_pacf)
    plt.axhline(y=0, linestyle='--', color='gray')
    plt.axhline(y=-1.96 / np.sqrt(len(time_series)), linestyle='--', color='gray')
    plt.axhline(y=1.96 / np.sqrt(len(time_series)), linestyle='--', color='gray')
    plt.title('PACF')
    plt.tight_layout()

# Average data and create train/test split
measures_daily = daily_avg(test_measures)
train_measures_daily = measures_daily[:-10]
test_measures_daily = measures_daily[-10:]

# Ensure data is stationary
test_stationarity(train_measures_daily)

# Determine p and q parameters
params = arma_order_select_ic(train_measures_daily, ic='aic')

# Build and fit model
mod = ARIMA(train_measures_daily, order=(params.aic_min_order[0], 0, params.aic_min_order[1]))
results = mod.fit()
test_measures_daily['prediction'] = results.forecast(steps=10)[0]
train_measures_daily['model'] = results.predict()

# Plot results
plt.plot(test_measures_daily[['value', 'prediction']])
plt.plot(train_measures_daily[['value', 'model']]['2015-07':])
plt.legend(['Test values', 'Prediction', 'Train values', 'Model'])





