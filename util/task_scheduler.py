import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import schedule
import time
from datetime import datetime
import pytz  # 用于处理时区
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


class TimezoneAwareScheduler:
    """
    一个时区感知的任务调度器，允许在指定时区的特定时间执行任务。

    Attributes:
        target_time (str): 任务执行的时间，格式为 'HH:MM'。
        timezone (str): 执行任务的时区名称，如 'Asia/Shanghai' 表示北京时间。
    """

    def __init__(self, target_time: str = '19:40', timezone: str = 'Asia/Shanghai'):
        """
        初始化任务调度器。

        Args:
            target_time (str): 任务每天执行的时间，格式为 'HH:MM' (24小时制)。
            timezone (str): 执行任务的时区，默认为 'Asia/Shanghai' (北京时间)。
        """
        self.target_time = target_time
        self.timezone = pytz.timezone(timezone)

    def start_scheduler(self, task_function: Callable[[], None]) -> None:
        """
        开始任务调度器，在指定时区的指定时间每天执行任务。

        Args:
            task_function (Callable[[], None]): 定时执行的任务函数，无参数无返回值。

        Raises:
            Exception: 如果调度器中断或发生意外。
        """
        def job_wrapper():
            # 获取当前时间，并转换为任务指定的时区
            now = datetime.now(self.timezone)
            logger.log_info(f"任务开始执行，当前时间为 {now.strftime('%Y-%m-%d %H:%M:%S')} ({self.timezone.zone})")
            task_function()

        # 每天在指定时区和时间执行任务
        schedule.every().day.at(self.target_time).do(job_wrapper)
        
        logger.log_info(f"任务调度器已启动，每天 {self.target_time} ({self.timezone.zone}) 执行一次任务。")
        
        try:
            while True:
                schedule.run_pending()  # 检查待执行的任务
                time.sleep(1)  # 睡眠以降低 CPU 负载
        except KeyboardInterrupt:
            logger.log_info("任务调度器已手动终止。")
        except Exception as error:
            logger.log_exception()