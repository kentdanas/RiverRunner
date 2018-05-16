import dateutil
import json
import requests
import sys

from riverrunner import context
from riverrunner import repository


DATA_DIR = "data/"

USGS_BASE_URL = "https://waterservices.usgs.gov/nwis/iv/"
USGS_FORMAT = "json"
USGS_SITE_STATUS = "all"


def get_site_ids():
    """retrieve site ids from file

    Returns:
        [string]: list of site ids
    """
    site_ids = []
    with open(DATA_DIR + "usgs_site_ids.csv", "r") as f:
        site_ids = [line.strip() for line in f]
    return site_ids


def get_param_codes():
    """retrieve parameter codes from file

    Returns:
        [string]: list of parameter codes
    """
    param_codes = []
    with open(DATA_DIR + "usgs_param_codes.csv", "r") as f:
        param_codes = [line.strip() for line in f]
    return param_codes


def get_json_data(site_id, start_date, end_date, param_code):
    """retrieve JSON data for a specific site, parameter, and date range

    Args:
        site_id (string): string representation of site id
        start_date (string): start date in the format 'YYYY-MM-DD'
        end_date (string): end date in the format 'YYYY-MM-DD'
        param_code (string): string representation of parameter code

    Returns:
        {string: string}: map relating timestamps to values
    """
    params = {
        "format": USGS_FORMAT,
        "sites": site_id,
        "startDT": start_date,
        "endDT": end_date,
        "parameterCd": param_code,
        "siteStatus": USGS_SITE_STATUS,
    }
    response = requests.get(USGS_BASE_URL, params=params)
    try:
        response_json = response.json()
    except json.decoder.JSONDecodeError:
        print(response.content)
        raise
    #response_json = requests.get(USGS_BASE_URL, params=params).json()
    time_series_list = response_json["value"]["timeSeries"]
    values_list = []
    if len(time_series_list) > 0:
        values_list = time_series_list[0]["values"][0]["value"]
    date_value_map = {elem["dateTime"]: elem["value"] for elem in values_list}
    return date_value_map


def scrape_usgs_data(start_date, end_date):
    """scrape data for all sites and parameters, over the specified date range

    Args:
        start_date (string): start date in the format 'YYYY-MM-DD'
        end_date (string): end date in the format 'YYYY-MM-DD'

    Returns:
        [string]: list of full paths of CSV files that were written to
    """
    site_ids = get_site_ids()
    param_codes = get_param_codes()
    out_files = []
    for param_code in param_codes:
        out_file = DATA_DIR + "measurements_{}.csv".format(param_code)
        out_files.append(out_file)
        with open(out_file, "w") as f:
            for site_id in site_ids:
                print("{}, {}: ".format(param_code, site_id), end="")
                json_data = get_json_data(
                    site_id=site_id,
                    start_date=start_date,
                    end_date=end_date,
                    param_code=param_code
                )
                print("{}".format(len(json_data)))
                for date_time, value in json_data.items():
                    f.write("{},{},{},{}\n".format(
                        site_id,
                        param_code,
                        date_time,
                        value
                    ))
    return out_files


def upload_data_from_file(csv_file):
    """insert all records contained in file to database

    Args:
        csv_file (string): full path of CSV file containing records

    Returns:
        bool: success/exception
    """
    r = repository.Repository()
    with open(csv_file, "r") as f:
        success = r.put_measurements(csv_file=f)
    return success


if __name__ == "__main__":
    #start_date = "2018-01-01"
    #end_date = "2018-04-30"
    #csv_files = scrape_usgs_data(start_date=start_date, end_date=end_date)
    csv_files = [
        "data/measurements_72254.csv",
        #"data/measurements_72147.csv",
        #"data/measurements_00021.csv",
        #"data/measurements_00045.csv",
        #"data/measurements_00060.csv"
    ]
    for csv_file in csv_files:
        success = upload_data_from_file(csv_file)
