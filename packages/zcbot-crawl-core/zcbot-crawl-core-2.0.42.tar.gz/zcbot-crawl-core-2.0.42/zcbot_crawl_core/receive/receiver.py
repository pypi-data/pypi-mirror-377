# -*- coding: utf-8 -*-
import json
import logging
import threading
import time
import pika
import traceback
from pika.exceptions import StreamLostError
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Union, List
from .key_builder import get_rabbit_result_keys
from .model import RabbitMeta, RunMode
from .processor import AbstractMessageProcess
from ..util.decator import singleton

LOGGER = logging.getLogger(__name__)


class Rabbit(object):
    """
    通用Rabbit客户端
    """
    lock = threading.Lock()

    def __init__(self, connection_uri=None):
        self.connection_uri = connection_uri
        self.connection = pika.BlockingConnection(pika.URLParameters(self.connection_uri))
        self.default_channel = self.connection.channel()
        LOGGER.info(f'Rabbit初始化链路 connection_uri -> {self.connection_uri}')

    def ensure_channel(self, force: bool = False):
        """
        链路检查，确保链路通畅
        :return:
        """
        # 双重校验
        if force or not self.connection or self.connection.is_closed or not self.default_channel or self.default_channel.is_closed:
            try:
                self.lock.acquire(timeout=30)
                if force or not self.connection or self.connection.is_closed or not self.default_channel or self.default_channel.is_closed:
                    # 清理链路
                    if self.default_channel:
                        try:
                            self.default_channel.close()
                        except Exception as e:
                            LOGGER.error(e)
                    if self.connection:
                        try:
                            self.connection.close()
                        except Exception as e:
                            LOGGER.error(e)
                    # 重新建立链接
                    self.connection = pika.BlockingConnection(pika.URLParameters(self.connection_uri))
                    self.default_channel = self.connection.channel()
                    LOGGER.info(f'重建链路... -> {self.connection_uri}')
            finally:
                if self.lock.locked():
                    self.lock.release()

    def close(self):
        if self.default_channel and self.default_channel.is_open:
            try:
                self.default_channel.close()
            except Exception as e:
                LOGGER.error(e)
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception as e:
                LOGGER.error(e)

    # # 销毁关闭链接
    # def __del__(self):
    #     try:
    #         self.close()
    #     except Exception as e:
    #         LOGGER.error(e)


