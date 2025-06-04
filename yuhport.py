#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime

import portoflio
from utils import read_data_export
from portoflio import Portfolio
import utils

import pandas as pd


if __name__ == '__main__':
    data = read_data_export('./exports')

    # years = [2022, 2023, 2024]
    # for i, y in enumerate(years):
    #     _data = utils.filter_timerange(data, datetime(1999, 1, 1), datetime(y, 12, 31))
    #     _data = utils.filter_asset(_data, portoflio.CRYPTO_ASSETS)
    #     _portfolio = Portfolio(_data)
    #     _disposals = _portfolio.total_disposal_gains(y, reduce=False)
    #     assert isinstance(_disposals, dict)
    #     utils.display_disposals(_disposals, True if i == 0 else False)
    #     del _data, _portfolio, _disposals

    portoflio = Portfolio(data)
    df_holdings = pd.DataFrame.from_dict(portoflio.holdings(), orient='index', columns=['QUANTITY'])
    print('Portfolio holdings', df_holdings)

