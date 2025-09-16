from typing_extensions import TypeVar, Literal, Any, Generic
from abc import ABC, abstractmethod
import asyncio
from functools import wraps
from dataclasses import dataclass, field
from datetime import timedelta
import logging
import websockets

from deribit.core import DERIBIT_MAINNET, path_join
from ..exc import NetworkError

T = TypeVar('T')
M = TypeVar('M', default=Any)
R = TypeVar('R', default=Any)

logger = logging.getLogger('deribit.core.ws')

@dataclass
class Context:
  ws: websockets.ClientConnection
  listener: asyncio.Task

@dataclass(kw_only=True)
class SocketClient(ABC):
  domain: str = DERIBIT_MAINNET
  path: str = '/ws/api/v2'
  timeout: timedelta = timedelta(seconds=10)
  ctx_future: asyncio.Future[Context] = field(default_factory=asyncio.Future, init=False)
  open_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  close_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  
  @property
  def url(self) -> str:
    return path_join(f'wss://{self.domain}', self.path)

  @property
  async def ctx(self) -> Context:
    return await self.open()
  
  @property
  async def ws(self) -> websockets.ClientConnection:
    return (await self.ctx).ws
  
  async def __aenter__(self):
    await self.open()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.close(await self.ctx, exc_type, exc_value, traceback)

  async def force_open(self):
    async def connect():
      try:
        return await websockets.connect(self.url, open_timeout=self.timeout.total_seconds())
      except websockets.exceptions.WebSocketException as e:
        raise NetworkError(f'Failed to connect to {self.url}') from e
      
    ws = await connect()
    logger.info('Connected!')
    return Context(
      ws=ws,
      listener=asyncio.create_task(self.listener(ws)),
    )
  
  async def open(self) -> Context:
    if self.open_lock.locked() or self.ctx_future.done():
      return await self.ctx_future

    async with self.open_lock:
      logger.info('Connecting...')
      ctx = await self.force_open()
      self.ctx_future.set_result(ctx)
      return ctx

  async def force_close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    ctx.listener.cancel()
    await ctx.ws.__aexit__(exc_type, exc_value, traceback)

  async def close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    if not self.close_lock.locked():
      async with self.close_lock:
        await self.force_close(ctx, exc_type, exc_value, traceback)


  async def listener(self, ws: websockets.ClientConnection, /):
    while True:
      try:
        msg = await ws.recv()
        logger.debug('Received: %s', msg)
        self.on_msg(msg)
      except websockets.exceptions.WebSocketException as e:
        logger.error('Error receiving message: %s', e)
        raise NetworkError('Error receiving message') from e

  @abstractmethod
  def on_msg(self, msg: str | bytes):
    ...

  async def wait_with_listener(self, fut: asyncio.Future[T]) -> T:
    """Wait for a future to complete, propagating any exceptions if the listener task fails or gets cancelled"""
    async def coro():
      return await fut
    ctx = await self.ctx
    task = asyncio.create_task(coro())
    done, _ = await asyncio.wait([task, ctx.listener], return_when='FIRST_COMPLETED')
    if ctx.listener in done:
      if (exc := ctx.listener.exception()) is not None:
        raise exc
      else:
        raise asyncio.CancelledError('Listener task got cancelled')
    return task.result()

class RpcSocketClient(SocketClient, Generic[M, R]):
  """Base request/response socket client."""
  @abstractmethod
  async def req(self, msg: M) -> R:
    ...
