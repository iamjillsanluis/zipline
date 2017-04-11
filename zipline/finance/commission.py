#
# Copyright 2016 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import abc

from abc import abstractmethod
from six import with_metaclass

DEFAULT_PER_SHARE_COST = 0.0075       # 0.75 cents per share
DEFAULT_PER_DOLLAR_COST = 0.0015      # 0.15 cents per dollar
DEFAULT_MINIMUM_COST_PER_TRADE = 1.0  # $1 per trade
DEFAULT_FUTURE_COST_PER_TRADE = 2.35  # $2.35 per trade
DEFAULT_FUTURE_COST_BY_SYMBOL = {     # Default costs by root symbol
    'AD': 2.35,  # AUD
    'AI': 2.35,  # Bloomberg Commodity Index
    'BD': 2.35,  # Big Dow
    'BO': 2.35,  # Soybean Oil
    'BP': 2.35,  # GBP
    'CD': 2.35,  # CAD
    'CL': 2.35,  # Crude Oil
    'CM': 2.35,  # Corn e-mini
    'CN': 2.35,  # Corn
    'DJ': 2.35,  # Dow Jones
    'EC': 2.35,  # Euro FX
    'ED': 2.35,  # Eurodollar
    'EE': 2.35,  # Euro FX e-mini
    'EI': 2.35,  # MSCI Emerging Markets mini
    'EL': 2.35,  # Eurodollar NYSE LIFFE
    'ER': 2.35,  # Russell2000 e-mini
    'ES': 2.35,  # SP500 e-mini
    'ET': 2.35,  # Ethanol
    'EU': 2.35,  # Eurodollar e-micro
    'FC': 2.35,  # Feeder Cattle
    'FF': 2.35,  # 3-Day Federal Funds
    'FI': 2.35,  # Deliverable Interest Rate Swap 5y
    'FS': 2.35,  # Interest Rate Swap 5y
    'FV': 2.35,  # US 5y
    'GC': 2.35,  # Gold
    'HG': 2.35,  # Copper
    'HO': 2.35,  # Heating Oil
    'HU': 2.35,  # Unleaded Gasoline
    'JE': 2.35,  # JPY e-mini
    'JY': 2.35,  # JPY
    'LB': 2.35,  # Lumber
    'LC': 2.35,  # Live Cattle
    'LH': 2.35,  # Lean Hogs
    'MB': 2.35,  # Municipal Bonds
    'MD': 2.35,  # SP400 Midcap
    'ME': 2.35,  # MXN
    'MG': 2.35,  # MSCI EAFE mini
    'MI': 2.35,  # SP400 Midcap e-mini
    'MS': 2.35,  # Soybean e-mini
    'MW': 2.35,  # Wheat e-mini
    'ND': 2.35,  # Nasdaq100
    'NG': 2.35,  # Natural Gas
    'NK': 2.35,  # Nikkei225
    'NQ': 2.35,  # Nasdaq100 e-mini
    'NZ': 2.35,  # NZD
    'OA': 2.35,  # Oats
    'PA': 2.35,  # Palladium
    'PB': 2.35,  # Pork Bellies
    'PL': 2.35,  # Platinum
    'QG': 2.35,  # Natural Gas e-mini
    'QM': 2.35,  # Crude Oil e-mini
    'RM': 2.35,  # Russell1000 e-mini
    'RR': 2.35,  # Rough Rice
    'SB': 2.35,  # Sugar
    'SF': 2.35,  # CHF
    'SM': 2.35,  # Soybean Meal
    'SP': 2.35,  # SP500
    'SV': 2.35,  # Silver
    'SY': 2.35,  # Soybean
    'TB': 2.35,  # Treasury Bills
    'TN': 2.35,  # Deliverable Interest Rate Swap 10y
    'TS': 2.35,  # Interest Rate Swap 10y
    'TU': 2.35,  # US 2y
    'TY': 2.35,  # US 10y
    'UB': 2.35,  # Ultra Tbond
    'US': 2.35,  # US 30y
    'VX': 2.35,  # VIX
    'WC': 2.35,  # Wheat
    'XB': 2.35,  # RBOB Gasoline
    'XG': 2.35,  # Gold e-mini
    'YM': 2.35,  # Dow Jones e-mini
    'YS': 2.35,  # Silver e-mini
}


