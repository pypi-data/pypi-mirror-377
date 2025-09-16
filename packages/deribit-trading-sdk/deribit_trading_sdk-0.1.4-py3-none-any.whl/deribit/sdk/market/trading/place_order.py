from dataclasses import dataclass

from trading_sdk.types import fmt_num, ApiError
from trading_sdk.market.trading.place_order import (
  SpotPlaceOrder, PerpPlaceOrder, InversePerpPlaceOrder, Order as OrderTDK
)

from deribit.trading.buy import Order, LimitOrder, MarketOrder
from deribit.sdk.core import SdkMixin, wrap_exceptions, spot_name, perp_name, inverse_perp_name

def parse_order(order: OrderTDK) -> Order:
  if order['type'] == 'LIMIT':
    return LimitOrder(
      type='limit',
      price=fmt_num(order['price']),
      amount=fmt_num(order['qty'])
    )
  elif order['type'] == 'MARKET':
    return MarketOrder(
      type='market',
      amount=fmt_num(order['qty'])
    )

@dataclass
class PlaceOrder(SpotPlaceOrder, PerpPlaceOrder, InversePerpPlaceOrder, SdkMixin):
  @wrap_exceptions
  async def place_order(self, instrument: str, /, *, order: OrderTDK) -> str:
    fn = self.client.buy if order['side'] == 'BUY' else self.client.sell
    r = await fn(instrument, parse_order(order))
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return r['result']['order']['order_id']

  async def spot_place_order(self, base: str, quote: str, /, *, order: OrderTDK) -> str:
    instrument = spot_name(base, quote)
    return await self.place_order(instrument, order=order)

  async def perp_place_order(self, base: str, quote: str, /, *, order: OrderTDK) -> str:
    instrument = perp_name(base, quote)
    return await self.place_order(instrument, order=order)

  async def inverse_perp_place_order(self, currency: str, /, *, order: OrderTDK) -> str:
    instrument = inverse_perp_name(currency)
    return await self.place_order(instrument, order=order)