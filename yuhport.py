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
    # data = utils.filter_timerange(data, datetime(2022, 1, 1), datetime(2023, 12, 31))
    # data = utils.filter_asset(data, portoflio.CRYPTO_ASSETS)

    portoflio = Portfolio(data)
    df_holdings = pd.DataFrame.from_dict(portoflio.holdings(), orient='index')
    print(df_holdings)

    df_disposals = pd.DataFrame.from_dict(portoflio.total_disposal_gains(2023), orient='index')
    print(df_disposals)

