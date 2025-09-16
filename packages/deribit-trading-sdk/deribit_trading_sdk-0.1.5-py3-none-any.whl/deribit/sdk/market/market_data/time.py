from dataclasses import dataclass

from trading_sdk.types import ApiError
from trading_sdk.market.market_data.time import Time as TimeTDK

from deribit.core import timestamp as ts
from deribit.sdk.core import SdkMixin, wrap_exceptions

@dataclass
class Time(TimeTDK, SdkMixin):
  @wrap_exceptions
  async def time(self):
    r = await self.client.get_time()
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return ts.parse(r['result'])
