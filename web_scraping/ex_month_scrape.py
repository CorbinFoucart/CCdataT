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

def create_expedia_request_url(start_date, end_date):
    base_url = 'https://www.expedia.com/Flights-Search?'
    flight_dates = 'flighttype=on&starDate={}%2F{}%2F{}&endDate={}%2F{}%2F{}&mode=search&trip=roundtrip'.format(*start_date,*end_date)
    leg1 = '&leg1=from%3ANew+York%2C+NY+%28JFKJohn+F.+Kennedy+Intl.%29%2Cto%3AHong+Kong%2C+Hong+Kong+SAR+%28HKG-Hong+Kong+Intl.%29%2Cdeparture%3A{}%2F{}%2F{}TANYT'.format(*start_date)
    leg2 = '&leg2=from%3AHong+Kong%2C+Hong+Kong+SAR+%28HKG-Hong+Kong+Intl.%29%2Cto%3ANew+York%2C+NY+%28JFK-John+F.+Kennedy+Intl.%29%2Cdeparture%3A{}%2F{}%2F{}TANYT'.format(*end_date)
    passenger_options = '&passengers=children%3A0%2Cadults%3A1%2Cseniors%3A0%2Cinfantinlap%3AY'
    request_url = base_url + flight_dates + leg1 + leg2 + passenger_options
    return request_url

def date2tuple(datetime_obj):
    return datetime_obj.strftime("%m/%d/%Y").split('/')

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
        
        url = create_expedia_request_url(date2tuple(vacation_start), date2tuple(vacation_end))
        browser.get(url)
        time.sleep(15)
        try:
            price_elements = browser.find_elements_by_css_selector('[data-test-id="listing-price-dollars"]')
            price_strings = [item.text for item in price_elements]
            prices = np.asarray([int(string.replace(',', '').replace('$', '')) for string in price_strings])
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
    timeseries.to_csv('expedia_JFK_HKG_prices_{}_2019.csv'.format(month))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape expedia for prices in a given month')
    parser.add_argument('--month', type=int)
    args = parser.parse_args()
    month_to_scrape = args.month
    main(month_to_scrape)



