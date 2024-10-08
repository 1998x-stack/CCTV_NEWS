import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
from datetime import datetime, timedelta
from typing import List, Dict

from config.config import (
    EMAIL_ADDRESS, EMAIL_PASSWORD, TO_EMAILS, DATA_CSV_PATH,
    DOMESTIC_BROADCAST_NEWS_CSV_PATH, BASIC_DATA_DIR, BASIC_IMAGE_DIR, TARGET_TIME
)
from src.news_collect_for_today import collect_daily_news
from util.log_utils import logger
from util.email_sender import EmailSender
from util.task_scheduler import TimezoneAwareScheduler
from util.markdown_formatter import MarkdownFormatter
from util.visualizations import run_visualizations


def create_directory_structure() -> None:
    """Create the necessary directory structure for storing visualizations."""
    logger.log_info("Creating directory structure for visualizations...")
    base_dirs = [
        os.path.join(BASIC_IMAGE_DIR, 'all'),
        os.path.join(BASIC_IMAGE_DIR, 'domestic_broadcast_news')
    ]
    sub_dirs = ['heatmap', 'keywords', 'keywords_trend', 'location', 'wordCloud']

    for base_dir in base_dirs:
        for sub_dir in sub_dirs:
            dir_path = os.path.join(base_dir, sub_dir)
            os.makedirs(dir_path, exist_ok=True)
            logger.log_info(f"Created directory: {dir_path}")
    logger.log_info("Directory structure creation completed.")


def generate_file_paths(base_dir: str, prefix: str, start_date: str, end_date: str) -> Dict[str, str]:
    """
    Generate file paths for visualization outputs.

    Args:
        base_dir (str): Base directory for the files.
        prefix (str): Prefix for the file names.
        start_date (str): Start date of the data range.
        end_date (str): End date of the data range.

    Returns:
        Dict[str, str]: Dictionary containing file paths for different visualizations.
    """
    logger.log_info(f"Generating file paths for {base_dir} {prefix} from {start_date} to {end_date}")
    file_paths = {
        'result_data': os.path.join(BASIC_DATA_DIR, base_dir, f'result_data_{prefix}_{start_date}_{end_date}.csv'),
        'keywords': os.path.join(BASIC_IMAGE_DIR, base_dir, 'keywords', f'keywords_png_{prefix}_{start_date}_{end_date}.png'),
        'keywords_trend': os.path.join(BASIC_IMAGE_DIR, base_dir, 'keywords_trend', f'top_keywords_trend_png_{prefix}_{start_date}_{end_date}.png'),
        'province_frequency': os.path.join(BASIC_IMAGE_DIR, base_dir, 'location', f'province_frequency_png_{prefix}_{start_date}_{end_date}.png'),
        'wordcloud': os.path.join(BASIC_IMAGE_DIR, base_dir, 'wordCloud', f'wordcloud_png_{prefix}_{start_date}_{end_date}.png'),
        'heatmap': os.path.join(BASIC_IMAGE_DIR, base_dir, 'heatmap', f'province_heatmap_html_{prefix}_{start_date}_{end_date}.html'),
    }
    logger.log_info(f"File paths generated: {file_paths}")
    return file_paths


def run_visualization_for_period(file_path: str, date_range: tuple, file_paths: Dict[str, str]) -> None:
    """
    Run visualizations for a specific period and save the results.

    Args:
        file_path (str): Path to the input CSV file.
        date_range (tuple): Tuple containing start and end dates.
        file_paths (Dict[str, str]): Dictionary containing output file paths.
    """
    logger.log_info(f"Running visualizations for period {date_range[0]} to {date_range[1]}")
    logger.log_info(f"Input file: {file_path}")
    logger.log_info(f"Output files: {file_paths}")
    
    run_visualizations(
        file_path=file_path,
        date_range=date_range,
        algorithm="textrank",
        fields=['title', 'content'],
        n_keywords=40,
        result_data_path=file_paths['result_data'],
        keywords_png_path=file_paths['keywords'],
        top_keywords_trend_png_path=file_paths['keywords_trend'],
        provinces_png_path=file_paths['province_frequency'],
        wordcloud_png_path=file_paths['wordcloud'],
        heatmap_html_path=file_paths['heatmap'],
    )
    logger.log_info(f"Visualizations completed for period {date_range[0]} to {date_range[1]}")


