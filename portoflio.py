#coding: utf-8

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

import utils

class Portfolio:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data

    def display_transaction(self, asset: str) -> None:
        """Display all transactions related to the given asset
        Args:
            - asset (str): asset identifier
        Return:
            None
        """
        asset_data = utils.filter_asset(self._data, asset)

        header_string = '{0:>10s} {1:>5s} {2:>5s} {3:>8s} {4:>8s} {5:>8s} {6:>8s}'.format(
            'DATE', 'ASSET', 'ORDER', 'CURRENCY', 'QUANTITY', 'PRICE', 'FEES')
        print(header_string)

        for _, transaction in asset_data.iterrows():
            date_string = f'{transaction.DATE.strftime("%d/%m/%Y")}' 
            asset_string = f'{transaction.ASSET:>5s}'
            order_string = f'{transaction.BUY_SELL:>5s}'
            currency_string = f'{transaction.DEBIT_CURRENCY if transaction.BUY_SELL == "BUY" else transaction.CREDIT_CURRENCY:>8s}'
            quantity_string = f'{int(transaction.QUANTITY):8d}'
            price_string = f'{transaction.PRICE_PER_UNIT:>8.4f}'
            fees_string = f'{transaction.FEES_COMMISSION:>8.4f}'

            formated_string = ' '.join([
                date_string,
                asset_string,
                order_string,
                currency_string,
                quantity_string,
                price_string,
                fees_string
            ])
            print(formated_string)

    def compute_asset_costs(self, asset: str, currency: Optional[str] = None) -> Dict:
        """Compute costs related to the given asset (excluding fees)
        Args:
            - asset (str): asset identifier
            - currency (str): specify a currency
        Return:
            a Dict containing total costs, quantities and fees (not included in total costs)
            in respective curencies
        """
        if currency:
            raise NotImplemented

        asset_data = utils.filter_asset(self._data, asset)

        _currencies: List = []
        _costs: Dict = {}
        _quantities: Dict = {}
        _fees: Dict = {}
        for i, transaction in asset_data.iterrows():
            if not transaction.BUY_SELL == 'BUY':
                continue
            curr: str = transaction.DEBIT_CURRENCY
            if not curr in _currencies:
                _currencies += [curr]
                _quantities[curr] = transaction.QUANTITY
                _costs[curr] = transaction.QUANTITY * transaction.PRICE_PER_UNIT
                _fees[curr] = transaction.FEES_COMMISSION
            else:
                _quantities[curr] += transaction.QUANTITY
                _costs[curr] += transaction.QUANTITY * transaction.PRICE_PER_UNIT
                _fees[curr] += transaction.FEES_COMMISSION

        costs: Dict = {}
        for curr in _currencies:
            costs[curr] = {
                'total_costs': _costs[curr],
                'total_quantity': _quantities[curr],
                'total_fees': _fees[curr]                
            }
        return costs

    def compute_asset_gains(self, asset: str, currency: Optional[str] = None) -> Dict:
        """Compute realized gains (costs included) related to the given asset
        Args:
            - asset (str): asset identifier
            - currency (str): specify a currency
        Return:
            a Dict containing total gains, quantities and total fees (not included in gains)
            in respective curencies
        """
        if currency:
            raise NotImplemented

        asset_data = utils.filter_asset(self._data, asset)

        _currencies: List = []
        _gains: Dict = {}
        _quantities: Dict = {}
        _fees: Dict = {}
        for i, transaction in asset_data.iterrows():
            if not transaction.BUY_SELL == 'SELL':
                continue
            curr: str = transaction.CREDIT_CURRENCY
            if not curr in _currencies:
                _currencies += [curr]
                _quantities[curr] = transaction.QUANTITY
                _gains[curr] = transaction.QUANTITY * transaction.PRICE_PER_UNIT
                _fees[curr] = transaction.FEES_COMMISSION
            else:
                _quantities[curr] += transaction.QUANTITY
                _gains[curr] += transaction.QUANTITY * transaction.PRICE_PER_UNIT
                _fees[curr] += transaction.FEES_COMMISSION

        costs: Dict = self.compute_asset_costs(asset, currency)

        gains: Dict = {}
        for curr in _currencies:
            gains[curr] = {
                'total_gains': _gains[curr] - costs[curr]['total_costs'],
                'total_quantity': costs[curr]['total_quantity'] - _quantities[curr],
                'total_fees': _fees[curr] + costs[curr]['total_fees']
            }
        return gains


