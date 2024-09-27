# coding=utf-8
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import pandas as pd
import time
from tqdm import tqdm  # 导入tqdm库

from util.log_utils import logger
from util.utils import determine_format

class VideoDataCollector:
    def __init__(self, start_date: str, end_date: str, proxies: Dict[str, str]):
        """
        初始化视频数据收集器
        :param start_date: 开始日期，格式为 "YYYYMMDD"
        :param end_date: 结束日期，格式为 "YYYYMMDD"
        :param proxies: 代理设置字典
        """
        start_date_format = determine_format(start_date)
        end_date_format = determine_format(end_date)
        self.start_date = datetime.strptime(start_date, start_date_format) if start_date else datetime.now()
        self.end_date = datetime.strptime(end_date, end_date_format) if end_date else datetime.now()
        self.proxies = proxies

    def get_video_data(self, date: str, retries: int = 3) -> List[Dict[str, Any]]:
        """
        获取指定日期的视频数据，带重试机制
        :param date: 日期字符串，格式为 "YYYYMMDD"
        :param retries: 最大重试次数
        :return: 视频信息列表
        """
        url = f"https://tv.cctv.com/lm/xwlb/day/{date}.shtml"
        for attempt in range(retries):
            try:
                response = requests.get(url, proxies=self.proxies)
                response.raise_for_status()  # 如果响应错误，将引发HTTPError
                soup = BeautifulSoup(response.content, 'html.parser')
                videos = []
                for li in soup.select('li'):
                    video_info = {}
                    anchor = li.find('a', href=True)

                    # 确保存在链接和标题
                    if anchor and 'title' in anchor.attrs:
                        video_info['link'] = anchor['href']
                        video_info['title'] = anchor['title']
                        video_info['date'] = date  # 添加日期键
                    else:
                        logger.log_info(f"No valid link or title found for date {date}. Skipping entry.")
                        continue  # 如果没有链接或标题，跳过这个条目

                    duration_span = li.find('span')
                    video_info['duration'] = duration_span.text if duration_span else "未知时长"  # 处理时长缺失的情况
                    video_info['content'] = self.get_video_content(video_info['link'])
                    videos.append(video_info)

                return videos
            except Exception as e:
                logger.log_exception()
                time.sleep(1)  # 等待1秒再重试
        return []

    def get_video_content(self, video_url: str) -> str:
        """
        获取视频页面的内容
        :param video_url: 视频页面URL
        :return: 视频内容
        """
        try:
            response = requests.get(video_url, proxies=self.proxies)
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.select('#content_area p')
            content = '\n'.join([p.text for p in paragraphs])
            return content if content else "内容未找到"
        except Exception as e:
            logger.log_exception()
            return "内容未找到"

    def date_range(self) -> List[str]:
        """
        生成日期范围内的所有日期
        :return: 日期列表，格式为 "YYYYMMDD"
        """
        delta = self.end_date - self.start_date
        return [(self.start_date + timedelta(days=i)).strftime("%Y%m%d") for i in range(delta.days + 1)]

    def collect_all_data(self) -> List[Dict[str, Any]]:
        """
        收集指定日期范围内的所有视频数据
        :return: 包含所有视频信息的列表
        """
        all_data = []
        dates = self.date_range()
        with ThreadPoolExecutor(max_workers=20) as executor:
            # 使用 tqdm 进度条来显示进度
            future_to_date = {executor.submit(self.get_video_data, date): date for date in dates}
            for future in tqdm(as_completed(future_to_date), total=len(future_to_date), desc="Fetching videos"):
                date = future_to_date[future]
                try:
                    data = future.result()
                    if data:
                        all_data.extend(data)
                        logger.log_info(f"Success: Fetched data for {date}")
                    else:
                        logger.log_info(f"Failed: No data found for {date}")
                except Exception as e:
                    logger.log_exception()
        return self.clean_collected_data(all_data)

    def clean_collected_data(self, collected_data):
        collected_data = [
            {
                'date' : self.convert_date(data['date']),
                'duration' : data['duration'],
                'title' : data['title'].strip("[视频]").strip(),
                'content' : data['content'].strip("央视网消息（新闻联播）：").strip(),
                'link' : data['link'],
            }
            for data in collected_data
            if '内容未找到' not in data['content']
        ]
        return collected_data
    
    def convert_date(self, date) -> str:
        date_str = str(date)
        return pd.to_datetime(date_str, errors='coerce', format=determine_format(date_str)).strftime("%Y-%m-%d")
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        将数据保存为JSON文件
        :param data: 视频信息列表
        :param filename: 输出文件名
        """
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logger.log_info(f"Data saved to {filename}")

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        将数据转换为CSV格式并保存
        :param data: 视频信息列表
        :param filename: 输出文件名
        """
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.log_info(f"Data saved to {filename}")