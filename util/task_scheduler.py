import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))


import schedule
import time
from typing import Callable
from util.log_utils import logger

class TaskScheduler:
    """
    任务调度器类，用于定时执行指定的任务。

    Attributes:
        interval_minutes (int): 任务执行的时间间隔（分钟）。
    """

    def __init__(self, interval_minutes: int):
        """
        初始化任务调度器。

        Args:
            interval_minutes (int): 每隔多少分钟执行一次任务。
        """
        if interval_minutes <= 0:
            raise ValueError("时间间隔必须大于0分钟。")  # 检查边界条件
        self.interval_minutes = interval_minutes

    def start_scheduler(self, task_function: Callable[[], None]) -> None:
        """
        开始任务调度器，定时执行任务。

        Args:
            task_function (Callable[[], None]): 定时执行的任务函数，无参数无返回值。

        Raises:
            Exception: 如果调度器中断或发生意外。
        """
        schedule.every(self.interval_minutes).minutes.do(task_function)  # 定义调度间隔
        
        logger.log_info(f"任务调度器已启动，每 {self.interval_minutes} 分钟执行一次任务。")
        
        try:
            while True:
                schedule.run_pending()  # 检查待执行的任务
                time.sleep(5)  # 睡眠以降低 CPU 负载
        except KeyboardInterrupt:
            logger.log_info("任务调度器已手动终止。")
        except Exception as error:
            logger.log_exception()

    def stop_scheduler(self) -> None:
        """
        优雅地停止任务调度器。

        此方法可以通过外部调用来停止调度器。当前版本中，调度器使用无限循环，默认只通过手动终止。
        """
        logger.log_info("任务调度器停止功能暂未实现。当前只能通过手动停止。")
