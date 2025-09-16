from dataclasses import dataclass
from decimal import Decimal

from trading_sdk.market.market_streams.depth import (
  SpotDepth, PerpDepth, InversePerpDepth, Book
)

from deribit.sdk.core import SdkMixin, wrap_exceptions, spot_name, perp_name, inverse_perp_name

@dataclass
class Depth(SpotDepth, PerpDepth, InversePerpDepth, SdkMixin):
  @wrap_exceptions
  async def depth(self, instrument: str, /, *, limit: int | None = None):
    stream = self.client.subscriptions.depth(instrument, depth=limit or 20)
    async for book in stream:
      yield Book(
        bids=[Book.Entry(price=Decimal(e.price), qty=Decimal(e.amount)) for e in book['bids']],
        asks=[Book.Entry(price=Decimal(e.price), qty=Decimal(e.amount)) for e in book['asks']]
      )

  async def spot_depth(self, base: str, quote: str, /, *, limit: int | None = None):
    instrument = spot_name(base, quote)
    async for book in self.depth(instrument, limit=limit):
      yield book

  async def perp_depth(self, base: str, quote: str, /, *, limit: int | None = None):
    instrument = perp_name(base, quote)
    async for book in self.depth(instrument, limit=limit):
      yield book

  async def inverse_perp_depth(self, currency: str, /, *, limit: int | None = None):
    instrument = inverse_perp_name(currency)
    async for book in self.depth(instrument, limit=limit):
      yield book