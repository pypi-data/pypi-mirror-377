from wake.logger_item import LoggerItem


class LoggerCollector:
    def __init__(self):
        pass

    def flush(self, item: LoggerItem):
        pass


class LoggerCollectorNone(LoggerCollector):
    def __init__(self):
        super().__init__()

    def flush(self, item: LoggerItem):
        pass
