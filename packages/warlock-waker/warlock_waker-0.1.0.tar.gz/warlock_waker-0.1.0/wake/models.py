from enum import Enum


class Resp:
    def __init__(self, url: str = "", code: int = 200, msg: str = "", data: str = ""):
        self.url = url
        self.code = code
        self.msg = msg
        self.data = data

    @classmethod
    def from_dict(cls, data):
        return cls(
            url=data.get("url", ""),
            code=data.get("code", 200),
            msg=data.get("msg", ""),
            data=data.get("data", "")
        )


class Times:
    def __init__(self, start: int = 0, end: int = 0, pop: int = 0):
        self.start = start
        self.end = end
        self.pop = pop

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=data.get("start", 0),
            end=data.get("end", 0),
            pop=data.get("pop", 0)
        )


class Proxy:
    def __init__(self, _id: str = "", vendor: str = "", region: str = "", addr: str = ""):
        self.id = _id
        self.vendor = vendor
        self.region = region
        self.addr = addr

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get("id", ""),
            vendor=data.get("vendor", ""),
            region=data.get("region", ""),
            addr=data.get("addr", "")
        )


class Attempt:
    def __init__(self, ts: int = 0, code: int = 0, duration: int = 0, proxy: Proxy = Proxy.from_dict({})):
        self.ts = ts
        self.code = code
        self.duration = duration
        self.proxy = proxy

    @classmethod
    def from_dict(cls, data):
        return cls(
            ts=data.get("ts", ""),
            code=data.get("code", ""),
            duration=data.get("duration", ""),
            proxy=Proxy.from_dict(data.get("proxy", {}))
        )


class Executor:
    def __init__(self, _id: str = "", host: str = ""):
        self.id = _id
        self.host = host

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get("id", ""),
            host=data.get("host", "")
        )


class CrawlerType(Enum):
    GELLEN = "gellen"
    SUREFIRE = "surefire"
    SERP = "SERP"


class CrawlerAction(Enum):
    FETCH = "fetch"
    PARSE = "parse"
    SCHED = "sched"


