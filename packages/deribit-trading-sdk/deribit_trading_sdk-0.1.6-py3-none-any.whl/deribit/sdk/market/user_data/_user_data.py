from dataclasses import dataclass

from .my_trades import MyTrades
from .open_orders import OpenOrders
from .query_order import QueryOrder
from .balances import Balances
from .my_funding_history import MyFundingHistory

@dataclass
class UserData(MyTrades, OpenOrders, QueryOrder, Balances, MyFundingHistory):
  ...