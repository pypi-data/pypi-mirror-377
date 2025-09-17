import json
import logging
import os
import traceback
from logging.handlers import TimedRotatingFileHandler

import pytz
import redis
from kafka import KafkaProducer
from redis.cluster import ClusterNode, RedisCluster
from requests.exceptions import ProxyError
from requests.exceptions import ReadTimeout
from wake.models import *
from wake.utils import CustomJSONEncoder
from wake import LoggerCollector
from wake import LoggerInterface
from wake import LoggerItem
from wake import LoggerStrategy
from wake.logger_conf import LOG_CONSUMER_KEY, LOG_VERSION, LOG_ENABLE, KAFKA_BOOTSTRAP, LOGGER_PATH, LOG_TYPE, \
    REDIS_CONF
from wake.logger_conf import ip_address

east_8 = pytz.timezone('Asia/Shanghai')
utc_tz = pytz.timezone('UTC')

LOG_CONF = {
    "level": "DEBUG",
    "dir": LOGGER_PATH,
    "rotation": "00:00",
    "retention": "1 week",
}
WORKER = {
    "id": ip_address if not os.environ.get("MY_POD_NAME") else os.environ.get("MY_POD_NAME"),
    "host": ip_address
}

KAFKA_CONF = {
    'bootstrap.servers': KAFKA_BOOTSTRAP,  # Kafka服务器地址
    "batch.size": 16384,  # 控制批处理大小
    "linger.ms": 5,  # 控制批处理等待时间
    "compression.type": "snappy",  # 启用压缩，减少网络传输和存储需求
    "retries": 2,  # 重试次数
    "retry.backoff.ms": 100,  # 重试间隔
    'max_block_ms': 120000,
}

# 是否为调试模式
log_debug: bool = LOG_CONF["level"] == "DEBUG"


# 定义一个函数，该函数将在线程中运行并发送消息
# def produce_messages(topic, message):
#     with producer_lock:  # 使用锁来同步对 producer 的访问
#         producer.send(topic, message)
#         producer.flush()


