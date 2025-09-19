import asyncio
import sys
import pytest
import redis
import logging
from ff_arq import TaskManager

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "abc.123456"
REDIS_DB = 0

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture(scope="function", autouse=True)
async def init_task_queue():
    config = {
        "redis_dsn": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "task_dir_path": "tests/tasks",
        "queues": {
            "default": {
                "concurrency": 1
            }
        },
    }

    task_manager = TaskManager.init(**config)
    
    # 后台启动 TaskManager.run()
    task_manager_runner = (
        asyncio.create_task(task_manager.run())
        if sys.version_info >= (3, 7)
        else asyncio.ensure_future(task_manager.run())
    )

    yield
    
    # 清理 Redis
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB
    )
    for key in redis_client.scan_iter("*"):
        redis_client.delete(key)
    
    # 关闭后台任务
    task_manager_runner.cancel()

@pytest.mark.asyncio
async def test_run_task(caplog):
    """
    Test that test_task logs output as expected.
    """
    from .tasks.simple_task import test_task

    with caplog.at_level(logging.DEBUG):
        await test_task(sleep_time=1, enqueue=True)
        await asyncio.sleep(2)

    # 假设 test_task 打印的日志内容包含 "test_task executed"
    assert any("test_task completed" in record.message for record in caplog.records)

@pytest.mark.asyncio
async def test_run_cron_task(caplog):
    """
    Test that test_cron_task logs output as expected.
    """
    with caplog.at_level(logging.DEBUG):
        await asyncio.sleep(2)
        assert any("test_cron_task completed" in record.message for record in caplog.records)

@pytest.mark.asyncio
async def test_shutdown(caplog):
    """
    Test that TaskManager.shutdown runs without errors.
    """
    from .tasks.simple_task import test_task

    with caplog.at_level(logging.DEBUG):
        await test_task(sleep_time=1, enqueue=True)

        # 在执行任务前停止队列服务
        await TaskManager.get_instance().shutdown()
        
        await asyncio.sleep(2)
        assert not any("test_task completed" in record.message for record in caplog.records)
        assert not any("test_cron_task completed" in record.message for record in caplog.records)

@pytest.mark.asyncio
async def test_add_task_to_invalidate_queue():
    """
    Test that add_task_to_invalidate_queue runs without errors.
    """
    from .tasks.simple_task import add_task_to_invalidate_queue

    with pytest.raises(
        RuntimeError, 
        match="add task to queue failed, task queue \\[invalidate_queue\\] not found!"
    ):
        await add_task_to_invalidate_queue(enqueue=True)

@pytest.mark.asyncio
async def test_task_manager_not_initialized():
    """
    Test that accessing TaskManager instance without initialization raises an error.
    """
    TaskManager._instance = None

    with pytest.raises(
        RuntimeError, 
        match="TaskManager has not been initialized."
    ):
        TaskManager.get_instance()

@pytest.mark.asyncio
async def test_get_default_redis_settings():
    """
    Test that adding a task with an invalid function raises an error.
    """
    from ff_arq.task_queue import TaskQueue, RedisSettings

    task_queue = TaskQueue()
    redis_settings = task_queue.get_redis_settings()
    default_redis_settings = RedisSettings()
    assert str(redis_settings) == str(default_redis_settings)

@pytest.mark.asyncio
async def test_get_singlethon_redis_client():
    """
    Test that get_redis_client returns the same instance on multiple calls.
    """
    from ff_arq import TaskQueue, TaskQueueConfig

    config = TaskQueueConfig(redis_dsn=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    task_queue = TaskQueue(config=config)
    redis_client1 = await task_queue.get_redis_client()
    redis_client2 = await task_queue.get_redis_client()
    assert redis_client1 is redis_client2

@pytest.mark.asyncio
async def test_task_queue_restart(caplog):
    """
    Test that TaskQueue can be restarted without errors.
    """
    task_manager = TaskManager.get_instance()
    from .tasks.simple_task import test_task

    with caplog.at_level(logging.DEBUG):
        await test_task(sleep_time=2, enqueue=True)
        await asyncio.sleep(1)
        assert any("test_task start" in record.message for record in caplog.records)

        # 在执行任务前停止队列服务
        await task_manager.shutdown()

        await asyncio.sleep(2)
        assert not any("test_task completed" in record.message for record in caplog.records)

        # 重启任务队列
        task_manager_runner = (
            asyncio.create_task(task_manager.run())
            if sys.version_info >= (3, 7)
            else asyncio.ensure_future(task_manager.run())
        )

        # 等待in_progress_key过期，任务重新入队        
        task_queue = task_manager.get_task_queue("default")
        await asyncio.sleep(task_queue.worker.in_progress_timeout_s)
        assert any("test_task completed" in record.message for record in caplog.records)

        task_manager_runner.cancel()