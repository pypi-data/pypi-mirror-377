from wake_v2.logger_item import LoggerItem


class LoggerInterface:
    def __init__(self, item: LoggerItem = None):
        self.item = item

    def get_item(self):
        return self.item

    def error(self, message):
        pass

    def info(self, message):
        pass

    def debug(self, message):
        pass

    def warning(self, message):
        pass

    def critical(self, message):
        pass

    def extra(self, extras: dict):
        pass

    def clean(self):
        self.item = None

    def reset(self, item: LoggerItem):
        self.item = item

    def times(self, times):
        self.item.set_times(times)

    def domain(self, domain):
        self.item.domain = domain


class LoggerInterfaceOutput(LoggerInterface):
    def __init__(self):
        super().__init__()

    def info(self, message):
        print(message)