class CommissionModel(with_metaclass(abc.ABCMeta)):
    """
    Abstract commission model interface.

    Commission models are responsible for accepting order/transaction pairs and
    calculating how much commission should be charged to an algorithm's account
    on each transaction.
    """

    @abstractmethod
    def calculate(self, order, transaction):
        """
        Calculate the amount of commission to charge on ``order`` as a result
        of ``transaction``.

        Parameters
        ----------
        order : zipline.finance.order.Order
            The order being processed.

            The ``commission`` field of ``order`` is a float indicating the
            amount of commission already charged on this order.

        transaction : zipline.finance.transaction.Transaction
            The transaction being processed. A single order may generate
            multiple transactions if there isn't enough volume in a given bar
            to fill the full amount requested in the order.

        Returns
        -------
        amount_charged : float
            The additional commission, in dollars, that we should attribute to
            this order.
        """
        raise NotImplementedError('calculate')


class EquityCommissionModel(CommissionModel):
    pass


class FutureCommissionModel(CommissionModel):
    pass


class PerUnit(object):
    """
    Mixin class for Equity and Future commission models calculated using a
    fixed cost per unit traded.
    """

    def __repr__(self):
        return "{class_name}(cost_per_unit={cost_per_unit}, " \
               "min_trade_cost={min_trade_cost})" \
            .format(class_name=self.__class__.__name__,
                    cost_per_unit=self.cost_per_unit,
                    min_trade_cost=self.min_trade_cost)

    def _calculate(self, order, transaction, cost_per_unit):
        """
        If there is a minimum commission:
            If the order hasn't had a commission paid yet, pay the minimum
            commission.

            If the order has paid a commission, start paying additional
            commission once the minimum commission has been reached.

        If there is no minimum commission:
            Pay commission based on number of units in the transaction.
        """
        additional_commission = abs(transaction.amount * cost_per_unit)

        if self.min_trade_cost is None:
            # no min trade cost, so just return the cost for this transaction
            return additional_commission

        if order.commission == 0:
            # no commission paid yet, pay at least the minimum
            return max(self.min_trade_cost, additional_commission)
        else:
            # we've already paid some commission, so figure out how much we
            # would be paying if we only counted per unit.
            per_unit_total = \
                (order.filled * cost_per_unit) + additional_commission

            if per_unit_total < self.min_trade_cost:
                # if we haven't hit the minimum threshold yet, don't pay
                # additional commission
                return 0
            else:
                # we've exceeded the threshold, so pay more commission.
                return per_unit_total - order.commission


class PerShare(PerUnit, EquityCommissionModel):
    """
    Calculates a commission for a transaction based on a per share cost with
    an optional minimum cost per trade.

    Parameters
    ----------
    cost : float, optional
        The amount of commissions paid per share traded.
    min_trade_cost : float, optional
        The minimum amount of commissions paid per trade.
    """

    def __init__(self,
                 cost=DEFAULT_PER_SHARE_COST,
                 min_trade_cost=DEFAULT_MINIMUM_COST_PER_TRADE):
        self.cost_per_share = float(cost)
        self.min_trade_cost = min_trade_cost

    def calculate(self, order, transaction):
        return self._calculate(order, transaction, self.cost_per_share)


