import logging
from datetime import datetime, timedelta
from src.video_data_collector import VideoDataCollector
from src.markdown_formatter import MarkdownFormatter
from typing import List, Dict

class NewsCollector:
    """用于收集新闻数据的类。"""

    def __init__(self, start_date: str, end_date: str, proxies: Dict[str, str]):
        self.video_data_collector = VideoDataCollector(start_date, end_date, proxies)

    def fetch_latest_news(self) -> List[Dict]:
        """获取最新的新闻数据，包括今天和过去两周的数据。"""
        today = datetime.now().strftime("%Y%m%d")
        two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime("%Y%m%d")
        
        # 收集今天和过去两周的视频数据
        all_data = self.video_data_collector.collect_all_data()
        
        # 过滤出今天的数据
        today_data = [video for video in all_data if video['date'] == today]
        logging.info(f"Fetched {len(today_data)} videos for today.")
        
        return today_data