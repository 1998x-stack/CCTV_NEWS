
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from typing import List, Dict
from datetime import datetime

class MarkdownFormatter:
    """用于将新闻数据格式化为 Markdown 格式的类。"""

    @staticmethod
    def format_news(news_list: List[Dict]) -> str:
        """将新闻列表格式化为 Markdown 字符串。"""
        markdown_lines = [
            f"# 今日新闻 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
        ]
        for news in news_list:
            title = news.get('title', '无标题')
            url = news.get('link', '无链接')  # 确保使用正确的键
            content = news.get('content', '内容未找到')  # 加载内容
            markdown_lines.append(f"- [{title}]({url})\n  {content}")
        return '\n'.join(markdown_lines)