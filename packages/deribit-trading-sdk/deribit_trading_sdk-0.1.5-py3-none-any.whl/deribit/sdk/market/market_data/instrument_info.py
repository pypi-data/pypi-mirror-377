from dataclasses import dataclass

from trading_sdk.types import ApiError
from trading_sdk.market.market_data.instrument_info import (
  SpotInfo, PerpInfo, InversePerpInfo, Info
)

from deribit.sdk.core import SdkMixin, wrap_exceptions, spot_name, perp_name, inverse_perp_name

@dataclass
class InstrumentInfo(SpotInfo, PerpInfo, InversePerpInfo, SdkMixin):
  @wrap_exceptions
  async def instrument_info(self, instrument: str, /) -> Info:
    r = await self.client.get_instrument(instrument)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      info = r['result']
      return Info(
        tick_size=info['tick_size'],
        step_size=info['contract_size'],
        min_qty_=info['min_trade_amount']
      )

  async def spot_info(self, base: str, quote: str, /) -> Info:
    instrument = spot_name(base, quote)
    return await self.instrument_info(instrument)

  async def perp_info(self, base: str, quote: str, /) -> Info:
    instrument = perp_name(base, quote)
    return await self.instrument_info(instrument)

  async def inverse_perp_info(self, currency: str, /) -> Info:
    instrument = inverse_perp_name(currency)
    return await self.instrument_info(instrument)