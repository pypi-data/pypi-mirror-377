# -*- coding: utf-8 -*-
import json
import random
import uuid
from typing import List, Dict
from zcbot_url_parser import parser as url_parser
from ..model.enums import CommonStatus, TaskMode
from ..util import logger, cfg
from ..util import time as time_lib
from ..util.exceptions import BizException
from ..client.redis_client import Redis
from ..util import redis_key as redis_key_util
from ..model.stream import StreamApiData, StreamTaskItem
from ..dao import spider as spider_dao
from ..dao.meta import create_pipeline, run_pipeline

LOGGER = logger.get('流采')


def publish(api_data: StreamApiData, attach_spiders_dict: Dict):
    """
    准备批次采集任务物料
    """
    # 如果上游传递则直接使用，否则本系统生成批次编号
    app_code = api_data.appCode
    task_items = api_data.taskItems or []
    spider_ids = api_data.spiderIds or []
    # 默认通用通道
    channel_code = api_data.channelCode or 'common'
    if not app_code:
        raise BizException(f'[分拣]app_code未指定 api_data={api_data}')
    if not task_items:
        raise BizException(f'[分拣]任务清单为空 api_data={api_data}')
    if not spider_ids:
        raise BizException(f'[分拣]未指定spider_ids api_data={api_data}')
    spider_ids_string = ",".join(spider_ids)
    LOGGER.info(f'[分拣]开始流采分拣 app_code={app_code}, spider_ids={spider_ids_string}, rows={len(task_items)}')

    # 物料分拣
    result_map, classify_result_list, classify_ignore_list = classify(api_data)
    # 初始化采集任务
    init_job(result_map, spider_ids, channel_code, attach_spiders_dict)
    LOGGER.info(f'[分拣]流采分拣完成 app_code={app_code}, spider_ids={spider_ids_string}, rows={len(task_items)}')

    return result_map, classify_result_list, classify_ignore_list


def classify(api_data: StreamApiData) -> (Dict[str, List[StreamTaskItem]], List[dict]):
    """
    任务分拣
    :param api_data: 待分拣任务清单，
    :return:
    """
    app_code = api_data.appCode
    todo_list = api_data.taskItems
    LOGGER.info('[分拣]开始流采分拣 total=%s' % len(todo_list))

    result_map = dict()
    classify_result_list = list()
    classify_ignore_list = list()
    for idx, row in enumerate(todo_list):
        plat_code = row.platCode
        # 如果有plat_code则不分拣(兼容购物党等平台)
        if not plat_code:
            # 解析链接组装任务
            url_model = url_parser.parse_url(row.url)
            if not url_model:
                LOGGER.warning(f'[分拣]未识别的流采任务 sn={row.sn} url={row.url}')
                classify_ignore_list.append(row)
                continue
            link_id, plat_code, plat_name, ec_sku_id = url_model.link_sn, url_model.plat_code, url_model.plat_name, url_model.ec_sku_id
            if link_id and plat_code and ec_sku_id:
                row.linkId = link_id
                row.platCode = plat_code
                row.platName = plat_name
                row.ecSkuId = ec_sku_id
            else:
                LOGGER.warning(f'[分拣]未识别的流采任务 url={row.url}, url_sn={link_id}, plat_code={plat_code}, ec_sku_id={ec_sku_id}')
                classify_ignore_list.append(row)
                continue
        # 额外字段
        row.appCode = row.appCode or app_code
        row.rowId = row.rowId or row.sn
        # 分拣
        if row.sn and plat_code:
            task_list = result_map.get(plat_code)
            if not task_list:
                task_list = list()
                result_map[plat_code] = task_list
            task_list.append(row)
            classify_result_list.append(row.to_classify_result())
    # 统计
    count_map = dict()
    for key in result_map.keys():
        count_map[key] = len(result_map.get(key))
    LOGGER.info('[分拣]流采分拣完成 %s' % count_map)

    return result_map, classify_result_list, classify_ignore_list


