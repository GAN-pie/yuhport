#coding: utf-8

from datetime import datetime
from typing import Dict, List, Optional, Union
import pandas as pd

import utils

VALID_ACTIVITY = ['INVEST_ORDER_EXECUTED', 'INVEST_RECURRING_ORDER_EXECUTED']

CRYPTO_ASSETS = [
    'SWQ',
    'ETH',
    'SOL',
    'DOT',
    'XRP',
    'XBT',
    'MKR',
    'AAV',
    'BNT',
    'MAT',
]

TICKER_MAPPING = {
    'AAV': 'AAVE-USD',
    'BNT': 'BNT-USD',
    'DOT': 'DOT-USD',
    'ETH': 'ETH-USD',
    'MAT': 'MATIC-USD',
    'MKR': 'MKR-USD',
    'SOL': 'SOL-USD',
    'XBT': 'BTC-USD',
    'XRP': 'XRP-USD'
}

class Portfolio:
    def __init__(self, data: pd.DataFrame) -> None:
        self._data = utils.filter_activity(data, VALID_ACTIVITY)

    def get_assets(self) -> List[str]:
        """
        Give the assets list contained in the portfolio
        Returns:
            a list of assets
        """
        return self._data['ASSET'].dropna().unique().tolist()

    def holdings(self) -> Dict[str, int]:
        """
        Compute positions for every assets in their specific currency
        Returns:
            a Dict with <asset>-<currency> keys mapping to held shares quantities
        """
        assets_currencies_map: Dict[str, int] = {}
        # Adding BUY operations
        for grouping, group_data in self._data.groupby(['ASSET', 'DEBIT_CURRENCY']):
            assert isinstance(grouping, tuple)
            _asset, _currency = grouping
            qte = group_data['QUANTITY'].sum()
            key_string = "-".join([_asset, _currency])
            if not key_string in assets_currencies_map:
                assets_currencies_map[key_string] = qte
            else:
                assets_currencies_map[key_string] += qte
        # Substract SELL operations
        for grouping, group_data in self._data.groupby(['ASSET', 'CREDIT_CURRENCY']):
            assert isinstance(grouping, tuple)
            _asset, _currency = grouping
            _asset, _currency = grouping
            qte = group_data['QUANTITY'].sum()
            key_string = "-".join([_asset, _currency])
            if not key_string in assets_currencies_map:
                assets_currencies_map[key_string] = -qte
            else:
                assets_currencies_map[key_string] -= qte
        return assets_currencies_map

    def display_transactions(self, asset: Optional[str] = None) -> None:
        """Display all transactions related to the given asset if specified or all assets
        Args:
            - asset (str): asset identifier
        Return:
            None
        """
        asset_data = utils.filter_asset(self._data, [asset] if asset else self.get_assets())

        header_string = '{0:>10s} {1:>8s} {2:>5s} {3:>8s} {4:>12s} {5:>10s} {6:>6s}'.format(
            'DATE', 'ASSET', 'ORDER', 'CURRENCY', 'QUANTITY', 'PRICE', 'FEES')
        print(header_string)


        for _, transaction in asset_data.iterrows():
            date_string = f'{transaction.DATE.strftime("%d/%m/%Y")}' 
            asset_string = f'{transaction.ASSET:>8s}'
            try:
                order_string = f'{transaction.BUY_SELL:>5s}'
            except ValueError as err:
                print(err, transaction)
                exit()
            currency_string = f'{transaction.DEBIT_CURRENCY if transaction.BUY_SELL == "BUY" else transaction.CREDIT_CURRENCY:>8s}'
            quantity_string = f'{transaction.QUANTITY:>10.6f}'
            price_string = f'{transaction.PRICE_PER_UNIT:>10.4f}'
            fees_string = f'{transaction.FEES_COMMISSION:>6.2f}'

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

    def display_gains(self, asset: Optional[str] = None) -> None:
        """Display all gains or related to the given asset if specified
        Args:
            - asset (str): the asset identifier
        Return:
            None
        """

        header_string: str = '{0:>10s} {1:>10s} {2:>10s}'.format('ASSET', 'GAINS', 'FEES')
        print(header_string)

        assets: List = [asset] if asset else self.get_assets()
        for _asset in assets:
            gains: Dict = self.compute_asset_gains(_asset)
            for currency, _gains in gains.items():
                gains_string: str = f'{"-".join([_asset, currency]):>10s} {_gains["total_gains"]:>+10.4f} {_gains["total_fees"]:>10.4f}'
                print(gains_string)

    def display_holdings(self, asset: Optional[str] = None) -> None:
        """Display holdings of all assets or only the specified one
        Args:
            - asset (str): the asset identifier
        Return:
            None
        """

        header_string: str = '{0:>10s} {1:>12s} {2:>10s} {3:>10s}'.format(
            'ASSET', 'QUANTITY', 'GAINS', 'FEES')
        print(header_string)

        assets: List = [asset] if asset else self.get_assets()

        for _asset in assets:
            gains: Dict = self.compute_asset_gains(_asset)
            for currency, _gains in gains.items():
                holdings_string: str = f'{"-".join([_asset, currency]):>10s} {_gains["total_quantity"]:>10.6f} {_gains["total_gains"]:>+10.4f} {_gains["total_fees"]:>10.4f}'
                print(holdings_string)

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
                # this if statement has the side effect of ignoring all currency-based trades
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
                # this if statement has the side effect of ignoring all currency-based trades
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

        if not _gains:
            return {
                _curr: {
                    'total_gains': 0.0,
                    'total_quantity': _costs['total_quantity'],
                    'total_fees': _costs['total_fees']
                }
                for _curr, _costs in costs.items()
            }
        else:
            gains: Dict = {}
            for curr in _currencies:
                gains[curr] = {
                    'total_gains': _gains[curr] - costs[curr]['total_costs'],
                    'total_quantity': costs[curr]['total_quantity'] - _quantities[curr],
                    'total_fees': _fees[curr] + costs[curr]['total_fees']
                }
            return gains

    def _compute_disposal_gains_asset(self, asset: str, year: str, currency: Optional[str] = None) -> Dict:
        data = utils.filter_timerange(
            self._data,
            datetime(int(1990), 1, 1),
            datetime(int(year), 12, 31)
        )
        asset_data = utils.filter_asset(data, asset)
        # print(asset_data)

        currencies: Dict = {}

        sell_transactions = asset_data[asset_data['BUY_SELL'].isin(['SELL'])]
        for i, transac in sell_transactions.iterrows():
            print(i, transac)
            _currency = transac.CREDIT_CURRENCY
            _raw_sell_price = transac.QUANTITY * transac.PRICE_PER_UNIT
            _net_sell_price = _raw_sell_price - transac.FEES_COMMISSION

            integer_loc = asset_data.index.get_loc(i)
            _portfolio_to_date = Portfolio(
                asset_data.iloc[:integer_loc]
            )
            _portfolio_to_date.display_transactions()

            # TODO: if asset is crypto compute porfolio value to date
            #_asset_asset_data = utils.filter_asset(asset_data, CRYPTO_ASSETS)
            #_portfolio_value: float

            _cost = _portfolio_to_date.compute_asset_costs(asset)
            _raw_asset_cost = _cost[_currency]['total_costs']
            _net_asset_cost = _raw_asset_cost + _cost[_currency]['total_fees']

            _disposal_gain = _net_sell_price - _net_asset_cost

            print(f'Net selling price ({_currency}): {_net_sell_price:>10.4f}')
            print(f'Net asset cost ({_currency}): {_net_asset_cost:>10.4f}') 
            print(f'Net disposal gain ({_currency}): {_disposal_gain:>+10.4f}') 

            if not currencies.get(_currency):
                currencies[_currency] = [_disposal_gain]
            else:
                currencies[_currency] += [_disposal_gain]

        return {curr: sum(gains) for curr, gains in currencies.items()}

    def asset_cost(
            self,
            asset: str,
            currency: Optional[str] = None,
            averaged: Optional[bool] = True,
            operation_id: Optional[int] = None) -> float:
        """
        Compute the (averaged) acquisition cost of the asset in the given currency, at the time before operation (if specified)
        Args:
            - asset (str): specifies the asset
            - currency (str): the currency of the asset (for multicurrency assets)
            - averaged (bool): whether or not to average acquisition costs, default is True
            - operation_id (int): integer-based index of the inner DataFrame
        Return:
            a float refering to acquisition cost
        """
        if operation_id:
            _portfolio = Portfolio(self._data.iloc[:operation_id])
            return _portfolio.asset_cost(asset, currency, averaged)
        cost = 0.0
        qte = 0
        for _, operation in self._data.iterrows():
            if operation.BUY_SELL != 'BUY' or operation.DEBIT_CURRENCY != currency or operation.ASSET != asset:
                continue
            raw_operation_price = operation.PRICE_PER_UNIT * operation.QUANTITY
            net_operation_price = raw_operation_price + operation.FEES_COMMISSION

            rate = utils.get_conversion_rate(operation.DATE, operation.DEBIT_CURRENCY)
            cost += net_operation_price * rate
            qte += operation.QUANTITY

        return cost / (qte if averaged else 1)

    def portfolio_cost(self, operation_id: Optional[int] = None) -> float:
        """
        Compute the whole portfolio acquisition costs before the given operation (if specified)
        Args:
            - operation_id (int): integer-based index of the inner DataFrame
        Return:
            a float denoting the total costs of portfolio (including fees)
        """
        if operation_id:
            _portfolio = Portfolio(self._data.iloc[:operation_id])
            return _portfolio.portfolio_cost()
        cost = 0.0
        for _, operation in self._data.iterrows():
            if operation.BUY_SELL != 'BUY':
                continue
            raw_operation_price = operation.PRICE_PER_UNIT * operation.QUANTITY
            net_operation_price = raw_operation_price + operation.FEES_COMMISSION

            rate = utils.get_conversion_rate(operation.DATE, operation.DEBIT_CURRENCY)
            cost += net_operation_price * rate

        return cost

    def portfolio_value(self, operation_id: Optional[int] = None, date: Optional[datetime] = None) -> float:
        """
        Compute the whole portfolio value at the time before the given operation (if specified)
        Args:
            - operation_id (int): integer-based index of the inner DataFrame
            - date (datetime): the date of reference
        Return:
            a float denoting the value of the portfolio
        """
        date = date if date is not None else datetime.today()
        assert isinstance(date, datetime)
        if operation_id:
            _portfolio = Portfolio(self._data.iloc[:operation_id])
            return _portfolio.portfolio_value(operation_id=None, date=date)
        values = 0.0
        for name, postition_qte in self.holdings().items():
            _asset, _currency = name.split('-')
            try:
                market_price = utils.get_market_value(TICKER_MAPPING[_asset], date)
            except KeyError:
                return 0.0
            rate = utils.get_conversion_rate(date, _currency)

            values += market_price * rate * postition_qte

        return values

    def total_disposal_gains(self, year: int, reduce: Optional[bool] = None) -> Union[float, Dict]:
        """
        The function calculates the total disposal gains of the year.
        Args:
            - year (int): an integer specifying the year of reference
            - reduce (bool): whether or not to return a single net disposal gain or raw individual gains
        Return:
            a dictionary containing raw disposal gains, or a single float if reduce is True
        """
        year_data_mask = self._data['DATE'].dt.year == year
        sell_data_mask = self._data['BUY_SELL'] == 'SELL'

        operations = self._data[year_data_mask & sell_data_mask]
        # raw_disposal_gains: Dict[str, List[float]] = {}
        raw_disposal_gains: Dict[str, List[Dict]] = {}
        for i, _ in operations.iterrows():
            operation_id = self._data.index.get_loc(i)
            assert isinstance(operation_id, int), f'{operation_id} must be int, not {type(operation_id)}'

            unit_price = self._data.iloc[operation_id].PRICE_PER_UNIT
            quantity = self._data.iloc[operation_id].QUANTITY
            fees = self._data.iloc[operation_id].FEES_COMMISSION
            currency = self._data.iloc[operation_id].CREDIT_CURRENCY
            date = self._data.iloc[operation_id].DATE
            asset = self._data.iloc[operation_id].ASSET

            _asset = "-".join([asset, currency])

            rate = utils.get_conversion_rate(date, currency)

            selling_price = (unit_price * quantity - fees) * rate
            disposal_gain: float
            avg_cost = 0.0
            if asset in CRYPTO_ASSETS:
                _portfolio = Portfolio(utils.filter_asset(self._data, CRYPTO_ASSETS))
                portfolio_cost = _portfolio.portfolio_cost(operation_id)
                portfolio_value = _portfolio.portfolio_value(operation_id, date)
                disposal_gain = selling_price - portfolio_cost * selling_price / portfolio_value
                avg_cost = _portfolio.asset_cost(asset, currency, True, operation_id)
            else:
                avg_cost = self.asset_cost(asset, currency, True, operation_id)
                portfolio_cost = self.portfolio_cost(operation_id)
                portfolio_value = self.portfolio_value(operation_id, date)
                disposal_gain = selling_price - avg_cost * quantity
           

            if raw_disposal_gains.get(_asset):
                raw_disposal_gains[_asset] += [{
                    'date': date,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'fees': fees,
                    'avg_cost': avg_cost,
                    'portfolio_cost': portfolio_cost,
                    'portfolio_value': portfolio_value,
                    'disposal_gain': disposal_gain,
                    'rate': rate
                }]
            else:
                raw_disposal_gains[_asset] = [{
                    'date': date,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'fees': fees,
                    'avg_cost': avg_cost,
                    'portfolio_cost': portfolio_cost,
                    'portfolio_value': portfolio_value,
                    'disposal_gain': disposal_gain,
                    'rate': rate
                }]


        if reduce:
            net_value = sum([sum(_asset_disposals['disposal_gain']) for _asset_disposals in raw_disposal_gains.values()])
            return net_value
        return raw_disposal_gains

