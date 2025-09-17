"""
定义log的基础形式
{
  "action": "crawl|parse|sched", # 关键动作：爬取、内链解析、列表页或作者页或其他种子页调度
  "method": "requests|wget|curl_cffi|selenium|drssionpage", # 关键动作的具体分类
  "status": "success|timeout|failed", # 状态枚举
  "timestamps": {
    "push": 1718107877366, # 入队时间戳
    "pop": 1718107877366, # 出队时间戳
    "end": 1718107877366, # 处理结束时间戳
  },
  "logs": [
     "2024-06-11 20:11:18 重试下载不通过，放入渲染队列 耗时： 3355.701171875", # 文本log内容，注意转义，记录额外事件信息，注意精简日志（尤其无必要再重复打印url信息）、解决字符集问题
  ],
  "tags": {
    "k1": "v1", # k/v均为字符串类型，拓展字段须遵循key规范（wiki约束），方便下游分析
    "k2": "v2"
  }
}
"""
import time


class LoggerItem:
    def __init__(self,
                 action: str = "",
                 method: str = "",
                 status: str = "",
                 times=None,
                 logs=None,
                 tags=None
                 ):
        """
        :params action: 关键动作
        :params method: 关键动作的具体分类
        :params status: 状态枚举
        :params timestamps: 时间戳集合
        :params logs: 日志
        :params tags: 标签
        """
        if times is None:
            times = {}
        if logs is None:
            logs = []
        if tags is None:
            tags = {}
        self.action = action
        self.status = status
        self.times = times
        self.logs = logs
        self.tags = tags
        self.attempts = []
        self.ts = int(time.time() * 1_000)

    def to_dict(self):
        return self.__dict__

    def log(self, message: str):
        self.logs.append(message)

    def tag(self, key: str, val: str):
        self.tags[key] = val

    def times(self, key: str, val: str):
        self.times[key] = val

    def tags(self, tags: dict):
        self.tags = tags

    def set_times(self, times: dict):
        self.times = times

    def set_status(self, status: str):
        self.status = status

    @classmethod
    def from_dict(cls, data):
        return cls(
            action=data.get("action", ""),
            status=data.get("status", ""),
            times=data.get("times", {}),
            logs=data.get("logs", []),
            tags=data.get("tags", {})
        )
