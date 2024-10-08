import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import markdown
from typing import List, Dict
from datetime import datetime

class MarkdownFormatter:
    """用于将新闻数据格式化为 Markdown 格式的类。"""

    @staticmethod
    def format_news(news_list: List[Dict]) -> str:
        """将新闻列表格式化为 Markdown 字符串。"""
        # 标题和日期部分
        markdown_lines = [
            "# 《新闻联播》 📰\n",  # 增加表情符号
            f"> 发布日期：{datetime.now().strftime('%Y-%m-%d')} 📅\n",
            "---\n"
        ]
        for news in news_list:
            title = news.get('title', '无标题')  # 提供默认标题
            url = news.get('link', '')  # 确保使用正确的键
            content = news.get('content', '无内容')  # 加载内容，默认值为空内容
            # 使用 Markdown 链接格式，增强可读性
            markdown_lines.append(f"### [{title}]({url})\n")
            # 处理内容中的换行符，每段添加引用符号
            paragraphs = content.split('\n')
            
            if title == '国内联播快讯' and len(paragraphs) % 2 == 0:
                sub_titles = paragraphs[::2]
                sub_paragraphs = paragraphs[1::2]
                for sub_title, sub_paragraph in zip(sub_titles, sub_paragraphs):
                    markdown_lines.append(f" *{sub_title.strip()}*\n")
                    if sub_paragraph.strip():  # 跳过空行
                        markdown_lines.append(f"> {sub_paragraph.strip()}\n")
            else:
                for paragraph in paragraphs:
                    if paragraph.strip():  # 跳过空行
                        markdown_lines.append(f"> {paragraph.strip()}\n")
            markdown_lines.append("\n\n---\n\n")  # 使用分隔线来划分新闻条目
        
        # 合并所有行
        text = '\n'.join(markdown_lines)
        return markdown.markdown(text)
    
if __name__ == '__main__':
    today = datetime.now().strftime("%Y%m%d")
    from src.news_collect_for_today import collect_daily_news
    collected_data = collect_daily_news(today)
    markdown_content = MarkdownFormatter.format_news(collected_data)
    print(markdown_content)