from arq.connections import RedisSettings


class TaskQueueConfig:

    def __init__(
        self,
        queue_name: str = "default",
        concurrency: int = 10,
        task_timeout: int = 300,
        keep_result: int = 3600,
        retry_jobs: bool = True,
        max_tries: int = 5,
        handle_signals: bool = False,
        redis_dsn: str = None
    ):
        """
        构造函数

        :param queue_name 队列名称
        :param concurrency 并发执行任务数量
        :param task_timeout 任务超时时间
        :param keep_result 任务结果最大保存时间
        :param retry_jobs 是否开启任务重试
        :param max_tries 最大重试次数
        :param handle_signals 是否接受进程关闭信号
        :param redis_dsn redis链接配置信息
        """
        self.queue_name = queue_name
        self.concurrency = concurrency
        self.task_timeout = task_timeout
        self.keep_result = keep_result
        self.max_tries = max_tries
        self.retry_jobs = retry_jobs
        self.handle_signals = handle_signals
        self.redis_dsn = redis_dsn