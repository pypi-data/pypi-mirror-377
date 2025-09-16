from typing_extensions import AsyncIterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from trading_sdk.market.market_data.candles import SpotCandles, PerpCandles, InversePerpCandles, Candle

from deribit.core import timestamp as ts
from deribit.sdk.core import SdkMixin, wrap_exceptions, spot_name, perp_name, inverse_perp_name

@dataclass
class Candles(SpotCandles, PerpCandles, InversePerpCandles, SdkMixin):
  @wrap_exceptions
  async def candles(
    self, instrument: str, /, *,
    interval: timedelta,
    start: datetime, end: datetime,
    limit: int | None = None
  ) -> AsyncIterable[Sequence[Candle]]:
    mins = int(interval.total_seconds() // 60)
    async for c in self.client.get_tradingview_chart_data_paged(instrument, start=start, end=end, resolution=mins):
      yield [
        Candle(
          open=c['open'][i],
          high=c['high'][i],
          low=c['low'][i],
          close=c['close'][i],
          volume=c['volume'][i],
          time=ts.parse(c['ticks'][i]),
        )
        for i in range(len(c['open']))
      ]

  async def spot_candles(self, base: str, quote: str, /, *, interval: timedelta, start: datetime, end: datetime, limit: int | None = None) -> AsyncIterable[Sequence[Candle]]:
    instrument = spot_name(base, quote)
    async for c in self.candles(instrument, interval=interval, start=start, end=end, limit=limit):
      yield c

  async def perp_candles(self, base: str, quote: str, /, *, interval: timedelta, start: datetime, end: datetime, limit: int | None = None) -> AsyncIterable[Sequence[Candle]]:
    instrument = perp_name(base, quote)
    async for c in self.candles(instrument, interval=interval, start=start, end=end, limit=limit):
      yield c

  async def inverse_perp_candles(self, currency: str, /, *, interval: timedelta, start: datetime, end: datetime, limit: int | None = None) -> AsyncIterable[Sequence[Candle]]:
    instrument = inverse_perp_name(currency)
    async for c in self.candles(instrument, interval=interval, start=start, end=end, limit=limit):
      yield c