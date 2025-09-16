from dataclasses import dataclass
from decimal import Decimal

from trading_sdk.market.user_data.open_orders import (
  SpotOpenOrders, PerpOpenOrders, InversePerpOpenOrders, OrderState
)

from deribit.core import timestamp as ts, ApiError
from deribit.sdk.core import (
  SdkMixin, wrap_exceptions, parse_side, parse_status,
  spot_name, perp_name, inverse_perp_name
)

@dataclass
class OpenOrders(SpotOpenOrders, PerpOpenOrders, InversePerpOpenOrders, SdkMixin):
  @wrap_exceptions
  async def open_orders(self, instrument: str, /) -> list[OrderState]:
    r = await self.client.get_open_orders_by_instrument(instrument)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      orders = r['result']
      return [
        OrderState(
          id=o['order_id'],
          price=Decimal(o['price']),
          qty=Decimal(o['amount']),
          filled_qty=Decimal(o['filled_amount']),
          time=ts.parse(o['creation_timestamp']),
          side=parse_side(o['direction']),
          status=parse_status(o)
        )
        for o in orders
      ]

  async def spot_open_orders(self, base: str, quote: str, /) -> list[OrderState]:
    instrument = spot_name(base, quote)
    return await self.open_orders(instrument)

  async def perp_open_orders(self, base: str, quote: str, /) -> list[OrderState]:
    instrument = perp_name(base, quote)
    return await self.open_orders(instrument)

  async def inverse_perp_open_orders(self, currency: str, /) -> list[OrderState]:
    instrument = inverse_perp_name(currency)
    return await self.open_orders(instrument)