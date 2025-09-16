from dataclasses import dataclass

from .get_time import GetTime

@dataclass(frozen=True)
class Supporting(
  GetTime,
):
  ...