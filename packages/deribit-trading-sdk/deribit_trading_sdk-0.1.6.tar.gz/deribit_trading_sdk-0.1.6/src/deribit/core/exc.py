from typing_extensions import TypeVar

T = TypeVar('T')

class Error(Exception):
  ...

class NetworkError(Error):
  ...

class ValidationError(Error):
  ...

class UserError(Error):
  ...

class AuthError(Error):
  ...

class ApiError(Error):
  ...
