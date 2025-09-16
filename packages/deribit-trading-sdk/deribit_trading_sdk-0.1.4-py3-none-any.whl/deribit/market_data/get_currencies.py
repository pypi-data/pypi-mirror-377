from typing_extensions import NotRequired, Literal, overload
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import ClientMixin, ApiResponse, validator, TypedDict, raise_on_error

class WithdrawalPriority(TypedDict):
  name: str
  value: Decimal

class Currency(TypedDict):
  apr: NotRequired[Decimal]
  coin_type: str
  currency: str
  currency_long: str
  fee_precision: int
  in_cross_collateral_pool: NotRequired[bool]
  min_confirmations: NotRequired[int]
  min_withdrawal_fee: NotRequired[Decimal]
  withdrawal_fee: NotRequired[Decimal]
  withdrawal_priorities: NotRequired[list[WithdrawalPriority]]

validate_response = validator(list[Currency])

@dataclass(frozen=True)
class GetCurrencies(ClientMixin):
  @overload
  async def get_currencies(
    self, *, validate: bool = True,
    unsafe: Literal[False] = False
  ) -> ApiResponse[list[Currency]]:
    ...
  @overload
  async def get_currencies(
    self, *, validate: bool = True,
    unsafe: Literal[True]
  ) -> list[Currency]:
    ...
  async def get_currencies(
    self, *, validate: bool = True,
    unsafe: bool = False,
  ) -> ApiResponse[list[Currency]] | list[Currency]:
    """Retrieves all cryptocurrencies supported by the API.
    
    - `validate`: Whether to validate the response against the expected schema.
    - `unsafe`: Whether to raise an exception in case of an error.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_currencies)
    """
    r = await self.get('/public/get_currencies')
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return raise_on_error(r) if unsafe else r
    