def main() -> None:
    """Main function to collect news, generate visualizations, and send email."""
    logger.log_info("Starting main function execution")
    
    today = datetime.now().strftime("%Y%m%d")
    day_14_before = (datetime.now() - timedelta(days=14)).strftime("%Y%m%d")
    day_3mon_before = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
    logger.log_info(f"Date ranges: Today: {today}, 14 days ago: {day_14_before}, 3 months ago: {day_3mon_before}")

    logger.log_info("Collecting daily news...")
    collected_data = collect_daily_news(today)
    logger.log_info(f"Collected {len(collected_data)} news items")

    logger.log_info("Generating markdown content...")
    markdown_content = MarkdownFormatter.format_news(collected_data)
    logger.log_info("Markdown content generated.")

    create_directory_structure()

    # Generate visualizations for different periods and data types
    visualization_configs = [
        ('all', DATA_CSV_PATH, '14', (day_14_before, today)),
        ('domestic_broadcast_news', DOMESTIC_BROADCAST_NEWS_CSV_PATH, '14', (day_14_before, today)),
        ('all', DATA_CSV_PATH, '3mon', (day_3mon_before, today)),
        ('domestic_broadcast_news', DOMESTIC_BROADCAST_NEWS_CSV_PATH, '3mon', (day_3mon_before, today)),
    ]

    logger.log_info("Starting visualization generation...")
    all_file_paths = []
    for base_dir, file_path, prefix, date_range in visualization_configs:
        logger.log_info(f"Processing visualization for {base_dir} {prefix}")
        file_paths = generate_file_paths(base_dir, prefix, date_range[0], date_range[1])
        run_visualization_for_period(file_path, date_range, file_paths)
        all_file_paths.append(file_paths)
        logger.log_info(f"Visualizations for {prefix} period in {base_dir} completed.")

    # Prepare email attachments
    logger.log_info("Preparing email attachments...")
    html_attachments = [paths['heatmap'] for paths in all_file_paths]
    html_attachments.extend([path.replace('province', 'city') for path in html_attachments])
    html_attachments.extend([path.replace('province', 'county') for path in html_attachments])
    logger.log_info(f"HTML attachments prepared: {len(html_attachments)} files")

    attachments = []
    for paths in all_file_paths:
        attachments.extend([paths['keywords'], paths['wordcloud'], paths['keywords_trend'], paths['province_frequency']])
        attachments.extend([paths['province_frequency'].replace('province', 'city')])
        attachments.extend([paths['province_frequency'].replace('province', 'county')])
    logger.log_info(f"Image attachments prepared: {len(attachments)} files")

    # Send email
    logger.log_info("Initializing email sender...")
    email_sender = EmailSender(smtp_server='smtp.gmail.com', smtp_port=587,
                               username=EMAIL_ADDRESS, password=EMAIL_PASSWORD)
    logger.log_info("Sending email...")
    email_sender.send_email(
        subject=f"《新闻联播》 ({today})",
        body=markdown_content,
        to_emails=TO_EMAILS,
        html_attachments=html_attachments,
        attachments=attachments
    )
    logger.log_info("Email sent successfully.")
    logger.log_info("Main function execution completed.")


if __name__ == "__main__":
    logger.log_info("Script execution started")
    main()
    logger.log_info("Script execution completed")
    # Uncomment the following lines to use the scheduler
    # logger.log_info("Initializing task scheduler")
    # task_scheduler = TimezoneAwareScheduler(target_time=TARGET_TIME)
    # logger.log_info(f"Starting scheduler with target time: {TARGET_TIME}")
    # task_scheduler.start_scheduler(main)