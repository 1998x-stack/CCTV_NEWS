import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from typing import List, Dict
from datetime import datetime
from src.news_collect_for_today import collect_news

class MarkdownFormatter:
    """用于将新闻数据格式化为 Markdown 格式的类。"""

    @staticmethod
    def format_news(news_list: List[Dict]) -> str:
        """将新闻列表格式化为 Markdown 字符串。"""
        markdown_lines = [
            f"# 新闻联播 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
        ]
        for news in news_list:
            title = news.get('title', '')
            url = news.get('link', '')  # 确保使用正确的键
            content = news.get('content', '')  # 加载内容
            markdown_lines.append(f"- [{title}]({url})\n  {content}")
        return '\n'.join(markdown_lines)
    
if __name__ == '__main__':
    today = datetime.now().strftime("%Y%m%d")
    collected_data = collect_news(today)
    markdown_content = MarkdownFormatter.format_news(collected_data)
    print(markdown_content)