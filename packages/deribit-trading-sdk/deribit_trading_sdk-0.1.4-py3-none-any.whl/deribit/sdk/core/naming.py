def spot_name(base: str, quote: str) -> str:
  return f'{base}_{quote}'

def perp_name(base: str, quote: str) -> str:
  return f'{base}_{quote}-PERPETUAL'

def inverse_perp_name(currency: str) -> str:
  return f'{currency}-PERPETUAL'
