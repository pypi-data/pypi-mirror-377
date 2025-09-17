import wake_v2.utils
from wake_v2.models import CrawlerAction, CrawlerType, CrawlerCommand, CrawlerStatus
from wake_v2.quick_logger import build_log
import json
log = build_log()
log.set_base_info(CrawlerAction.FETCH, CrawlerCommand.WGET)
log.reset({
    "sid": "dap000dd5db@hu18f1416ed6f46f9802",
    "appid": "fuck",
    "url": "htts://fuck.com/a/b/c/d?with=you",
    "domain": "fuck.com",
    "ts": 1718107877366,
    "version": "v2",
    "type": "gellen|surefire|SERP",
    "action": "fetch|parse|sched",
    "command": "requests|curl_cffi|playwright|wget|clip|secular",
    "status": "success|timeout|failed",
    "resp": {
        "url": "wwww.fuck.com",
        "code": 200,
        "msg": "xxxx",
        "data": "..."
    },
    "times": {
        "push": 1718107877366,
        "pop": 1718107877366,
        "end": 1718107877366
    },
    "retries": 0,
    "attempts": [
        {
            "ts": 1757986950255,
            "code": 200,
            "duration": 666,
            "proxy": {
                "id": "47636QYC01",
                "vendor": "91|yunlifang|asyun|ss",
                "region": "B3",
                "addr": "http://115.209.79.80:3328"
            }
        }
    ],
    "executor": {
        "id": "run-data-api-request-gray-5f45cd7bf7-bgkz9",
        "host": "10.103.246.212"
    },
    "logs": [
        "2024-06-11 20:11:18 retry failed, fallback to renderer queue, cost: 3355 ms"
    ],
    "tags": {
        "k": "v",
        "path": "/path/to/pdf"
    }
}
)
log.times({
    "pop": 1111,
    "push": 1111,
    "end": 1111
})
log.append_attempt(
    {"ts": 1, "code": 1111, "duration": 1111, "proxy": {"id": "1", "vendor": "A", "region": "cn", "addr": "127.0.0.1"}})
log.append_attempt(
    {"ts": 1, "code": 1111, "duration": 1111, "proxy": {"id": "1", "vendor": "A", "region": "cn", "addr": "127.0.0.1"}})
log.append_attempt(
    {"ts": 1, "code": 1111, "duration": 1111, "proxy": {"id": "1", "vendor": "A", "region": "cn", "addr": "127.0.0.1"}})
log.set_domain("bbb.com")
log.set_resp({
    "url": "http://127.0.0.1:1.html",
    "code": 200,
    "msg": "222",
    "data": ""
})
log.set_type(CrawlerType.SUREFIRE)

log.info("你好")
# log.flush(CrawlerStatus.SUCCESS)
result = json.dumps(log.interface.item.__dict__, ensure_ascii=False,
                    cls=wake_v2.utils.CustomJSONEncoder)
print(result)