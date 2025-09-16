from typing_extensions import Literal, AsyncIterable
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from deribit.core import TypedDict, ClientMixin, ApiResponse, validator, timestamp as ts, ApiError

class Candles(TypedDict):
  close: list[Decimal]
  high: list[Decimal]
  low: list[Decimal]
  open: list[Decimal]
  volume: list[Decimal]
  ticks: list[int]
  """Millisecond timestamps"""
  status: Literal['ok', 'no_data']

validate_response = validator(Candles)

@dataclass(frozen=True)
class GetTradingviewChartData(ClientMixin):
  async def get_tradingview_chart_data(
    self, instrument_name: str, *,
    start: datetime, end: datetime,
    resolution: str | int,
    validate: bool = True
  ) -> ApiResponse[Candles]:
    """Get a given index price.
    
    - `instrument_name`: The name of the instrument to get the index price for. See available indices in the [docs](https://docs.deribit.com/#public-get_index_price).
    - `start`: The start timestamp to get the chart data for.
    - `end`: The end timestamp to get the chart data for.
    - `resolution`: The resolution to get the chart data for. Can be an integer (number of minutes) or keyword (e.g. `1D`)
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_tradingview_chart_data)
    """
    r = await self.get('/public/get_tradingview_chart_data', {
      'instrument_name': instrument_name,
      'start_timestamp': ts.dump(start),
      'end_timestamp': ts.dump(end),
      'resolution': resolution,
    })
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  
  async def get_tradingview_chart_data_paged(
    self, instrument_name: str, *,
    start: datetime, end: datetime,
    resolution: str | int,
    validate: bool = True
  ) -> AsyncIterable[Candles]:
    end_time = ts.dump(end)
    while True:
      r = await self.get_tradingview_chart_data(instrument_name, start=start, end=ts.parse(end_time), resolution=resolution, validate=validate)
      if not 'result' in r:
        raise ApiError(r['error'])
      c = r['result']
      out = Candles(
        close=[],
        high=[],
        low=[],
        open=[],
        volume=[],
        ticks=[],
        status=c['status'],
      )
      for i in range(len(c['close'])):
        if c['ticks'][i] < end_time:
          out['close'].append(c['close'][i])
          out['high'].append(c['high'][i])
          out['low'].append(c['low'][i])
          out['open'].append(c['open'][i])
          out['volume'].append(c['volume'][i])
          out['ticks'].append(c['ticks'][i])
      if len(out['ticks']) == 0:
        break
      out['close'].reverse()
      out['high'].reverse()
      out['low'].reverse()
      out['open'].reverse()
      out['volume'].reverse()
      out['ticks'].reverse()
      yield out
      end_time = min(out['ticks'])
    