def get_crawler_logger(logger_name: str = "wake"):
    # 如果日志目录不存在，则创建
    if not os.path.exists(LOGGER_PATH):
        os.makedirs(LOGGER_PATH, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # 设置记录器的全局级别

    # 设置 INFO 级别的文件处理器
    info_handler = TimedRotatingFileHandler(os.path.join(LOGGER_PATH, f'{logger_name}.log'),
                                            when='midnight', interval=1, backupCount=7)

    info_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %('
                                       'message)s')
    info_handler.setFormatter(info_formatter)

    # 设置 ERROR 级别的文件处理

    # 避免多次添加处理器
    if not logger.handlers:
        logger.addHandler(info_handler)

    return logger


# 创建 logger 实例
logger = get_crawler_logger('wake')


class QuickCrawlerLogItem(LoggerItem):
    def __init__(self,
                 sid: str = "",
                 appid: str = "",
                 url: str = "",
                 typo: str = "",
                 domain: str = "",
                 action: str = "",
                 method: str = "",
                 status: str = "",
                 timestamps=None,
                 logs=None,
                 tags=None,
                 retries: int = 0,
                 resp: Resp = None):
        self.sid = sid
        self.appid = appid
        self.url = url
        self.domain = domain
        self.retries = retries
        if not resp:
            resp = Resp.from_dict({})
        self.resp = resp
        self.executor = Executor.from_dict(WORKER)
        self.version = LOG_VERSION
        self.type = typo
        super().__init__(action, method, status, timestamps, logs, tags)

    @classmethod
    def from_dict(cls, data):
        return cls(
            sid=data.get("sid", ""),
            appid=data.get("appid", "dataapi"),
            url=data.get("url", ""),
            typo=data.get("type", ""),
            domain=data.get("domain", ""),
            action=data.get("action", ""),
            method=data.get("method", ""),
            status=data.get("status", ""),
            timestamps=data.get("timestamps", {}),
            logs=data.get("logs", []),
            tags=data.get("tags", {}),
            retries=data.get("retries", 0),
            resp=data.get("resp", {})
        )


class QuickLoggerInterface(LoggerInterface):
    def __init__(self):
        super().__init__()

    def info(self, message):
        _message = str(message)
        _message = _message.replace("\n", "\\n")
        self.item.log(_message)


def delivery_report(err, msg):
    if err is not None:
        logger.error("Message delivered error {}".format(err))
    else:
        logger.debug('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def init_redis(redis_conf: dict):
    hosts = redis_conf.get("hosts", ["127.0.0.1"])
    ports = redis_conf.get("ports", [6379])
    db = redis_conf.get("db", "db1")
    pwd = redis_conf.get("pwd", "")
    if redis_conf["cluster"]:
        startup_nodes = [ClusterNode(host, port) for port in ports for host in hosts]
        client = RedisCluster(
            startup_nodes=startup_nodes, password=pwd, decode_responses=True
        )
        return client
    else:
        client = redis.Redis(host=hosts[0], port=ports[0], db=db, password=pwd, decode_responses=True)
        return client


class KafkaLoggerCollector(LoggerCollector):
    def __init__(self):
        super().__init__()
        producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP,
                                 compression_type='snappy')
        self.producer = producer

    def flush(self, item: LoggerItem):
        logger.info(LOG_ENABLE)
        if LOG_ENABLE:
            logger.info("flushing log")
            try:
                # producer.produce(LOG_CONSUMER_KEY, json.dumps(item.to_dict(), ensure_ascii=False),
                #                  callback=delivery_report)
                self.producer.send(LOG_CONSUMER_KEY,
                                   value=json.dumps(item.to_dict(), ensure_ascii=False, default=str, cls = CustomJSONEncoder).encode(
                                       "utf-8")).get()
                self.producer.flush(timeout=3)
            except Exception as dil_error:
                traceback.format_exc()
                logger.error(f"{dil_error}{traceback.format_exc()}")
                logger.error(json.dumps(item.to_dict()))
            finally:
                logger.info("flushed log")
        else:
            logger.info(json.dumps(item.to_dict(), ensure_ascii=False))


class RedisLoggerCollector(LoggerCollector):
    def __init__(self):
        super().__init__()
        self.redis_log_client = init_redis(REDIS_CONF)

    def flush(self, item: LoggerItem):
        if LOG_ENABLE:
            logger.info("flushing log")
            self.redis_log_client.rpush(LOG_CONSUMER_KEY, json.dumps(item.to_dict(), ensure_ascii=False, cls = CustomJSONEncoder))
        else:
            logger.info(json.dumps(item.to_dict(), ensure_ascii=False))


class LoggerQuickCrawlStrategy(LoggerStrategy):
    def __init__(self, interface: LoggerInterface, collector: LoggerCollector, clazz):
        super().__init__(interface, collector, clazz)
        self.action = None
        self.command = None
        self.domain = None
        self.type = None
        self.resp = None

    def set_base_info(self, action: CrawlerAction, command: str):
        self.action = action.value
        self.command = command

    def set_domain(self, domain):
        self.domain = domain

    def set_type(self, typo: CrawlerType):
        self.type = typo.__str__()

    def set_resp(self, resp):
        self.resp = Resp.from_dict(resp)

    def set_tag(self, key, val):
        flush_item = self.interface.get_item()
        if flush_item:
            try:
                flush_item.tag(key, val)
            except Exception as e:
                pass

    def set_tag_failed_block(self):
        flush_item = self.interface.get_item()
        if flush_item:
            try:
                flush_item.tag("failed.reason", "block")
            except Exception as e:
                flush_item.tag("failed.reason", "others")

    def set_tag_failed_reason(self, e: Exception):
        flush_item = self.interface.get_item()
        if flush_item:
            try:
                str_info = str(traceback.format_exc())
                if isinstance(e, ProxyError):
                    flush_item.tag("failed.reason", "proxy")
                elif isinstance(e, ReadTimeout):
                    flush_item.tag("failed.reason", "timeout")
                elif (str_info.__contains__("ERR_PROXY_CONNECTION_FAILED")
                      or str_info.__contains__("PROXY")
                      or str_info.__contains__("proxy")):
                    flush_item.tag("failed.reason", "proxy")
                else:
                    flush_item.tag("failed.reason", "others")
            except Exception as e:
                flush_item.tag("failed.reason", "others")

    def reset(self, item: dict):
        try:
            item = self.clazz.from_dict(item)
            item.action = self.action
            self.interface.reset(item)
        except Exception as e:
            logger.error(e)

    '''
    1. 取出需要投递的信息
    2. 投递消息
    3. 清除消息
    '''

    def flush(self, status=None):
        try:
            flush_item = self.interface.get_item()
            if flush_item is not None:
                flush_item.set_status(status)
                flush_item.command = self.command
                flush_item.domain = self.domain
                flush_item.type = self.type
                flush_item.resp = self.resp
                self.collector.flush(flush_item)
            self.interface.clean()
        except Exception as e:
            logger.error("push error")

    def info(self, message):
        self.interface.info(message)

    def times(self, times):
        self.interface.times(times)


def build_log():
    if LOG_TYPE == 'REDIS':
        collector = RedisLoggerCollector()
    else:
        collector: LoggerCollector = KafkaLoggerCollector()
    log = LoggerQuickCrawlStrategy(QuickLoggerInterface(), collector, QuickCrawlerLogItem)
    return log
