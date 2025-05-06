#!/usr/bin/env python3
# coding: utf-8

from pprint import pprint
import portoflio
from utils import read_data_export
from portoflio import Portfolio


if __name__ == '__main__':
    data = read_data_export('../patripy/ressources')

    portoflio = Portfolio(data)
    portoflio.display_transaction('SOL')
    costs = portoflio.compute_asset_costs('SOL')
    pprint(costs)
    gains = portoflio.compute_asset_gains('SOL')
    pprint(gains)


