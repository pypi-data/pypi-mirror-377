from typing import Callable, Union

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings
from arq.jobs import Job
from .task_worker import Worker
from .schema import TaskQueueConfig


class TaskQueue(object):

    def __init__(
        self,
        config: TaskQueueConfig = None
    ) -> None:
        """
        Constructor.

        :param config 任务队列配置
        """
        self.config = config if config else TaskQueueConfig()
        self.redis_client = None
        self.worker = None

    async def add_task(self, func: Union[Callable, str], *args, **kwargs) -> Job:
        """
        Add task.

        :param func 任务函数
        :param args 任务相关的位置参数，部分arq任务参数参考arq文档说明
        :param kwargs 任务相关的关键字参数，部分arq任务参数参考arq文档说明
        :return arq Job实例
        """
        redis_client = await self.get_redis_client()
        return await redis_client.enqueue_job(
            func if isinstance(func, str) else func.__name__, *args, **kwargs
        )

    async def get_redis_client(self) -> ArqRedis:
        """
        Get redis client.

        :return ArqRedis实例
        """
        if self.redis_client:
            return self.redis_client

        redis_settings = self.get_redis_settings()
        self.redis_client = await create_pool(
            redis_settings, retry=3, default_queue_name=self.config.queue_name
        )
        return self.redis_client
    
    def get_redis_settings(self) -> RedisSettings:
        """
        Get default redis configuration.

        :return RedisSettings实例
        """
        if self.config.redis_dsn:
            return RedisSettings.from_dsn(self.config.redis_dsn)

        return RedisSettings()

    async def run(self):
        """
        Start arq worker.
        """
        from .task_manager import TaskManager
        task_manager = TaskManager.get_instance()

        functions = task_manager.get_tasks(queue_name=self.config.queue_name)
        cron_jobs = task_manager.get_cron_tasks(queue_name=self.config.queue_name)

        self.worker = Worker(
            functions=functions,
            cron_jobs=cron_jobs,
            queue_name=self.config.queue_name,
            max_jobs=self.config.concurrency,
            job_timeout=self.config.task_timeout,
            redis_settings=self.get_redis_settings(),
            keep_result=self.config.keep_result,
            retry_jobs=self.config.retry_jobs,
            max_tries=self.config.max_tries,
            handle_signals=self.config.handle_signals,
        )

        await self.worker.async_run()

    async def shutdown(self):
        """
        Shutdown arq worker and redis client.
        """
        if self.worker:
            await self.worker.close()
