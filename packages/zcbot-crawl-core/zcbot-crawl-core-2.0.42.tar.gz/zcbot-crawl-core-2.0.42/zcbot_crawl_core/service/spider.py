# -*- coding: utf-8 -*-
from typing import List
from ..util import logger
from ..dao import spider as spider_dao

LOGGER = logger.get('批次爬虫')


def get_spider(spider_id: str):
    row = spider_dao.get_spider(spider_id=spider_id)
    return row


def get_spiders_by_id(spider_ids: List[str]):
    spiders = spider_dao.get_spiders_by_id(spider_ids)
    return spiders
