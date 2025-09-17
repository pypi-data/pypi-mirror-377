from typing_extensions import Sequence, AsyncIterable
from dataclasses import dataclass
from datetime import datetime

from trading_sdk.types import ApiError, UserError
from trading_sdk.market.user_data.my_funding_history import (
  PerpMyFundingHistory, InversePerpMyFundingHistory, Funding
)

from deribit.core import timestamp as ts
from deribit.sdk.core import (
  SdkMixin, wrap_exceptions, perp_name, inverse_perp_name
)
from deribit.account.get_transaction_log import is_settlement

@dataclass
class MyFundingHistory(PerpMyFundingHistory, InversePerpMyFundingHistory, SdkMixin):
  @wrap_exceptions
  async def my_funding_history(
    self, instrument: str, /, *,
    start: datetime, end: datetime
  ) -> AsyncIterable[Sequence[Funding]]:
    r = await self.client.get_instrument(instrument)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      info = r['result']
    if info['kind'] != 'future':
      raise UserError(f'Instrument {instrument} is not a perpetual instrument')

    currency = info['settlement_currency']
    async for logs in self.client.get_transaction_log_paged(currency, start=start, end=end, query='settlement'):
      chunk = [
        Funding(
          funding=log['interest_pl'],
          time=ts.parse(log['timestamp']),
          side='SHORT' if log['side'] == 'short' else 'LONG'
        )
        for log in logs
          if is_settlement(log) and log['instrument_name'] == instrument
      ]
      if chunk:
        yield chunk

  async def perp_my_funding_history(
    self, base: str, quote: str, /, *,
    start: datetime, end: datetime
  ) -> AsyncIterable[Sequence[Funding]]:
    instrument = perp_name(base, quote)
    async for funding in self.my_funding_history(instrument, start=start, end=end):
      yield funding

  async def inverse_perp_my_funding_history(
    self, currency: str, /, *,
    start: datetime, end: datetime
  ) -> AsyncIterable[Sequence[Funding]]:
    instrument = inverse_perp_name(currency)
    async for funding in self.my_funding_history(instrument, start=start, end=end):
      yield funding