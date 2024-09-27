
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import schedule
import time
import logging
from util.markdown_formatter import MarkdownFormatter

class NewsEmailScheduler:
    """新闻邮件调度器，用于定时发送新闻邮件。

    Attributes:
        email_sender: EmailSender 实例，用于发送邮件。
        fetcher: HackerNewsFetcher 实例，用于获取新闻。
        interval_minutes: 发送邮件的时间间隔（分钟）。
    """

    def __init__(self, email_sender, fetcher, interval_minutes: int = 60 * 24):
        """初始化 NewsEmailScheduler 实例。

        Args:
            email_sender: EmailSender 实例。
            fetcher: HackerNewsFetcher 实例。
            interval_minutes: 发送邮件的时间间隔，默认为 30 分钟。
        """
        self.email_sender = email_sender
        self.fetcher = fetcher
        self.interval_minutes = interval_minutes
        logging.debug("NewsEmailScheduler 实例已创建。")

    def send_news_email(self):
        """获取新闻并发送邮件。"""
        try:
            news_list = self.fetcher.fetch_latest_news()
            if news_list:
                body = MarkdownFormatter.format_news(news_list)
                subject = f"Hacker News 最新新闻 ({time.strftime('%Y-%m-%d %H:%M')})"
                to_emails = [self.email_sender.username]  # 修改为实际的收件人列表
                self.email_sender.send_email(subject, body, to_emails)
                logging.info("新闻邮件发送成功。")
            else:
                logging.warning("未获取到新闻，邮件未发送。")
        except Exception as e:
            logging.error(f"发送新闻邮件时出错: {e}")

    def start(self):
        """开始定时任务。"""
        schedule.every(self.interval_minutes).minutes.do(self.send_news_email)
        logging.info(f"开始新闻邮件调度器，每 {self.interval_minutes} 分钟发送一次。")
        
        while True:
            schedule.run_pending()
            time.sleep(1)