
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import logging
from datetime import datetime
from src.news_collector import NewsCollector
from src.email_sender import EmailSender
from src.visualizations import Visualizations
from src.markdown_formatter import MarkdownFormatter

def main():
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 设置代理（如果需要）
    proxies = {
        # 'http': 'http://your_proxy',
        # 'https': 'http://your_proxy',
    }
    
    # 初始化新闻收集器，设置开始和结束日期为今天
    today = datetime.now().strftime("%Y%m%d")
    news_collector = NewsCollector(start_date=today, end_date=today, proxies=proxies)
    
    # 获取今日新闻
    today_news = news_collector.fetch_latest_news()
    
    # 可视化设置
    font_path = 'path/to/SimHei.ttf'  # 修改为实际的字体路径
    visualizer = Visualizations(font_path)
    
    # 格式化为Markdown
    if today_news:
        markdown_content = MarkdownFormatter.format_news(today_news)
        
        # 创建可视化图表
        keywords = [news['title'] for news in today_news]
        visualizer.build_word_cloud(keywords, 'word_cloud.png')
        
        province_data = news_collector.extract_provinces(today_news)  # 假设有这个方法
        visualizer.visualize_provinces(province_data, 'province_frequency.png')
        
        visualizer.visualize_keywords(today_news, 'keywords_frequency.png')
        
        # 发送电子邮件
        email_sender = EmailSender(smtp_server='smtp.example.com', smtp_port=587,
                                   username='your_email@example.com', password='your_password')
        
        # 添加附件
        attachments = ['word_cloud.png', 'province_frequency.png', 'keywords_frequency.png']
        email_sender.send_email(subject=f"今日新闻 ({today})", body=markdown_content, to_emails=['recipient@example.com'], attachments=attachments)
    else:
        logging.warning("今日没有新闻数据。")

if __name__ == "__main__":
    main()