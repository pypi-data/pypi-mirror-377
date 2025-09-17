from typing_extensions import Literal, AsyncIterable
from dataclasses import dataclass

from deribit.core import AuthedSocketMixin
from deribit.trading.get_order_state import OrderStatus, validate_response

@dataclass(frozen=True)
class UserOrders(AuthedSocketMixin):
  async def user_orders(
    self, instrument_name: str, *,
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> AsyncIterable[OrderStatus]:
    """Subscribe to order changes in a given instrument.
    
    - `instrument_name`: The instrument name to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#user-orders-instrument_name-raw)
    """
    channel = f'user.orders.{instrument_name}.{interval}'
    async for msg in self.subscribe(channel):
      yield validate_response(msg) if self.validate(validate) else msg
    