class PerContract(PerUnit, FutureCommissionModel):
    """
    Calculates a commission for a transaction based on a per contract cost with
    an optional minimum cost per trade.

    Parameters
    ----------
    cost : float or dict
        The amount of commissions paid per contract traded. If given a float,
        the commission for all futures contracts is the same. If given a
        dictionary, it must map root symbols to the commission cost for
        contracts of that symbol.
    min_trade_cost : float
        The minimum amount of commissions paid per trade.
    """

    def __init__(self, cost, min_trade_cost):
        if isinstance(cost, int):
            cost = float(cost)
        self.cost_per_contract = cost
        self.min_trade_cost = min_trade_cost

    def calculate(self, order, transaction):
        if isinstance(self.cost_per_contract, float):
            cost_per_contract = self.cost_per_contract
        else:
            # Cost per contract is a dictionary. If the user's dictionary does
            # not provide a commission cost for a certain contract, fall back
            # on the default.
            root_symbol = order.asset.root_symbol
            backup_cost = DEFAULT_FUTURE_COST_BY_SYMBOL.get(
                root_symbol, DEFAULT_FUTURE_COST_PER_TRADE,
            )
            cost_per_contract = self.cost_per_contract.get(
                root_symbol, backup_cost,
            )
        return self._calculate(order, transaction, cost_per_contract)


class PerTradeBase(object):
    """
    Mixin class for Equity and Future commission models calculated using a
    fixed cost per trade.
    """

    def __init__(self, cost):
        """
        Cost parameter is the cost of a trade, regardless of share count.
        $5.00 per trade is fairly typical of discount brokers.
        """
        # Cost needs to be floating point so that calculation using division
        # logic does not floor to an integer.
        self.cost = float(cost)

    def calculate(self, order, transaction):
        """
        If the order hasn't had a commission paid yet, pay the fixed
        commission.
        """
        if order.commission == 0:
            # if the order hasn't had a commission attributed to it yet,
            # that's what we need to pay.
            return self.cost
        else:
            # order has already had commission attributed, so no more
            # commission.
            return 0.0


class PerEquityTrade(PerTradeBase, EquityCommissionModel):
    """
    Calculates a commission for a transaction based on a per trade cost.

    Parameters
    ----------
    cost : float, optional
        The flat amount of commissions paid per equity trade.
    """

    def __init__(self, cost=DEFAULT_MINIMUM_COST_PER_TRADE):
        super(PerEquityTrade, self).__init__(cost)


class PerFutureTrade(PerTradeBase, FutureCommissionModel):
    """
    Calculates a commission for a transaction based on a per trade cost.

    Parameters
    ----------
    cost : float, optional
        The flat amount of commissions paid per future trade.
    """
    pass


class PerDollarBase(object):
    """
    Mixin class for Equity and Future commission models calculated using a
    fixed cost per dollar traded.
    """

    def __init__(self, cost=DEFAULT_PER_DOLLAR_COST):
        """
        Cost parameter is the cost of a trade per-dollar. 0.0015
        on $1 million means $1,500 commission (=1M * 0.0015)
        """
        self.cost_per_dollar = float(cost)

    def __repr__(self):
        return "{class_name}(cost_per_dollar={cost})".format(
            class_name=self.__class__.__name__,
            cost=self.cost_per_dollar)

    def calculate(self, order, transaction):
        """
        Pay commission based on dollar value of shares.
        """
        cost_per_share = transaction.price * self.cost_per_dollar
        return abs(transaction.amount) * cost_per_share


class PerEquityDollar(PerDollarBase, EquityCommissionModel):
    """
    Calculates a commission for a transaction based on a per dollar cost.

    Parameters
    ----------
    cost : float
        The flat amount of commissions paid per dollar of equities traded.
    """

    def __init__(self, cost=DEFAULT_PER_DOLLAR_COST):
        super(PerEquityDollar, self).__init__(cost)


class PerFutureDollar(PerDollarBase, FutureCommissionModel):
    """
    Calculates a commission for a transaction based on a per dollar cost.

    Parameters
    ----------
    cost : float
        The flat amount of commissions paid per dollar of futures traded.
    """
    pass


# Alias PerTrade for backwards compatibility.
PerTrade = PerEquityTrade

# Alias PerDollar for backwards compatibility.
PerDollar = PerEquityDollar
