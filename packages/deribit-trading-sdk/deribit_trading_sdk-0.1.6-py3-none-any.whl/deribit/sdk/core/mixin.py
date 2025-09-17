from dataclasses import dataclass
from typing import Literal

from deribit import Deribit

@dataclass
class SdkMixin:
  client: Deribit
  subaccount_id: str | None = None
  validate: bool = True

  @classmethod
  def new(
    cls, client_id: str | None = None, client_secret: str | None = None, *,
    mainnet: bool = True, protocol: Literal['ws', 'http'] = 'ws',
    subaccount_id: str | None = None, validate: bool = True
  ):
    client = Deribit.new(client_id=client_id, client_secret=client_secret, mainnet=mainnet, protocol=protocol)
    return cls(client=client, subaccount_id=subaccount_id, validate=validate)

  async def __aenter__(self):
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)