@singleton
class RabbitResultReceiver(Rabbit):
    """
    【单例】异步采集结果接收
    1、通道随批次创建，随采集完成自动销毁
    2、消息与队列自动创建自动删除
    3、通道按批次区分
    """
    declare_lock = threading.Lock()

    def __init__(self, processor: Union[AbstractMessageProcess, Callable], connection_uri: str, max_watcher_count: int = None, max_processor_count: int = None):
        super().__init__(connection_uri)
        # 默认值，和zcbot_spider保持一致
        _max_watcher_count = max_watcher_count or 2
        _max_processor_count = max_processor_count or 16

        self.processor = processor
        self.watcher_executor = ThreadPoolExecutor(max_workers=_max_watcher_count, thread_name_prefix='rabbit-watcher')
        self.processor_executor = ThreadPoolExecutor(max_workers=_max_processor_count, thread_name_prefix='rabbit-processor')
        # 路由映射
        self.queue_declared_filter = set()
        LOGGER.info(f'[队列]监听器初始化 connection_uri={self.connection_uri}')

    def watch(self, run_mode: RunMode, app_code: Union[str, List[str]]):
        # rabbit配置信息统一构建【批采+流采】
        if isinstance(app_code, str):
            # 单个应用监测
            rabbit_meta = get_rabbit_result_keys(run_mode, app_code=app_code)
            self.watcher_executor.submit(self._receive_message, rabbit_meta)
        elif isinstance(app_code, List):
            # 多应用监测
            for _app_code in app_code:
                rabbit_meta = get_rabbit_result_keys(run_mode, app_code=_app_code)
                self.watcher_executor.submit(self._receive_message, rabbit_meta)

    def ensure_declares(self, meta: RabbitMeta):
        # 链路检查
        self.ensure_channel()
        # 双重校验
        if meta.queue_key not in self.queue_declared_filter:
            try:
                self.declare_lock.acquire(timeout=15)
                if meta.queue_key not in self.queue_declared_filter:
                    # 初始化消息队列
                    # 定义交换机
                    self.default_channel.exchange_declare(exchange=meta.exchange_key, exchange_type=meta.exchange_type, durable=True)
                    # 定义消息队列
                    self.default_channel.queue_declare(queue=meta.queue_key, durable=True)
                    # 定义绑定关系（路由）
                    self.default_channel.queue_bind(queue=meta.queue_key, exchange=meta.exchange_key, routing_key=meta.routing_key)
                    # 避免重复初始化
                    self.queue_declared_filter.add(meta.queue_key)
                    LOGGER.info('===============================')
                    LOGGER.info(f'init exchange_key -> {meta.exchange_key}')
                    LOGGER.info(f'init rabbit_routing_key -> {meta.routing_key}')
                    LOGGER.info(f'init rabbit_queue -> {meta.queue_key}')
                    LOGGER.info('===============================')
            finally:
                if self.declare_lock.locked():
                    self.declare_lock.release()

    def _receive_message(self, rabbit_meta: RabbitMeta):
        """
        连接消息队列并启动消费，阻塞队列（需要独立线程运行或挂在后台任务运行）
        """
        LOGGER.info(f'[队列]开始接收')
        _process_func = self.processor
        if isinstance(self.processor, AbstractMessageProcess):
            _process_func = self.processor.process_message
        try:
            self.ensure_declares(rabbit_meta)
            # 接收
            for method, properties, body in self.default_channel.consume(rabbit_meta.queue_key, auto_ack=False):
                # 保持通道激活状态
                if not method or not properties or not properties.headers:
                    LOGGER.error(f'[队列]无效消息 method={method}, properties={properties}, body={body}')
                    continue
                # 消息解析并发处理
                msg_type = properties.headers.get('msg_type', None)
                msg_tag = properties.headers.get('msg_tag', None)
                body_json = json.loads(body.decode())
                self.processor_executor.submit(_process_func, msg_type, body_json, msg_tag)
                # 消息确认
                self.default_channel.basic_ack(method.delivery_tag)
        except (StreamLostError, ConnectionAbortedError):
            LOGGER.error(f'[队列]服务端关闭链接通道StreamLostError,ConnectionAbortedError -> 重连 {traceback.format_exc()}')
        except pika.exceptions.ConnectionClosedByBroker:
            LOGGER.error(f'[队列]链接关闭异常ConnectionClosedByBroker -> 重连 {traceback.format_exc()}')
        except pika.exceptions.AMQPChannelError:
            LOGGER.error(f'[队列]通道关闭异常AMQPChannelError -> 重连 {traceback.format_exc()}')
        except pika.exceptions.AMQPConnectionError:
            LOGGER.error(f'[队列]链接关闭异常AMQPConnectionError -> 重连 {traceback.format_exc()}')
        except Exception:
            LOGGER.error(f'[队列]接收过程异常 -> 重连 {traceback.format_exc()}')
        finally:
            try:
                # 清空队列定义过滤校验，防止断链后三要素丢失
                self.queue_declared_filter.clear()
                # 关闭链接和通道（链接关闭通道自动关闭）
                self.default_channel.close()
                self.connection.close()
                LOGGER.info(f'[队列]销毁队列')
            except Exception:
                LOGGER.error(f'[队列]关闭链接异常 {traceback.format_exc()}')

            # 递归重试
            time.sleep(10)
            LOGGER.warning(f'[队列]异常重试中...')
            self._receive_message(rabbit_meta)
