from dataclasses import dataclass, field
import asyncio
from uuid import uuid4
import hmac
import hashlib

from deribit.core import (
  TypedDict, timestamp,
  ApiResponse, validator,
  AuthedClient, AuthedClientMixin,
  DERIBIT_MAINNET, DERIBIT_TESTNET,
  ApiError, UserError, AuthError
)
from .client import SocketClient, SocketMixin, SubscribeResponse, validate_subscribe_response
from .base import Context, logger

def sign(data: bytes, *, secret: str):
  return hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()

def signature_data(*, ts: int, nonce: str):
  return f'{ts}\n{nonce}\n'.encode()

class AuthData(TypedDict):
  access_token: str
  expires_in: int
  refresh_token: str
  scope: str

@dataclass
class AuthContext:
  auth_data: AuthData
  refresher: asyncio.Task

AuthResponseT: type[AuthData] = AuthData # type: ignore
validate_auth_response = validator(AuthResponseT)

@dataclass
class AuthedSocketClient(SocketClient, AuthedClient):
  client_id: str
  client_secret: str = field(repr=False)
  auth_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  auth_future: asyncio.Future[AuthContext] = field(default_factory=asyncio.Future, init=False)

  @property
  async def auth(self) -> AuthContext:
    return await self.authenticate()

  @classmethod
  def new(cls, *, mainnet: bool = True, validate: bool = True):
    import os
    client_id = os.environ['DERIBIT_CLIENT_ID'] if mainnet else os.environ['TEST_DERIBIT_CLIENT_ID']
    client_secret = os.environ['DERIBIT_CLIENT_SECRET'] if mainnet else os.environ['TEST_DERIBIT_CLIENT_SECRET']
    return cls(
      client_id=client_id,
      client_secret=client_secret,
      validate=validate,
      domain=DERIBIT_MAINNET if mainnet else DERIBIT_TESTNET,
    )

  async def login(self):
    ts = timestamp.now()
    nonce = uuid4().hex
    signature = sign(signature_data(ts=ts, nonce=nonce), secret=self.client_secret)
    r = await self.request('/public/auth', {
      'grant_type': 'client_signature',
      'signature': signature,
      'timestamp': ts,
      'nonce': nonce,
      'client_id': self.client_id,
    })
    if 'error' in r:
      raise AuthError(r)
    else:
      resp: AuthData = validate_auth_response(r['result']) if self.validate else r['result']
      return resp

  async def force_authenticate(self):
    auth_data = await self.login()
    logger.info('Loging successful, token expires in %s seconds', auth_data['expires_in'])

    async def refresher(auth_data: AuthData):
      while True:
        await asyncio.sleep(auth_data['expires_in'] - 60)
        logger.info('Refreshing token')
        auth_data = await self.login()
        logger.info('Token refreshed successfully. New token expires in %s seconds', auth_data['expires_in'])

    return AuthContext(
      auth_data=auth_data,
      refresher=asyncio.create_task(refresher(auth_data)),
    )

  async def authenticate(self):
    if self.auth_lock.locked() or self.auth_future.done():
      return await self.auth_future

    async with self.auth_lock:
      auth = await self.force_authenticate()
      self.auth_future.set_result(auth)
      return auth
  
  async def authed_request(self, path: str, params=None) -> ApiResponse:
    auth = await self.auth
    r = await self.req({
      'jsonrpc': '2.0',
      'method': path,
      'params': params,
      'access_token': auth.auth_data['access_token'],
    })
    if 'error' in r and r['error']['code'] == 10028: # too many requests
      await asyncio.sleep(0.2)
      return await self.authed_request(path, params)
    else:
      return r
  
  async def req_subscription(self, channel: str):
    await self.authenticate()
    r = await self.request('/private/subscribe', {
      'channels': [channel],
    })
    msg: SubscribeResponse = validate_subscribe_response(r) if self.validate else r
    if not 'result' in msg:
      raise ApiError(msg['error'])
    elif not channel in msg['result']:
      raise UserError(f'Channel "{channel}" not found')
    
    return msg
  
  async def req_unsubscription(self, channel: str):
    await self.authenticate()
    return await self.request('/private/unsubscribe', {
      'channels': [channel],
    })


@dataclass(frozen=True)
class AuthedSocketMixin(SocketMixin, AuthedClientMixin):
  client: AuthedSocketClient

  async def subscribe(self, channel: str):
    async for msg in self.client.subscribe(channel):
      yield msg
