from functools import wraps
import sys
from typing import Callable, Optional, TypeVar, overload

from arq.cron import cron
from arq.typing import OptionType, SecondsTimedelta, WeekdayOptionType

from .task_manager import TaskManager


# 兼容 ParamSpec
if sys.version_info >= (3, 10): # pragma: no cover
    from typing import ParamSpec
    P = ParamSpec("P")
else: # pragma: no cover
    try:
        from typing_extensions import ParamSpec
        P = ParamSpec("P")
    except ImportError:
        P = None

R = TypeVar("R")

def task(queue_name: str = "default", with_arq_ctx: bool = False):
    """
    Decorator to add a task to the task pool.
    """
    def decorator(func: Callable[P, R]):
        """
        Decorator to add a task to the task pool.
        """

        @overload
        def wrapper(*args: P.args, enqueue: bool, **kwargs: P.kwargs) -> R:
            ...
        
        @overload
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            ...

        @wraps(func)
        async def wrapper(*args: P.args, enqueue: bool = False, **kwargs: P.kwargs) -> R:
            """
            :param enqueue:  (Optional) 是否添加进队列执行.
            """
            if not with_arq_ctx:
                args = args[1:]

            if not enqueue:
                return await func(*args, **kwargs)

            task_queue = TaskManager.get_instance().get_task_queue(queue_name=queue_name)
            if not task_queue:
                raise RuntimeError(f"add task to queue failed, task queue [{queue_name}] not found!")

            return await task_queue.add_task(func=func, *args, **kwargs)

        TaskManager.get_instance().add_task(queue_name=queue_name, func=wrapper)
        return wrapper
    return decorator


def cron_task(
    queue_name: str = "default",
    name: Optional[str] = None,
    month: OptionType = None,
    day: OptionType = None,
    weekday: WeekdayOptionType = None,
    hour: OptionType = None,
    minute: OptionType = None,
    second: OptionType = None,
    microsecond: int = 123_456,
    run_at_startup: bool = False,
    unique: bool = True,
    job_id: Optional[str] = None,
    timeout: Optional[SecondsTimedelta] = None,
    keep_result: Optional[float] = 0,
    keep_result_forever: Optional[bool] = False,
    max_tries: Optional[int] = 5,
):
    """
    Decorator to add a cron task to the cron task pool.
    """
    def decorator(func):
        """
        Decorator to add a cron task to the cron task pool.
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            args = args[1:]
            return await func(*args, **kwargs)

        _cron_task = cron(
            wrapper,
            name=name,
            month=month,
            day=day,
            weekday=weekday,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            run_at_startup=run_at_startup,
            unique=unique,
            job_id=job_id,
            timeout=timeout,
            keep_result=keep_result,
            keep_result_forever=keep_result_forever,
            max_tries=max_tries,
        )
        TaskManager.get_instance().add_cron_task(queue_name=queue_name, func=_cron_task)
        return wrapper
    return decorator
