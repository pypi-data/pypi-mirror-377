# -*- coding: utf-8 -*-

from typing import List, Dict, Optional
from ..model.enums import CommonStatus, StreamSpiderGroupType
from ..model.entity import StreamSpiderGroup, StreamSpider
from ..dao import stream_spider_group as stream_spider_group_dao


def get_all_stream_spider_groups() -> List[Dict[str, str]]:
    """
    获取所有的爬虫组
    """

    return StreamSpiderGroupType.to_list()


def get_group(group_code: str, status: str = CommonStatus.ON.name) -> StreamSpiderGroup:
    """
    根据一个爬虫组编码，获取里面所有的爬虫
    """
    row = stream_spider_group_dao.get_spider_group(group_code=group_code, status=status)
    row = StreamSpiderGroup(**row)

    return row


def get_spider(spider_id: str, status: str = CommonStatus.ON.name) -> Optional[StreamSpider]:
    """
    获取爬虫详情
    """

    stream_spider = stream_spider_group_dao.get_spider_by_spider_id(spider_id=spider_id, status=status)

    return stream_spider


def get_spiders(group_code: str, plat_code: str, status: str = CommonStatus.ON.name) -> List[StreamSpider]:
    """
    通过爬虫组编号以及平台，获取对应的爬虫，返回空列表或者是对应列表
    """
    stream_spider_groups = get_groups(group_code=group_code, status=status)
    plat_spider_ids = []
    for spider_group in stream_spider_groups:
        for spider in spider_group.spiders:
            if spider.platCode == plat_code and spider.status == status:
                plat_spider_ids.append(spider.spiderId)

    stream_spiders = stream_spider_group_dao.get_spider_list(spider_ids=plat_spider_ids, status=status)

    return stream_spiders
