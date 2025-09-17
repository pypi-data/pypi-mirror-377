import json

import wake_v2.utils
from wake_v2.logger_item import LoggerItem
from wake_v2.logger_collector import LoggerCollector
from wake_v2.logger_interface import LoggerInterface, LoggerInterfaceOutput
from wake_v2.models import Attempt, CrawlerStatus


class LoggerStrategy:
    def __init__(self, interface: LoggerInterface, collector: LoggerCollector, clazz):
        self.collector = collector
        self.interface = interface
        self.clazz = clazz
        self.action = None
        self.command = None

    def set_base_info(self, action, command):
        self.action = action
        self.command = command

    def reset(self, item: dict):
        item = self.clazz.from_dict(item)
        item.action = self.action
        self.interface.reset(item)

    def append_attempt(self, attempt_: dict):
        attempt = Attempt.from_dict(attempt_)
        try:
            if self.interface.item and hasattr(self.interface.item, "attempts"):
                if self.interface.item.attempts:
                    self.interface.item.attempts.append(attempt)
                else:
                    self.interface.item.attempts = []
                    self.interface.item.attempts.append(attempt)
        except Exception as e:
            pass

    '''
    1. 取出需要投递的信息
    2. 投递消息
    3. 清除消息
    '''

    def flush(self, status: CrawlerStatus = CrawlerStatus.SUCCESS):
        flush_item = self.interface.get_item()
        flush_item.set_status(status.value)
        self.collector.flush(flush_item)
        self.interface.clean()

    def info(self, message):
        self.interface.info(message)

    def times(self, times):
        self.interface.times(times)


log = LoggerStrategy(LoggerInterfaceOutput(), LoggerCollector(), LoggerItem)
