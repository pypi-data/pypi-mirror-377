from dataclasses import dataclass
from decimal import Decimal

from trading_sdk.types import ApiError
from trading_sdk.market.trading.cancel_order import (
  SpotCancelOrder, PerpCancelOrder, InversePerpCancelOrder
)
from trading_sdk.market.user_data.query_order import OrderState

from deribit.core import timestamp as ts
from deribit.sdk.core import (
  SdkMixin, wrap_exceptions, parse_side, parse_status,
  spot_name, perp_name, inverse_perp_name
)

@dataclass
class CancelOrder(SpotCancelOrder, PerpCancelOrder, InversePerpCancelOrder, SdkMixin):
  @wrap_exceptions
  async def cancel_order(self, instrument: str, /, *, id: str) -> OrderState:
    r = await self.client.cancel(id)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      o = r['result']
      return OrderState(
        id=id,
        price=Decimal(o['price']),
        qty=Decimal(o['amount']),
        filled_qty=Decimal(o['filled_amount']),
        side=parse_side(o['direction']),
        time=ts.parse(o['last_update_timestamp']),
        status=parse_status(o)
      )

  async def spot_cancel_order(self, base: str, quote: str, /, *, id: str) -> OrderState:
    instrument = spot_name(base, quote)
    return await self.cancel_order(instrument, id=id)

  async def perp_cancel_order(self, base: str, quote: str, /, *, id: str) -> OrderState:
    instrument = perp_name(base, quote)
    return await self.cancel_order(instrument, id=id)

  async def inverse_perp_cancel_order(self, currency: str, /, *, id: str) -> OrderState:
    instrument = inverse_perp_name(currency)
    return await self.cancel_order(instrument, id=id)