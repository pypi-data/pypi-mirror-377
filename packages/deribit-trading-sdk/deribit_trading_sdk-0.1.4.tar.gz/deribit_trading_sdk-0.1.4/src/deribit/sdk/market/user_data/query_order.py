from dataclasses import dataclass
from decimal import Decimal

from trading_sdk.types import ApiError
from trading_sdk.market.user_data.query_order import (
  SpotQueryOrder, PerpQueryOrder, InversePerpQueryOrder, OrderState
)

from deribit.core import timestamp as ts
from deribit.sdk.core import (
  SdkMixin, wrap_exceptions, parse_side, parse_status,
  spot_name, perp_name, inverse_perp_name
)

@dataclass
class QueryOrder(SpotQueryOrder, PerpQueryOrder, InversePerpQueryOrder, SdkMixin):
  @wrap_exceptions
  async def query_order(self, instrument: str, /, *, id: str) -> OrderState:
    r = await self.client.get_order_state(id)
    if not 'result' in r:
      raise ApiError(r)
    else:
      o = r['result']
      return OrderState(
        id=o['order_id'],
        price=Decimal(o['price']),
        qty=Decimal(o['amount']),
        filled_qty=Decimal(o['filled_amount']),
        time=ts.parse(o['creation_timestamp']),
        side=parse_side(o['direction']),
        status=parse_status(o),
      )

  async def spot_query_order(self, base: str, quote: str, /, *, id: str) -> OrderState:
    instrument = spot_name(base, quote)
    return await self.query_order(instrument, id=id)

  async def perp_query_order(self, base: str, quote: str, /, *, id: str) -> OrderState:
    instrument = perp_name(base, quote)
    return await self.query_order(instrument, id=id)

  async def inverse_perp_query_order(self, currency: str, /, *, id: str) -> OrderState:
    instrument = inverse_perp_name(currency)
    return await self.query_order(instrument, id=id)