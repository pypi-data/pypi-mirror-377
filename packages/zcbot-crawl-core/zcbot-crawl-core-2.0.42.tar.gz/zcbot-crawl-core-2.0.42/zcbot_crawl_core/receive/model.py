import time
from enum import Enum
from typing import Union, Dict, List, Any
from pydantic import BaseModel


class RunMode(Enum):
    # 批采
    BATCH = 'batch'
    # 流采
    STREAM = 'stream'


class RabbitMeta(BaseModel):
    """
    消息发布元数据
    """
    # 交换机键
    exchange_key: str = None
    # 交换机类型
    exchange_type: str = None
    # 绑定关系（路由）键
    routing_key: str = None
    # 队列名称
    queue_key: str = None

    def __init__(self, exchange_key: str, exchange_type: str, routing_key: str, queue_key: str = None, **data: Any):
        super().__init__(**data)
        self.exchange_key = exchange_key
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.queue_key = queue_key


class MsgType(Enum):
    """
    消息类型枚举
    """
    # 爬虫控制指令
    ACT_OPENED = 'OPENED'
    ACT_CLOSED = 'CLOSED'
    # 数据消息
    SKU_TEXT = 'SKU_TEXT'
    SKU_IMAGES = 'SKU_IMAGES'


class SignalType(Enum):
    """
    采云间爬虫状态信号枚举
    """
    OPENED = 'OPENED'
    CLOSED = 'CLOSED'


class BaseMsg(BaseModel):
    """
    标准消息数据模型
    """
    # 消息接收者应用编码
    app_code: str = None
    # 消息类型（控制消息：ACT；数据消息：DATA；流式数据消息：STREAM）
    msg_type: Union[str, MsgType]
    # 消息体
    msg_body: Union[str, Dict, List] = None
    # 产生时间戳
    gen_time: int = int(time.time())
