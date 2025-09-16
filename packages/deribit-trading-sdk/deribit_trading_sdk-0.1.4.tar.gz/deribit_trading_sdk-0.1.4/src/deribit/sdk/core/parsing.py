from trading_sdk.types import Network, is_network, ApiError
from trading_sdk.market.user_data.query_order import Side as SideTDK, OrderStatus as OrderStatusTDK

from deribit.trading.get_order_state import OrderStatus, Direction

def parse_network(network: str) -> Network:
  if is_network(network):
    return network
  else:
    raise ApiError(f'Invalid network: {network}')

def parse_side(side: Direction) -> SideTDK:
  return 'BUY' if side == 'buy' else 'SELL'

def parse_status(order: OrderStatus) -> OrderStatusTDK:
  match order['order_state']:
    case 'open' if order['filled_amount'] > 0:
      return 'PARTIALLY_FILLED'
    case 'open':
      return 'NEW'
    case 'rejected':
      return 'CANCELED'
    case 'cancelled' if order['filled_amount'] > 0:
      return 'PARTIALLY_CANCELED'
    case 'cancelled':
      return 'CANCELED'
    case 'filled':
      return 'FILLED'
    case 'untriggered':
      return 'UNTRIGGERED'