#!/usr/bin/env python
"""
Small code library for web scraping expedia for cheap flights
@author Corbin Foucart
"""
import requests
from selenium import webdriver
import datetime, calendar
import time
import argparse

import numpy as np
import pandas as pd

# create a request url from JFK to Hong Kong, roundtrip
def create_request_roundtrip_url(start_date, end_date, from_airport='BOS'):
    base_url = 'https://www.justfly.com/flight/search?'
    flight_options = 'num_adults=1&num_children=0&num_infants=0&num_infants_lap=0&seat_class=Economy'
    seg0 = '&seg0_date={}-{}-{}&seg0_from={}&seg0_to=HKG'.format(*start_date, from_airport)
    seg1 = '&seg1_date={}-{}-{}&seg1_from=HKG&seg1_to={}'.format(*end_date, from_airport)
    flight_type = '&type=roundtrip'
    request_url = base_url + flight_options + seg0 + seg1 + flight_type
    return request_url

def date2tuple(datetime_obj):
    return datetime_obj.strftime("%Y/%m/%d").split('/')

def gen_daterange(start_day, days):
    return [start_day + datetime.timedelta(days=i) for i in days]

def add_week(start_date):
    """ start_date is datetime object"""
    end_date = start_date + datetime.timedelta(days=7)
    return end_date

def get_month_days(month, year=2019):
    ''' month is int'''
    n_days = calendar.monthrange(2019, month)[1]
    days = [datetime.date(year, month, day) for day in range(1, n_days+1)]
    return days

def scrape_prices(search_dates):
    """ scrapes expedia for prices on search dates, saves to csv file """

    # launch a Firefox session
    browser = webdriver.Firefox()

    # scrape data using the browser
    min_prices = []
    for search_date in search_dates:
        vacation_start = search_date
        vacation_end = add_week(vacation_start)
        
        url = create_request_roundtrip_url(date2tuple(vacation_start), date2tuple(vacation_end), from_airport='LAX')
        browser.get(url)
        time.sleep(40)
        try:
            elements = browser.find_elements_by_class_name('total-price')
            prices = np.asarray([float(elm.text.replace(',', '').replace('$', '')) for elm in elements])
            min_prices.append(np.min(prices))
        except:
            min_prices.append(np.nan)

    # kill the browser
    browser.quit()

    # save the data as a time-series
    timeseries = pd.Series(min_prices, search_dates)
    return timeseries

def main(month):
    """ month is integer month to scrape """
    month_days = get_month_days(month)
    timeseries = scrape_prices(search_dates=month_days)
    timeseries.to_csv('justfly_LAX_HKG_prices_{}_2019.csv'.format(month))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape expedia for prices in a given month')
    parser.add_argument('--month', type=int)
    args = parser.parse_args()
    month_to_scrape = args.month
    main(month_to_scrape)



