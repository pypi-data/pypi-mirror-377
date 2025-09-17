from wake.quick_logger import build_log

log = build_log()
log.reset({
    "url": "https://aiqicha.baidu.com/mark/markDetail?dataId=e48c4453cd5245cc421ad9a4f69b1273",
    "domain": "aiqicha.baidu.com",
    "sid": "gnu00018986@te1953b83b8643700012",
    "task_id": "",
    "retries": 3,
    "keywords": "",
    "request_url": [],
    "redirects": 0,
    "request_params": {},
    "tags": {
        "father_url": "https://aiqicha.baidu.com/company_mark_22244683502288",
        "normalize_url": "https://aiqicha.baidu.com/mark/markDetail?dataId=e48c4453cd5245cc421ad9a4f69b1273",
        "url_source": "url",
        "father_task_id": "",
        "father_sid": "gnu00014342@hf1953a99b7f83800012",
        "write_to_dataapi": "normalization",
        "http_code": "200"
    }
})
log.append_proxy({"code": 1, "vps": "2222", "address": "10.1.1.1", "delay": 400, "time": 111111111})
log.append_proxy({"code": 1, "vps": "2222", "address": "10.1.1.1", "delay": 400, "time": 111111111})
log.append_proxy({"code": 1, "vps": "2222", "address": "10.1.1.1", "delay": 400, "time": 111111111})
log.append_proxy({"code": 1, "vps": "2222", "address": "10.1.1.1", "delay": 400, "time": 111111111})
log.info("你好")
log.flush()
