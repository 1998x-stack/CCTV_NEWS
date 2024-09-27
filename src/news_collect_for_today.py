import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from datetime import datetime

from config.config import PROXIES
from util.log_utils import logger
from util.video_data_collector import VideoDataCollector
from util.utils import get_last_jsonl_record_safe, append_to_jsonl, append_to_csv, compare_dates
from config.config import DATA_CSV_PATH, DATA_JSONL_PATH, Domestic_Broadcast_News_CSV_PATH, Domestic_Broadcast_News_JSONL_PATH

def modify_csv_and_jsonl(collected_data, csv_path, jsonl_path):
    last_json = get_last_jsonl_record_safe(jsonl_path)
    last_date = last_json.get('date') if last_json else None
    if last_date:
        if compare_dates(collected_data[0]['date'], last_date):
            append_to_csv(collected_data, csv_path)
            append_to_jsonl(collected_data, jsonl_path)
    else:
        append_to_csv(collected_data, csv_path)
        append_to_jsonl(collected_data, jsonl_path)

def collect_news(day):
    try:
        video_data_collector = VideoDataCollector(start_date=day, end_date=day, proxies=PROXIES)
        collected_data = video_data_collector.collect_all_data()
        logger.log_info(f"Collected data for {day}: {collected_data}")
        collected_domestic_broadcast_news = [data for data in collected_data if data['title'] == '国内联播快讯']
        modify_csv_and_jsonl(collected_data, DATA_CSV_PATH, DATA_JSONL_PATH)
        modify_csv_and_jsonl(collected_domestic_broadcast_news, Domestic_Broadcast_News_CSV_PATH, Domestic_Broadcast_News_JSONL_PATH)
        logger.log_info(f"Data for {day} collected and saved.")
        return collected_data
    except:
        logger.log_exception()
        return []

if __name__ == '__main__':
    today = datetime.now().strftime("%Y-%m-%d")
    logger.log_info(f"Today is: {today}")
    collect_news(today)