from pika.exchange_type import ExchangeType
from .model import RabbitMeta, RunMode


# rabbit配置信息统一定义（同spider中配置一致）
def get_rabbit_result_keys(run_mode: RunMode, app_code: str) -> RabbitMeta:
    if run_mode == RunMode.BATCH:
        # 批采
        exchange_key = f'zcbot.batch_result'
        exchange_type = ExchangeType.topic
        routing_key = f'zcbot.batch_result.{app_code}'
        queue_key = f'zcbot.batch_result.{app_code}'
        return RabbitMeta(exchange_key, exchange_type, routing_key, queue_key)
    elif run_mode == RunMode.STREAM:
        # 流采
        exchange_key = f'zcbot.stream_result'
        exchange_type = ExchangeType.topic
        routing_key = f'zcbot.stream_result.{app_code}'
        queue_key = f'zcbot.stream_result.{app_code}'
        return RabbitMeta(exchange_key, exchange_type, routing_key, queue_key)
    else:
        # 死信队列
        exchange_key = f'zcbot.dead_result'
        exchange_type = ExchangeType.topic
        routing_key = f'zcbot.dead_result.dead_routing'
        queue_key = f'zcbot.dead_result.dead_queue'
        return RabbitMeta(exchange_key, exchange_type, routing_key, queue_key)