def init_job(result_map: Dict[str, List], spider_ids: List[str], channel_code: str, attach_spiders_dict: Dict) -> (Dict[str, List[StreamTaskItem]], List[dict], str):
    for spider_id in spider_ids:
        # 根据spider查询plat_code
        spider_conf = spider_dao.get_spider(spider_id, CommonStatus.ON)
        if not spider_conf:
            LOGGER.warning(BizException(f'[初始化队列]{spider_id}爬虫配置表zcbot_spider异常或不存在'))
            continue
        else:
            # 初始化队列
            plat_code = spider_conf.platCode
            task_items = result_map.get(plat_code)
            if task_items:
                for task_item in task_items:
                    callback = task_item.callback
                    if callback:
                        callback.update({"attachSpiders": attach_spiders_dict.get(spider_id)})
                    else:
                        callback = {"attachSpiders": attach_spiders_dict.get(spider_id)}
                    task_item.callback = callback
                LOGGER.info(f'[初始化队列]平台编码:{plat_code}开始初始化数据')
                redis_key = redis_key_util.get_stream_task_queue_key(spider_id=spider_id, channel_code=channel_code)
                plat_init_count = init_task_queue(redis_key, spider_conf, task_items)
                LOGGER.info(f'[发布]初始化流采队列 plat_code={plat_code}, plat_init_count={plat_init_count}')
            else:
                pass
                # LOGGER.warning(f'[初始化队列]平台编码:{plat_code}无初始化数据')


def init_task_queue(redis_key, spider_conf, rows):
    """
    初始化任务队列
    :param redis_key:
    :param spider_conf:
    :param rows:
    :return:
    """
    # 初始化队列
    task_mode = spider_conf.taskMode
    LOGGER.info(f'[队列]任务队列初始化开始 redis_key={redis_key}, task_mode={task_mode}')
    if task_mode and redis_key and task_mode == TaskMode.batch.value:
        # 批量模式（如：京东价格）
        batch_size = spider_conf.batchSize
        return _init_redis_batch(redis_key, rows, batch_size)
    else:
        # 单条采集模式
        return _init_redis(redis_key, rows)


def add_to_task_mapper(req_id, task_data, task_queue_key, pipe):
    """
    加入任务映射队列，用于重试任务源数据
    """
    _data = {
        'queue': task_queue_key,
        'source': task_data,
        'genTime': time_lib.current_timestamp10()
    }
    _expire_seconds = cfg.get_int('ZCBOT_CORE_REDIS_QUEUE_EXPIRE') or 12 * 3600
    pipe.set(redis_key_util.get_retry_request_source_key(req_id), json.dumps(_data), ex=_expire_seconds)


def _init_redis(redis_key, rows: List[StreamTaskItem]):
    rds = Redis()
    pipe = create_pipeline()
    for row in rows:
        req_id = str(uuid.uuid4())
        task = {
            'reqId': req_id,
            "sn": str(row.sn),
            "url": row.url,
            "platCode": row.platCode,
            "rowId": str(row.rowId),
            "appCode": row.appCode,
        }
        if row.callback:
            task["callback"] = row.callback
        if row.itemConfig:
            task["itemConfig"] = row.itemConfig

        # 任务入队
        pipe.lpush(redis_key, json.dumps(task))
        # 加入重试源数据集合
        add_to_task_mapper(req_id, task, redis_key, pipe)
    run_pipeline(pipe)
    count = rds.client.llen(redis_key)
    LOGGER.info(f'[队列]任务队列初始化完成 -> 单条模式 key={redis_key}, row={count}, count={len(rows)}')

    return count


def _init_redis_batch(redis_key, rows: List[StreamTaskItem], batch_size):
    _expire_seconds = cfg.get_int('ZCBOT_CORE_REDIS_QUEUE_EXPIRE') or 12 * 3600
    rds = Redis()
    batch_list = []
    random.shuffle(rows)
    pipe = create_pipeline()
    for row in rows:
        task = {
            "sn": str(row.sn),
            "url": row.url,
            "platCode": row.platCode,
            "rowId": str(row.rowId),
            "appCode": row.appCode,
            "callback": row.callback,
            "itemConfig": row.itemConfig
        }

        batch_list.append(task)
        if len(batch_list) >= batch_size:
            req_id = str(uuid.uuid4())
            batch_row_data = {
                'reqId': req_id,
                'data': batch_list
            }
            # 任务入队
            pipe.lpush(redis_key, json.dumps(batch_row_data))
            # 加入重试源数据集合
            add_to_task_mapper(req_id, batch_row_data, redis_key, pipe)
            batch_list = []
    if batch_list:
        req_id = str(uuid.uuid4())
        batch_row_data = {
            'reqId': req_id,
            'data': batch_list
        }
        # 任务入队
        pipe.lpush(redis_key, json.dumps(batch_row_data))
        # 加入重试源数据集合
        add_to_task_mapper(req_id, batch_row_data, redis_key, pipe)
    run_pipeline(pipe)
    count = rds.client.llen(redis_key)
    LOGGER.info(f'[队列]任务队列初始化完成 -> 批量模式 key={redis_key}, row={count}, count={len(rows)}')

    return len(rows)
