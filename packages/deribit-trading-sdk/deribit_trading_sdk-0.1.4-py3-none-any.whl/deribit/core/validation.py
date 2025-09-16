from typing_extensions import TypeVar, Generic, Any, is_typeddict, TypedDict as _TypedDict
from pydantic import TypeAdapter, ConfigDict, with_config
from dataclasses import is_dataclass
from .exc import ValidationError

T = TypeVar('T')

@with_config(ConfigDict(extra='allow'))
class TypedDict(_TypedDict):
  ...

class validator(Generic[T]):

  def __init__(self, Type: type[T]):
    is_record = is_dataclass(Type) or is_typeddict(Type)
    if is_record and not hasattr(Type, '__pydantic_config__'):
      setattr(Type, '__pydantic_config__', ConfigDict(extra='allow'))
    self.adapter = TypeAdapter(Type)
    
  def json(self, data: str | bytes | bytearray) -> T:
    from pydantic import ValidationError as PydanticValidationError
    try:
      return self.adapter.validate_json(data)
    except PydanticValidationError as e:
      raise ValidationError from e

  def python(self, data: Any) -> T:
    from pydantic import ValidationError as PydanticValidationError
    try:
      return self.adapter.validate_python(data)
    except PydanticValidationError as e:
      raise ValidationError from e
    
  def __call__(self, data) -> T:
    if isinstance(data, str | bytes | bytearray):
      return self.json(data)
    else:
      return self.python(data)
