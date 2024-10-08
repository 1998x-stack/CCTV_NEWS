import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from datetime import datetime, timedelta
from typing import List, Dict, Optional


from config.config import (
    PROXIES,
    DATA_CSV_PATH,
    DATA_JSONL_PATH,
    DOMESTIC_BROADCAST_NEWS_CSV_PATH,
    DOMESTIC_BROADCAST_NEWS_JSONL_PATH,
)
from util.log_utils import logger
from util.video_data_collector import VideoDataCollector
from util.utils import (
    get_last_jsonl_record_safe,
    append_to_jsonl,
    append_to_csv,
    compare_dates,
)

def update_data_files(collected_data: List[Dict], csv_path: str, jsonl_path: str) -> None:
    """
    Update CSV and JSONL files with collected data if it's newer than existing data.

    Args:
        collected_data (List[Dict]): List of dictionaries containing collected news data.
        csv_path (str): Path to the CSV file to be updated.
        jsonl_path (str): Path to the JSONL file to be updated.
    """
    if not collected_data:
        return

    try:
        last_json: Optional[Dict] = get_last_jsonl_record_safe(jsonl_path)
        last_date: Optional[str] = last_json.get('date') if last_json else None

        if last_date and compare_dates(collected_data[0]['date'], last_date):
            append_to_csv(collected_data, csv_path)
            append_to_jsonl(collected_data, jsonl_path)
        elif not last_date:
            append_to_csv(collected_data, csv_path)
            append_to_jsonl(collected_data, jsonl_path)
    except Exception:
        logger.log_exception()

def collect_daily_news(target_date: str) -> List[Dict]:
    """
    Collect news data for a specific date and update relevant files.

    Args:
        target_date (str): The date for which to collect news, in 'YYYY-MM-DD' format.

    Returns:
        List[Dict]: Collected news data as a list of dictionaries.
    """
    try:
        video_data_collector = VideoDataCollector(
            start_date=target_date,
            end_date=target_date,
            proxies=PROXIES
        )
        collected_data = video_data_collector.collect_all_data()

        if not collected_data:
            logger.log_info(f"No data collected for {target_date}.")
            previous_day = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            video_data_collector = VideoDataCollector(
                start_date=previous_day,
                end_date=previous_day,
                proxies=PROXIES
            )
            collected_data = video_data_collector.collect_all_data()

        domestic_broadcast_news = [
            data for data in collected_data if data['title'] == '国内联播快讯'
        ]

        update_data_files(collected_data, DATA_CSV_PATH, DATA_JSONL_PATH)
        update_data_files(
            domestic_broadcast_news,
            DOMESTIC_BROADCAST_NEWS_CSV_PATH,
            DOMESTIC_BROADCAST_NEWS_JSONL_PATH
        )

        logger.log_info(f"Data for {target_date} collected and saved.")
        return collected_data
    except Exception:
        logger.log_exception()
        return []

if __name__ == '__main__':
    today_date = datetime.now().strftime("%Y-%m-%d")
    logger.log_info(f"Today is: {today_date}")
    collect_daily_news(today_date)