from typing_extensions import TypedDict, Literal, AsyncIterable, TypeVar, Generic, Any
from abc import abstractmethod
from dataclasses import dataclass, field
from collections import defaultdict
import asyncio

from .base import RpcSocketClient

M = TypeVar('M', default=Any)
R = TypeVar('R', default=Any)
S = TypeVar('S', default=Any)

class Response(TypedDict, Generic[R]):
  kind: Literal['response']
  id: int
  response: R

class Subscription(TypedDict, Generic[S]):
  kind: Literal['subscription']
  channel: str
  data: S

Message = Response[R] | Subscription[S]

@dataclass
class MultiplexStreamsRPCSocketClient(RpcSocketClient[M, R], Generic[M, R, S]):
  """Multiplexed request/response and streams socket client. It uses IDs to identify requests and responses. It also supports subscription to multiple channels."""
  replies: dict[int, asyncio.Future[R]] = field(default_factory=dict, init=False, repr=False)
  counter: int = field(default=0, init=False, repr=False)
  subscribers: dict[str, list[asyncio.Queue[S]]] = field(default_factory=lambda: defaultdict(list), init=False, repr=False)

  async def req(self, msg: M) -> R:
    id = self.counter
    self.counter += 1
    while True:
      self.replies[id] = asyncio.Future()
      await self.send(id, msg)
      res = await self.wait_with_listener(self.replies[id])
      del self.replies[id]
      return res
    
  @abstractmethod
  async def req_subscription(self, channel: str) -> Any:
    ...

  @abstractmethod
  async def req_unsubscription(self, channel: str) -> Any:
    ...

  @abstractmethod
  def parse_msg(self, msg: str | bytes) -> Message[R, S]:
    ...

  def on_msg(self, msg: str | bytes):
    res = self.parse_msg(msg)
    if res['kind'] == 'response':
      self.replies[res['id']].set_result(res['response']) # type: ignore
    else:
      for q in self.subscribers[res['channel']]:
        q.put_nowait(res['data']) # type: ignore

  @abstractmethod
  async def send(self, id: int, msg: M):
    ...

  async def subscribe(self, channel: str) -> AsyncIterable[S]:
    q = asyncio.Queue()
    self.subscribers[channel].append(q)
    await self.req_subscription(channel)
    while True:
      yield await self.wait_with_listener(asyncio.create_task(q.get()))

  async def unsubscribe(self, channel: str, queue: asyncio.Queue[S] | None = None):
    if queue is not None:
      self.subscribers[channel].remove(queue)
    if not self.subscribers[channel]:
      del self.subscribers[channel]
    await self.req_unsubscription(channel)
