from typing_extensions import Literal, overload, AsyncIterable
from dataclasses import dataclass

from deribit.core import SocketMixin, validator
from deribit.market_data.get_last_trades_by_instrument import Trade

validate_message = validator(list[Trade])

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo']

@dataclass(frozen=True)
class Trades(SocketMixin):
  @overload
  def trades(
    self, *, instrument_name: str,
    interval: Literal['raw', '100ms', 'agg2'] = '100ms',
    validate: bool = True,
  ) -> AsyncIterable[list[Trade]]:
    """Subscribe to trades in a given instrument.
    
    - `instrument_name`: The instrument name to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#trades-instrument_name-interval)
    """
    ...
  @overload
  def trades(
    self, *, kind: InstrumentKind,
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = '100ms',
    validate: bool = True,
  ) -> AsyncIterable[list[Trade]]:
    """Subscribe to trades in a given currency, optionally filtered by instrument kind.
    
    - `kind`: The instrument kind to subscribe to.
    - `currency`: The currency to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#trades-instrument_name-interval)
    """
  async def trades(
    self, *, instrument_name: str | None = None,
    kind: InstrumentKind | None = None,
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = '100ms',
    validate: bool = True,
  ) -> AsyncIterable[list[Trade]]:
    if instrument_name is not None:
      channel = f'trades.{instrument_name}.{interval}'
    elif kind is not None:
      channel = f'trades.{kind}.{currency}.{interval}'
    else:
      raise ValueError('Must provide either instrument_name or kind')
    
    async for msg in self.subscribe(channel):
      yield validate_message(msg) if self.validate(validate) else msg
  