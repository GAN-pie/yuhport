# coding: utf-8

from glob import glob
from os import path
from typing import List, Optional, Union
from datetime import datetime, timezone
from numpy import isin
import pytz

import pandas as pd
import yfinance as yf

RATE_DATA_PATH = './data'

def read_data_export(folder: str) -> pd.DataFrame:
    """
    Read data export from CSV files in a single DataFrame sorted by date
    Args:
        - folder (str): specifies data files location
    Return:
        a pandas.DataFrame
    """
    exported_files: List = glob(path.join(folder, '*.CSV'))
    data_files: List = []
    for file_path in exported_files:
        data_files += [pd.read_csv(
            file_path,
            sep=';',
            parse_dates=['DATE'],
            date_format='%d/%m/%Y'
        )]
    data: pd.DataFrame = pd.concat(data_files)
    data.sort_values(by='DATE', inplace=True)
    data.columns = data.columns.str.replace(' ', '_')
    data.columns = data.columns.str.replace('/', '_')
    data.reset_index(drop=True, inplace=True)
    return data

def filter_activity(data: pd.DataFrame, activity: Union[str, List]) -> pd.DataFrame:
    """
    Allows the filtering of data by activity type
    Args:
        - data (pd.DataFrame): data to be filtered
        - activity (str, List[str]): activity(ies) to be retrieved
    Return:
        a new pd.DataFrame
    """
    selected = data['ACTIVITY_TYPE'].isin([activity] if isinstance(activity, str) else activity)
    filtered_data = data[selected]
    assert isinstance(filtered_data, pd.DataFrame)
    return filtered_data

def filter_timerange(data: pd.DataFrame, begin: datetime, end: datetime) -> pd.DataFrame:
    """
    Allow the filtering of date with a timerange
    Args:
        - data (pd.DataFrame): data to be filtered
        - begin (datetime): the begining of the timerange
        - end (datetime): the ending of the timerange
    Return:
        a new pd.DataFrame
    """
    timerange_data = data[(data['DATE'] >= begin) & (data['DATE'] <= end)]
    assert isinstance(timerange_data, pd.DataFrame)
    return timerange_data

def filter_asset(data: pd.DataFrame, asset: Union[str, List], order_type: Optional[str] = None) -> pd.DataFrame:
    """
    Allows filtergin data by asset
    Args:
        - data (pd.DataFrame): data to be filtered
        - asset (str, List[str]): specifies which asset(s) to keep in the data
        - order_type (str): speficies the operation type (BUY/SELL) to consider, default is None
    Return:
        a new pd.DataFrame
    """
    selected = data['ASSET'].isin([asset] if isinstance(asset, str) else asset)
    mask = selected
    if order_type:
        mask = data['BUY_SELL'].isin([order_type])
    filtered_data = data[selected & mask]
    assert isinstance(filtered_data, pd.DataFrame)
    return filtered_data

def is_multicurrency(data: pd.DataFrame, asset: str) -> bool:
    """
    Specifies whether or not the given asset has several currencies in the data
    Args:
        - data (pd.DataFrame): the data to consider
        - asset (str): specifies the asset to consider
    Return:
        a bool value with True when asset has multiple currencies recorded in data
    """
    asset_data = data[data['ASSET'].isin({'ASSET': [asset]})]
    currency_groups = asset_data.groupby('DEBIT_CURRENCY')
    return len(currency_groups) >= 1

def get_conversion_rate(date: datetime, src_currency: str, dest_currency: str = 'EUR') -> float:
    """
    Allows to retrieve currency exchange rate at given datetime
    Args:
        - date (datetime): specifies the date to retrieve rate information
        - src_currency (str): the source currency for exchange rate
        - dest_currency (str): the targeted currency for exchange, default is 'EUR'
    Return:
        a float value denoting the exchange rate between currencies
    """
    if src_currency.lower() == dest_currency.lower():
        return 1.0

    dat_file = path.join(RATE_DATA_PATH, '-'.join([src_currency.lower(), dest_currency.lower()]) + '.csv')
    assert path.isfile(dat_file), 'ERROR: missing conversion rate file'

    data = pd.read_csv(dat_file, sep=',', index_col=0, parse_dates=True, date_format='%d/%m/%Y %H:%M:%S')
    return data[data.index.date == date.date()].iloc[0, 0]

def get_market_value(asset: str, date: datetime) -> float:
    """
    Seek information on maket values.
    Args:
        - asset (str): specifies the asset on which information is to be retrieved
        - date (datetime): the date of reference for historical market values
    Return:
        a float denoting the market value of the asset at the specified date
    """
    ticker = yf.Ticker(asset)
    hist = ticker.history(period='5y', interval='1d')

    # Applying the UTC timezone to match DataFrame from yfinance PriceHistory
    ticker_tz = ticker._get_ticker_tz(10)
    assert isinstance(ticker_tz, str)
    tz = pytz.timezone(ticker_tz)
    date = tz.localize(date, is_dst=False)

    value_price = hist.loc[date, 'Close']
    return value_price
