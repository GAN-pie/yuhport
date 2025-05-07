#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint
from re import I
import portoflio
from utils import read_data_export
from portoflio import Portfolio


if __name__ == '__main__':
    data = read_data_export('../patripy/ressources')
    portoflio = Portfolio(data)

    print('ASSETS', portoflio.get_assets())

    # portoflio.display_transaction('SOL')
    # costs = portoflio.compute_asset_costs('SOL')
    # pprint(costs)
    # gains = portoflio.compute_asset_gains('SOL')
    # pprint(gains)

    # portoflio.display_gains()
    portoflio.display_holdings()

