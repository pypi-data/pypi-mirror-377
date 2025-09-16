from typing_extensions import Literal, overload, AsyncIterable
from dataclasses import dataclass

from deribit.core import AuthedSocketMixin, validator, UserError
from deribit.trading.get_user_trades_by_currency import Trade

validate_message = validator(list[Trade])

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo', 'combo', 'any']

@dataclass(frozen=True)
class UserTrades(AuthedSocketMixin):
  @overload
  def user_trades(
    self, *, instrument_name: str,
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> AsyncIterable[list[Trade]]:
    """Subscribe to user trades in a given instrument.
    
    - `instrument_name`: The instrument name to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#user-trades-instrument_name-interval)
    """
    ...
  @overload
  def user_trades(
    self, *, kind: InstrumentKind = 'any',
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> AsyncIterable[list[Trade]]:
    """Subscribe to user trades in a given currency, optionally filtered by instrument kind.
    
    - `kind`: The instrument kind to subscribe to.
    - `currency`: The currency to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#user-trades-kind-currency-interval)
    """
  async def user_trades(
    self, *, instrument_name: str | None = None,
    kind: InstrumentKind = 'any',
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> AsyncIterable[list[Trade]]:
    if instrument_name is not None:
      channel = f'user.trades.{instrument_name}.{interval}'
    elif kind is not None:
      channel = f'user.trades.{kind}.{currency}.{interval}'
    else:
      raise UserError('Must provide either instrument_name or kind')

    async for msg in self.subscribe(channel):
      yield validate_message(msg) if self.validate(validate) else msg
