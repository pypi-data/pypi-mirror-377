from dataclasses import dataclass
from datetime import datetime
from trading_sdk.types import ApiError, UserError
from trading_sdk.wallet.withdrawal_methods import WithdrawalMethod, Network, WithdrawalMethods as WithdrawalMethodsTDK

from deribit.sdk.core import SdkMixin, wrap_exceptions

def currency_network(currency: str) -> Network:
  match currency:
    case 'XRP':
      return 'XRP'
    case 'BNB':
      return 'BSC'
    case 'BTC':
      return 'BTC'
    case 'SOL':
      return 'SOL'
    case _:
      return 'ETH'

@dataclass
class WithdrawalMethods(WithdrawalMethodsTDK, SdkMixin):
  @wrap_exceptions
  async def withdrawal_methods(self, asset: str):
    r = await self.client.get_currencies()
    if not 'result' in r:
      raise ApiError(r['error'])
    for c in r['result']:
      if c['currency'] == asset:
        return [WithdrawalMethod(
          network=currency_network(asset),
          fee=WithdrawalMethod.Fee(asset=asset, amount=fee) if (fee := c.get('withdrawal_fee')) else None,
        )]
    
    raise UserError(f'Currency {asset} not found')