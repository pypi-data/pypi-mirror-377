# -*- coding: utf-8 -*-
from typing import List
from ..model.base import Platforms
from ..util import logger
from ..dao import batch_spider_group as batch_spider_group_dao
from ..dao import auth_user_spider_group as auth_user_spider_group_dao
from ..dao import spider_group as spider_group_dao
from ..model.entity import BatchSpiderGroup

LOGGER = logger.get('批次爬虫组')


def get_spider_group_list(group_code: str = None, plat_codes: List[str] = None, enable: int = None):
    rows = spider_group_dao.get_spider_group_list(group_code=group_code, plat_codes=plat_codes, enable=enable)
    rows = [BatchSpiderGroup(**x) for x in rows]
    return rows


def get_spider_group(group_code: str = None, plat_code: str = None, enable: int = None, tenant_code: str = None):
    row = {}
    if tenant_code:
        row = auth_user_spider_group_dao.get_spider_group(tenant_code=tenant_code, group_code=group_code, plat_code=plat_code, enable=enable)
    if not row:
        row = spider_group_dao.get_spider_group(group_code=group_code, plat_code=plat_code, enable=enable)

    if not row:
        row = {}
    row = BatchSpiderGroup(**row)
    return row


def get_platforms_by_group(group_code: str, enable: int = None):
    rows = spider_group_dao.get_platforms_by_group_code(group_code=group_code, enable=enable)
    rows = [Platforms(**x) for x in rows]
    return rows
