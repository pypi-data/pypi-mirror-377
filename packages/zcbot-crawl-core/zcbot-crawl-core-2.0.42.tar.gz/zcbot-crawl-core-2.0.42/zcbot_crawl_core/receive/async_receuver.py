# encoding: utf-8
import asyncio
import json
import logging
import time
import traceback
import aio_pika
from typing import Union, Callable
from ..util.decator import singleton
from .processor import AbstractMessageProcess
from aio_pika.exceptions import CONNECTION_EXCEPTIONS, ConnectionClosed, ChannelClosed, AMQPConnectionError, AMQPChannelError


LOGGER = logging.getLogger(__name__)


class AsyncTimeoutLock:
    def __init__(self, loop=None):
        self._lock = asyncio.Lock(loop=loop)

    async def acquire(self, timeout=30):
        try:
            await asyncio.wait_for(self._lock.acquire(), timeout)
        except asyncio.TimeoutError as e:
            raise e

    async def release(self):
        """释放锁。"""
        self._lock.release()

    def locked(self):
        return self._lock.locked()


class AsyncRabbit(object):
    """
    通用异步Rabbit客户端
    """
    lock = AsyncTimeoutLock()

    def __init__(self, connection_uri=None):
        self.connection_uri = connection_uri
        self.connection = aio_pika.RobustConnection(connection_uri)
        self.default_channel = self.connection.channel()
        LOGGER.info(f'Rabbit初始化链路 connection_uri -> {self.connection_uri}')

    async def ensure_channel(self, force: bool = False):
        if force or not self.connection or self.connection.is_closed or not self.default_channel or self.default_channel.is_closed:
            try:
                await self.lock.acquire(timeout=30)
                if force or not self.connection or self.connection.is_closed or not self.default_channel or self.default_channel.is_closed:
                    # 清理链路
                    if self.default_channel:
                        try:
                            await self.default_channel.close()
                        except Exception as e:
                            LOGGER.error(e)
                    if self.connection:
                        try:
                            await self.connection.close()
                        except Exception as e:
                            LOGGER.error(e)
                    # 重新建立链接
                    self.connection = aio_pika.RobustConnection(self.connection_uri)
                    self.default_channel = self.connection.channel()
                    LOGGER.info(f'重建链路... -> {self.connection_uri}')

            except Exception as e:
                LOGGER.error(e)

            finally:
                if self.lock.locked():
                    await self.lock.release()


@singleton
class AsyncRabbitResultReceiver(AsyncRabbit):

    declare_lock = AsyncTimeoutLock()

    def __init__(self, processor: Union[AbstractMessageProcess, Callable]):
        super(AsyncRabbitResultReceiver, self).__init__()
