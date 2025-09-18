# -*- coding: UTF-8 -*-


# 【批采】采集任务队列
def get_batch_task_queue_key(batch_id: str, spider_id: str):
    return f'zcbot:batch:{batch_id}:{spider_id}'


# 【流采】采集任务队列
def get_stream_task_queue_key(spider_id: str, channel_code: str):
    return f'zcbot:stream:{spider_id}:{channel_code}'


# # 采集任务队列
# def get_task_queue_key_for_remove(batch_id: str):
#     return f'zcbot:{batch_id}:*'


# 【重试】采集重试任务源数据映射
def get_retry_request_source_key(req_id: str):
    return f'zcbot:retry:source:{req_id}'


# 测试
if __name__ == '__main__':
    pass
