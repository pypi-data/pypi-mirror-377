from dataclasses import dataclass

from deribit.core import ClientMixin, ApiResponse, validator

validate_response = validator(int)

@dataclass(frozen=True)
class GetTime(ClientMixin):
  async def get_time(self, *, validate: bool = True) -> ApiResponse[int]:
    """Retrieves the current time (in milliseconds). This API endpoint can be used to check the clock skew between your software and Deribit's systems.
    
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#public-get_time)
    """
    r = await self.request('/public/get_time')
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  