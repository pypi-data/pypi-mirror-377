from typing_extensions import Literal, NamedTuple, overload
from decimal import Decimal
from dataclasses import dataclass

from deribit.core import ClientMixin, ApiResponse, validator, TypedDict, raise_on_error

class BookEntry(NamedTuple):
  price: Decimal
  amount: Decimal

State = Literal['open', 'closed']

class OrderBook(TypedDict):
  asks: list[BookEntry]
  bids: list[BookEntry]
  index_price: Decimal
  state: State

validate_response = validator(OrderBook)

@dataclass(frozen=True)
class GetOrderBook(ClientMixin):
  @overload
  async def get_order_book(
    self, instrument_name: str, *,
    depth: int | None = None,
    validate: bool = True,
    unsafe: Literal[False] = False,
  ) -> ApiResponse[OrderBook]:
    ...
  @overload
  async def get_order_book(
    self, instrument_name: str, *,
    depth: int | None = None,
    validate: bool = True,
    unsafe: Literal[True],
  ) -> OrderBook:
    ...
  async def get_order_book(
    self, instrument_name: str, *,
    depth: int | None = None,
    validate: bool = True,
    unsafe: bool = False,
  ) -> ApiResponse[OrderBook] | OrderBook:
    """Retrieves the order book for a given instrument.
    
    - `instrument_name`: The name of the instrument to get the order book for.
    - `depth`: The depth of the order book.
    - `validate`: Whether to validate the response against the expected schema.
    - `unsafe`: Whether to raise an exception in case of an error.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_order_book)
    """
    params: dict = {'instrument_name': instrument_name}
    if depth is not None:
      params['depth'] = depth
    r = await self.get('/public/get_order_book', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    
    return raise_on_error(r) if unsafe else r
