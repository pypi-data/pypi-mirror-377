from typing_extensions import Sequence, AsyncIterable
from dataclasses import dataclass
from datetime import datetime

from trading_sdk.market.user_data.my_trades import (
  SpotMyTrades, PerpMyTrades, InversePerpMyTrades, Trade
)

from deribit.core import timestamp as ts
from deribit.sdk.core import (
  SdkMixin, wrap_exceptions, spot_name, perp_name, inverse_perp_name
)

@dataclass
class MyTrades(SpotMyTrades, PerpMyTrades, InversePerpMyTrades, SdkMixin):
  @wrap_exceptions
  async def my_trades(
    self, instrument: str, /, *,
    start: datetime | None = None, end: datetime | None = None
  ) -> AsyncIterable[Sequence[Trade]]:
    async for trades in self.client.get_user_trades_by_instrument_paged(instrument, start=start, end=end, historical=True, count=20):
      yield [
        Trade(
          id=t['trade_id'],
          price=t['price'],
          qty=t['amount'],
          time=ts.parse(t['timestamp']),
          side='SELL' if t['direction'] == 'sell' else 'BUY',
          maker=t['liquidity'] == 'M',
          fee=Trade.Fee(
            amount=t['fee'],
            asset=t['fee_currency']
          ) if ('fee' in t and 'fee_currency' in t) else None
        )
        for t in trades
      ]

  async def spot_my_trades(self, base: str, quote: str, /, *, start: datetime | None = None, end: datetime | None = None) -> AsyncIterable[Sequence[Trade]]:
    instrument = spot_name(base, quote)
    async for trades in self.my_trades(instrument, start=start, end=end):
      yield trades

  async def perp_my_trades(self, base: str, quote: str, /, *, start: datetime | None = None, end: datetime | None = None) -> AsyncIterable[Sequence[Trade]]:
    instrument = perp_name(base, quote)
    async for trades in self.my_trades(instrument, start=start, end=end):
      yield trades

  async def inverse_perp_my_trades(self, currency: str, /, *, start: datetime | None = None, end: datetime | None = None) -> AsyncIterable[Sequence[Trade]]:
    instrument = inverse_perp_name(currency)
    async for trades in self.my_trades(instrument, start=start, end=end):
      yield trades