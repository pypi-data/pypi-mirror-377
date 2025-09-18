# -*- coding: utf-8 -*-
import logging
import threading
import traceback
from typing import Union, Dict, List
from .model import MsgType

LOGGER = logging.getLogger(__name__)


class AbstractMessageProcess(object):
    """
    抽象消息处理器
    """

    # 消息处理入口
    def process_message(self, msg_type: str, msg_data: Union[Dict, List] = None, msg_tag: str = None):
        try:
            if msg_type == MsgType.SKU_TEXT.name:
                self.process_sku_text(msg_data=msg_data, msg_tag=msg_tag)
            elif msg_type == MsgType.SKU_IMAGES.name:
                self.process_sku_images(msg_data=msg_data, msg_tag=msg_tag)
            elif msg_type == MsgType.ACT_OPENED.name:
                self.process_opened_action(msg_data=msg_data, msg_tag=msg_tag)
            elif msg_type == MsgType.ACT_CLOSED.name:
                self.process_closed_action(msg_data=msg_data, msg_tag=msg_tag)
            else:
                self.process_others(msg_data=msg_data, msg_type=msg_type, msg_tag=msg_tag)
        except Exception:
            LOGGER.error(f'[流采消息]解析异常 {traceback.format_exc()}')
            LOGGER.error(f'[流采消息]解析异常 msg_data={msg_data}, except={traceback.format_exc()}')

    def process_sku_text(self, msg_data: Union[Dict, List], msg_tag: str):
        LOGGER.warning(f'[{threading.current_thread().name}]process: msg_type=process_sku_text, msg_data={msg_data}, msg_tag={msg_tag}')

    def process_sku_images(self, msg_data: Union[Dict, List], msg_tag: str):
        LOGGER.warning(f'[{threading.current_thread().name}]process: msg_type=process_sku_images, msg_data={msg_data}, msg_tag={msg_tag}')

    def process_opened_action(self, msg_data: Union[Dict, List], msg_tag: str):
        LOGGER.warning(f'[{threading.current_thread().name}]process: msg_type=process_opened_action, msg_data={msg_data}, msg_tag={msg_tag}')

    def process_closed_action(self, msg_data: Union[Dict, List], msg_tag: str):
        LOGGER.warning(f'[{threading.current_thread().name}]process: msg_type=process_closed_action, msg_data={msg_data}, msg_tag={msg_tag}')

    def process_others(self, msg_data: Union[Dict, List], msg_type: str, msg_tag: str):
        LOGGER.error(f'[流采消息]未知类型消息 msg_type={msg_type}, msg_data={msg_data}, msg_tag={msg_tag}')
