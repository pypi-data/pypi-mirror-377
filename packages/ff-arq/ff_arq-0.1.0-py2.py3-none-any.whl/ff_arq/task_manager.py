import os
import asyncio
import importlib
from typing import Dict, Union
from .task_queue import TaskQueue
from .schema import TaskQueueConfig


class TaskManager:
    
    _instance = None

    def __init__(
        self,
        redis_dsn: str = None,
        task_dir_path: str = "src/tasks",
        queues: Dict[str, Union[dict, TaskQueueConfig]] = {}
    ):
        """
        构造函数

        :param redis_dsn redis链接配置信息
        :param queues 任务队列配置
        :param task_dir_path 任务目录路径
        """
        self.redis_dsn = redis_dsn
        self.task_dir_path = task_dir_path
        self.queues = queues

        self.task_pool = {}
        self.cron_task_pool = {}
        self.task_queues = self._init_task_queues()

    def _init_task_queues(self) -> Dict[str, TaskQueue]:
        """
        初始化任务队列

        :return 任务队列实例集合
        """
        task_queues = {}

        for name, config in self.queues.items():
            _config = config if isinstance(config, TaskQueueConfig) else TaskQueueConfig(**config)
            _config.queue_name = name

            if not _config.redis_dsn:
                _config.redis_dsn = self.redis_dsn
            
            task_queues[name] = TaskQueue(config=_config)

        return task_queues

    @classmethod
    def init(
        cls,
        redis_dsn: str = None,
        task_dir_path: str = "src/tasks",
        queues: Dict[str, Union[dict, TaskQueueConfig]] = {}
    ) -> "TaskManager":
        """
        初始化

        :param redis_dsn Redis配置信息
        :param queues 任务队列配置
        :param task_dir_path 任务目录路径
        :return TaskManager 实例
        """
        cls._instance = TaskManager(
            redis_dsn=redis_dsn,
            task_dir_path=task_dir_path,
            queues=queues
        )
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> "TaskManager":
        """
        获取 TaskManager 实例

        :return TaskManager 实例
        """
        if not cls._instance:
            raise RuntimeError(
                "TaskManager has not been initialized. "
                "Please initialize it using 'TaskManager.init()' before accessing the instance."
            )
        
        return cls._instance

    def get_task_queue(self, queue_name: str) -> TaskQueue:
        """
        获取 TaskQueue 实例

        :param queue_name 队列名称
        :return TaskQueue 实例
        """
        return self.task_queues.get(queue_name)
    
    def add_task(self, queue_name: str, func):
        """
        添加任务

        :param queue_name 队列名称
        :param func 任务函数
        """
        if queue_name not in self.task_pool:
            self.task_pool[queue_name] = []

        self.task_pool[queue_name].append(func)

    def get_tasks(self, queue_name: str) -> list:
        """
        获取队列任务

        :param queue_name 队列名称
        :return 任务列表
        """
        return self.task_pool.get(queue_name, [])

    def add_cron_task(self, queue_name: str, func):
        """
        添加定时任务

        :param queue_name 队列名称
        :param func 任务函数
        """
        if queue_name not in self.cron_task_pool:
            self.cron_task_pool[queue_name] = []

        self.cron_task_pool[queue_name].append(func)

    def get_cron_tasks(self, queue_name: str):
        """
        获取队列定时任务

        :param queue_name 队列名称
        :return 定时任务列表
        """
        return self.cron_task_pool.get(queue_name, [])

    async def run(self):
        """
        运行任务队列
        """
        self.load_tasks(self.task_dir_path)
        asyncio_tasks = [queue.run() for queue in self.task_queues.values()]
        await asyncio.gather(*asyncio_tasks)

    def load_tasks(self, dir_path: str = "src/tasks"):
        """
        加载任务

        :param dir_path 文件目录路径
        """
        if not dir_path or not os.path.exists(dir_path): # pragma: no cover
            return

        for entry in os.scandir(dir_path):
            if entry.is_dir():
                self.load_tasks(entry.path)
                continue

            filename = entry.name
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(dir_path, filename)
            module_name = filename[:-3]

            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

    async def shutdown(self):
        """
        停止任务队列
        """
        asyncio_tasks = [
            queue.shutdown() for queue in self.task_queues.values()
        ]
        await asyncio.gather(*asyncio_tasks)
