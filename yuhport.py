#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint
from datetime import datetime

import portoflio
from utils import read_data_export
from portoflio import Portfolio
import utils


if __name__ == '__main__':
    data = read_data_export('../patripy/ressources')
    #data = utils.filter_timerange(data, datetime(2022, 1, 1), datetime(2023, 12, 31))

    portoflio = Portfolio(data)

    #portoflio.display_transactions()

    #print('ASSETS', portoflio.get_assets())

    # portoflio.display_transaction('SOL')
    # costs = portoflio.compute_asset_costs('SOL')
    # pprint(costs)
    # gains = portoflio.compute_asset_gains('SOL')
    # pprint(gains)

    # portoflio.display_gains()
    #portoflio.display_holdings()

    disposal_gains = portoflio._compute_disposal_gains_asset('SOL', '2024')
    pprint(disposal_gains)

