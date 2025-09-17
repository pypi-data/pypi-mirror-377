from typing_extensions import Literal, NamedTuple, Awaitable, AsyncIterable, cast
from dataclasses import dataclass
from decimal import Decimal
import asyncio

from deribit.core import SocketMixin, validator, TypedDict

class BookEntryUpdate(NamedTuple):
  action: Literal['new', 'change', 'delete']
  price: Decimal
  amount: Decimal

class BookEntrySnapshot(NamedTuple):
  action: Literal['new']
  price: Decimal
  amount: Decimal

class BaseOrderBook(TypedDict):
  change_id: int
  instrument_name: str
  timestamp: int

class OrderBookSnapshot(BaseOrderBook):
  asks: list[BookEntrySnapshot]
  bids: list[BookEntrySnapshot]
  type: Literal['snapshot']

class OrderBookUpdate(BaseOrderBook):
  asks: list[BookEntryUpdate]
  bids: list[BookEntryUpdate]
  type: Literal['change']

validate_snapshot = validator(OrderBookSnapshot)
validate_update = validator(OrderBookUpdate)

@dataclass(frozen=True)
class DepthUpdates(SocketMixin):
  async def depth_updates(
    self, instrument_name: str, *,
    interval: Literal['100ms', 'agg2', 'raw'] = 'raw',
    validate: bool = True,
  ) -> tuple[Awaitable[OrderBookSnapshot], AsyncIterable[OrderBookUpdate]]:
    """Subscribes to changes to the order book for a certain instrument.
    
    - `instrument_name`: The instrument name to subscribe to.
    - `interval`: Frequency of notifications.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#book-instrument_name-interval)
    """
    channel = f'book.{instrument_name}.{interval}'
    
    snapshot = asyncio.Future[OrderBookSnapshot]()
    it = aiter(self.subscribe(channel))

    async def first():
      msg = await anext(it)
      if self.validate(validate):
        msg = validate_snapshot(msg)
      else:
        msg = cast(OrderBookSnapshot, msg)
      snapshot.set_result(msg)

    asyncio.create_task(first())

    async def gen():
      await snapshot
      while True:
        msg = await anext(it)
        if self.validate(validate):
          msg = validate_update(msg)
        else:
          msg = cast(OrderBookUpdate, msg)
        yield msg
    
    return snapshot, gen()
  