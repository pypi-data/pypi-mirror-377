from typing_extensions import NotRequired
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import ClientMixin, ApiResponse, validator, TypedDict

class Stats(TypedDict):
  high: Decimal | None
  """Highest 24h price"""
  low: Decimal | None
  """Lowest 24h price"""
  price_change: Decimal | None
  """24h price change percentage (not if no trades happened)"""
  volume: Decimal
  """24h volume"""

class BaseTicker(TypedDict):
  best_ask_amount: Decimal
  best_ask_price: Decimal
  best_bid_amount: Decimal
  best_bid_price: Decimal
  instrument_name: str
  last_price: Decimal
  mark_price: Decimal
  max_price: NotRequired[Decimal]
  min_price: NotRequired[Decimal]
  stats: Stats
  timestamp: int

class Greeks(TypedDict):
  delta: Decimal
  gamma: Decimal
  rho: Decimal
  theta: Decimal
  vega: Decimal

class OptionTicker(BaseTicker):
  ask_iv: Decimal
  bid_iv: Decimal
  greeks: Greeks
  mark_iv: Decimal
  underlying_index: Decimal
  underlying_price: Decimal

class PerpTicker(BaseTicker):
  current_funding: Decimal
  funding_8h: Decimal

Ticker = OptionTicker | PerpTicker | BaseTicker

TickerT: type[Ticker] = Ticker # type: ignore
validate_response = validator(TickerT)

@dataclass(frozen=True)
class GetTicker(ClientMixin):
  async def ticker(
    self, instrument_name: str, *,
    validate: bool = True
  ) -> ApiResponse[Ticker]:
    """Get an instrument's ticker.
    
    - `instrument_name`: The name of the instrument to get the ticker for.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-ticker)
    """
    r = await self.get('/public/ticker', {
      'instrument_name': instrument_name,
    })
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    