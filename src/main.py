import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from datetime import datetime, timedelta

from config.config import EMAIL_ADDRESS, EMAIL_PASSWORD, TO_EMAILS, DATA_CSV_PATH, Domestic_Broadcast_News_CSV_PATH, BASIC_DATA_DIR, BASIC_IMAGE_DIR
from src.news_collect_for_today import collect_news


from util.log_utils import logger
from util.email_sender import EmailSender
from util.markdown_formatter import MarkdownFormatter
from util.visualizations import run_visualizations

def main():
    today = datetime.now().strftime("%Y%m%d")
    day_14_before = (datetime.now() - timedelta(days=14)).strftime("%Y%m%d")
    day_3mon_before = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
    collected_data = collect_news(today)
    markdown_content = MarkdownFormatter.format_news(collected_data)
    logger.log_info("Markdown content generated.")
    
    ### make dirs
    os.makedirs(
        BASIC_IMAGE_DIR,
        exist_ok=True
    )
    os.makedirs(
        os.path.join(
            BASIC_IMAGE_DIR,
            'all',
            'keywords'
        ),
        exist_ok=True
    )
    os.makedirs(
        os.path.join(
            BASIC_IMAGE_DIR,
            'all',
            'province'
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            BASIC_IMAGE_DIR,
            'all',
            'wordCloud'
        ),
        exist_ok=True
    )
    os.makedirs(
        os.path.join(
            BASIC_IMAGE_DIR,
            'domestic_broadcast_news',
            'keywords'
        ),
        exist_ok=True
    )
    os.makedirs(
        os.path.join(
            BASIC_IMAGE_DIR,
            'domestic_broadcast_news',
            'province'
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            BASIC_IMAGE_DIR,
            'domestic_broadcast_news',
            'wordCloud'
        ),
        exist_ok=True
    )

    ### 14天前至今的数据可视化
    result_data_path_all_14 = os.path.join(
        BASIC_DATA_DIR,
        'all',
        f'result_data_all_14_{day_14_before}_{today}.csv'
    )
    keywords_png_path_all_14 = os.path.join(
        BASIC_IMAGE_DIR,
        'all',
        'keywords',
        f'keywords_png_all_14_{day_14_before}_{today}.png'
    )
    province_frequency_png_path_all_14 = os.path.join(
        BASIC_IMAGE_DIR,
        'all',
        'province',
        f'province_frequency_png_all_14_{day_14_before}_{today}.png'
    )
    wordcloud_png_path_all_14 = os.path.join(
        BASIC_IMAGE_DIR,
        'all',
        'wordCloud',
        f'wordcloud_png_all_14_{day_14_before}_{today}.png'
    )
    run_visualizations(
        file_path=DATA_CSV_PATH,
        date_range=(day_14_before, today),
        algorithm="textrank",
        fields=['title', 'content'],
        n_keywords=40,
        result_data_path=result_data_path_all_14,
        keywords_png_path=keywords_png_path_all_14,
        provinces_png_path=province_frequency_png_path_all_14,
        wordcloud_png_path=wordcloud_png_path_all_14,
    )
    logger.log_info("Visualizations for 14 days before today completed.")
    
    ### 14天前至今的国内广播新闻可视化
    result_data_path_broadcast_14 = os.path.join(
        BASIC_DATA_DIR,
        'domestic_broadcast_news',
        f'result_data_broadcast_14_{day_14_before}_{today}.csv'
    )
    keywords_png_path_broadcast_14 = os.path.join(
        BASIC_IMAGE_DIR,
        'domestic_broadcast_news',
        'keywords',
        f'keywords_png_broadcast_14_{day_14_before}_{today}.png'
    )
    province_frequency_png_path_broadcast_14 = os.path.join(
        BASIC_IMAGE_DIR,
        'domestic_broadcast_news',
        'province',
        f'province_frequency_png_broadcast_14_{day_14_before}_{today}.png'
    )
    wordcloud_png_path_broadcast_14 = os.path.join(
        BASIC_IMAGE_DIR,
        'domestic_broadcast_news',
        'wordCloud',
        f'wordcloud_png_broadcast_14_{day_14_before}_{today}.png'
    )
    run_visualizations(
        file_path=Domestic_Broadcast_News_CSV_PATH,
        date_range=(day_14_before, today),
        algorithm="textrank",
        fields=['title', 'content'],
        n_keywords=40,
        result_data_path=result_data_path_broadcast_14,
        keywords_png_path=keywords_png_path_broadcast_14,
        provinces_png_path=province_frequency_png_path_broadcast_14,
        wordcloud_png_path=wordcloud_png_path_broadcast_14,
    )
    logger.log_info("Visualizations for 14 days before today's domestic broadcast news completed.")
    
    ### 90天前至今的数据可视化
    result_data_path_all_3mon = os.path.join(
        BASIC_DATA_DIR,
        'all',
        f'result_data_all_3mon_{day_3mon_before}_{today}.csv'
    )
    keywords_png_path_all_3mon = os.path.join(
        BASIC_IMAGE_DIR,
        'all',
        'keywords',
        f'keywords_png_all_3mon_{day_3mon_before}_{today}.png'
    )
    province_frequency_png_path_all_3mon = os.path.join(
        BASIC_IMAGE_DIR,
        'all',
        'province',
        f'province_frequency_png_all_3mon_{day_3mon_before}_{today}.png'
    )
    wordcloud_png_path_all_3mon = os.path.join(
        BASIC_IMAGE_DIR,
        'all',
        'wordCloud',
        f'wordcloud_png_all_3mon_{day_3mon_before}_{today}.png'
    )
    run_visualizations(
        file_path=DATA_CSV_PATH,
        date_range=(day_3mon_before, today),
        algorithm="textrank",
        fields=['title', 'content'],
        n_keywords=40,
        result_data_path=result_data_path_all_3mon,
        keywords_png_path=keywords_png_path_all_3mon,
        provinces_png_path=province_frequency_png_path_all_3mon,
        wordcloud_png_path=wordcloud_png_path_all_3mon,
    )
    logger.log_info("Visualizations for 90 days before today completed.")
    
    ### 90天前至今的国内广播新闻可视化
    result_data_path_broadcast_3mon = os.path.join(
        BASIC_DATA_DIR,
        'domestic_broadcast_news',
        f'result_data_broadcast_3mon_{day_3mon_before}_{today}.csv'
    )
    keywords_png_path_broadcast_3mon = os.path.join(
        BASIC_IMAGE_DIR,
        'domestic_broadcast_news',
        'keywords',
        f'keywords_png_broadcast_3mon_{day_3mon_before}_{today}.png'
    )
    province_frequency_png_path_broadcast_3mon = os.path.join(
        BASIC_IMAGE_DIR,
        'domestic_broadcast_news',
        'province',
        f'province_frequency_png_broadcast_3mon_{day_3mon_before}_{today}.png'
    )
    wordcloud_png_path_broadcast_3mon = os.path.join(
        BASIC_IMAGE_DIR,
        'domestic_broadcast_news',
        'wordCloud',
        f'wordcloud_png_broadcast_3mon_{day_3mon_before}_{today}.png'
    )
    run_visualizations(
        file_path=Domestic_Broadcast_News_CSV_PATH,
        date_range=(day_3mon_before, today),
        algorithm="textrank",
        fields=['title', 'content'],
        n_keywords=40,
        result_data_path=result_data_path_broadcast_3mon,
        keywords_png_path=keywords_png_path_broadcast_3mon,
        provinces_png_path=province_frequency_png_path_broadcast_3mon,
        wordcloud_png_path=wordcloud_png_path_broadcast_3mon,
    )
    logger.log_info("Visualizations for 90 days before today's domestic broadcast news completed.")
    
    
    # 发送电子邮件
    email_sender = EmailSender(smtp_server='smtp.example.com', smtp_port=587,
                                username=EMAIL_ADDRESS, password=EMAIL_PASSWORD)
    # 添加附件
    attachments = [
        keywords_png_path_all_14,
        keywords_png_path_broadcast_14,
        keywords_png_path_all_3mon,
        keywords_png_path_broadcast_3mon,
        province_frequency_png_path_all_14,
        province_frequency_png_path_broadcast_14,
        province_frequency_png_path_all_3mon,
        province_frequency_png_path_broadcast_3mon,
        wordcloud_png_path_all_14,
        wordcloud_png_path_broadcast_14,
        wordcloud_png_path_all_3mon,
        wordcloud_png_path_broadcast_3mon,
    ]
    
    email_sender.send_email(
            subject=f"新闻联播 ({today})", 
            body=markdown_content, 
            to_emails=TO_EMAILS, 
            attachments=attachments
        )
    logger.log_info("Email sent successfully.")


if __name__ == "__main__":
    main()