from dataclasses import dataclass
from .depth import Depth
from .instrument_info import InstrumentInfo
from .candles import Candles
from .time import Time

@dataclass
class MarketData(Depth, InstrumentInfo, Candles, Time):
  ...