# coding: utf-8

from glob import glob
from os import path
from typing import List, Optional, Union
from datetime import datetime 

import pandas as pd

RATE_DATA_PATH = './data'

def read_data_export(folder: str) -> pd.DataFrame:
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
    return data

def filter_activity(data: pd.DataFrame, activity: Union[str, List]) -> pd.DataFrame:
    selected = data['ACTIVITY_TYPE'].isin([activity] if isinstance(activity, str) else activity)
    return data[selected]

def filter_timerange(data: pd.DataFrame, begin: datetime, end: datetime) -> pd.DataFrame:
    timerange: pd.DataFrame = data[(data['DATE'] >= begin) & (data['DATE'] <= end)]
    return timerange

def filter_asset(data: pd.DataFrame, asset: Union[str, List], order_type: Optional[str] = None) -> pd.DataFrame:
    selected = data['ASSET'].isin([asset] if isinstance(asset, str) else asset)
    mask = selected
    if order_type:
        mask = data['BUY_SELL'].isin([order_type])
    return data[selected & mask]

def is_multicurrency(data: pd.DataFrame, asset: str) -> bool:
    asset_data = data[data['ASSET'].isin({'ASSET': [asset]})]
    currency_groups = asset_data.groupby('DEBIT_CURRENCY')
    return len(currency_groups) >= 1

def get_conversion_rate(date: datetime, src_currency: str, dest_currency: Optional[str] = None) -> float:
    dest_currency = dest_currency if dest_currency is not None else 'EUR'
    dat_file = path.join(RATE_DATA_PATH, '-'.join([dest_currency.lower(), src_currency.lower()]) + '.csv')
    assert path.isfile(dat_file), 'ERROR: missing conversion rate file'
    data = pd.read_csv(dat_file, sep=',', index_col=0, parse_dates=True, date_format='%d/%m/%Y %H:%M:%S')
    return data[data.index.date == date.date()].iloc[0, 0]

def get_market_value(asset: str, date: datetime) -> float:
    return 0.0
