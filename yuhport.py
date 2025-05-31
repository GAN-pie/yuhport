#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint
from datetime import datetime, timezone

import portoflio
from utils import read_data_export
from portoflio import Portfolio
import utils

import pandas as pd


if __name__ == '__main__':
    data = read_data_export('./exports')

    years = [2022, 2023, 2024]
    for y in years:
        _data = utils.filter_timerange(data, datetime(1999, 1, 1), datetime(y, 12, 31))
        _portfolio = Portfolio(_data)
        _disposals = pd.DataFrame.from_dict(_portfolio.total_disposal_gains(y), orient='index')
        print(f'{y} disposal', _disposals)
        del _data, _portfolio, _disposals

    portoflio = Portfolio(data)
    df_holdings = pd.DataFrame.from_dict(portoflio.holdings(), orient='index')
    print('Portfolio holdings', df_holdings)

