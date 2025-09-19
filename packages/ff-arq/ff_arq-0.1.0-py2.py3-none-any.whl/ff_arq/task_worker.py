from arq import Worker as ArqWorker
from arq.constants import in_progress_key_prefix


class Worker(ArqWorker):
    """
    Arq Worker.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        修改in_progress_timeout_s数值,
        确保in_progress_key过期前能够被重新设置过期时间至少3次
        """
        super().__init__(*args, **kwargs)
        self.in_progress_timeout_s = self.poll_delay_s * 3 + 10

    async def heart_beat(self) -> None:
        """
        更新worker心跳检测代码逻辑, 增加in_progress任务超时设置
        """
        await self._update_progressing_job_expire_time()
        return await super().heart_beat()

    async def _update_progressing_job_expire_time(self):
        """
        更新in_progress_key的过期时间, 解决以下问题:
        避免job_timeout时长设置过长, 应用(worker)重启后任务没有快速重启异常

        注:
        心跳检测的频率是由poll_delay控制的, 为确保in_progress_key的过期时间能够正确设置,
        in_progress_key的过期时间至少为poll_delay的3倍(保证在过期之前有2次过期时间设置)
        """
        for job_id, _ in list(self.tasks.items()):
            in_progress_key = in_progress_key_prefix + job_id
            async with self.pool.pipeline(transaction=True) as pipe:
                pipe.pexpire(in_progress_key, int(self.in_progress_timeout_s * 1000))
                await pipe.execute()
