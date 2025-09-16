from dataclasses import dataclass
from decimal import Decimal

from trading_sdk.types import ApiError
from trading_sdk.market.market_data.depth import SpotDepth, PerpDepth, InversePerpDepth, Book

from deribit.sdk.core import SdkMixin, wrap_exceptions, spot_name, perp_name, inverse_perp_name

@dataclass
class Depth(SpotDepth, PerpDepth, InversePerpDepth, SdkMixin):
  @wrap_exceptions
  async def depth(self, instrument: str, /, *, limit: int | None = None) -> Book:
    r = await self.client.get_order_book(instrument, depth=limit)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return Book(
        asks=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.amount)
        ) for p in r['result']['asks'][:limit]],
        bids=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.amount)
        ) for p in r['result']['bids'][:limit]],
      )

  async def spot_depth(self, base: str, quote: str, /, *, limit: int | None = None) -> Book:
    instrument = spot_name(base, quote)
    return await self.depth(instrument, limit=limit)

  async def perp_depth(self, base: str, quote: str, /, *, limit: int | None = None) -> Book:
    instrument = perp_name(base, quote)
    return await self.depth(instrument, limit=limit)

  async def inverse_perp_depth(self, currency: str, /, *, limit: int | None = None) -> Book:
    instrument = inverse_perp_name(currency)
    return await self.depth(instrument, limit=limit)