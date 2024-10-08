import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from typing import List, Dict, Tuple, Optional
import warnings
from datetime import datetime

import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from wordcloud import WordCloud
from matplotlib import font_manager


from config.config import FONT_PATH, DATA_CSV_PATH
from util.log_utils import logger
from util.news_heatmap import create_heatmap
from util.keywords_extractor import KeywordExtractor
from util.utils import load_and_filter_data, extract_location_counts

warnings.filterwarnings("ignore")
font_manager.fontManager.addfont(FONT_PATH)
plt.rcParams['font.family'] = 'SimHei'


def visualize_keywords(df: pd.DataFrame, png_path: Optional[str] = None) -> str:
    """
    Visualize keyword frequencies.

    Args:
        df (pd.DataFrame): DataFrame containing keywords and their frequencies.
        png_path (Optional[str]): Path to save the PNG file. If None, a default path is used.

    Returns:
        str: Path to the saved PNG file.
    """
    if png_path is None:
        png_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'figures/keywords_bar_chart.png'
        )
    
    plt.figure(figsize=(15, 10))
    top_keywords = df.groupby('keyword')['score'].sum().nlargest(40).reset_index()
    plt.barh(top_keywords['keyword'], top_keywords['score'], color='skyblue')
    plt.title('新闻联播核心词')
    plt.xlabel('分数')
    plt.ylabel('关键词')
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    
    return png_path


def visualize_keyword_trend(result_df: pd.DataFrame, top_n: int = 6, png_path: Optional[str] = None) -> str:
    """
    Visualize the cumulative score trend of the top N keywords.

    Args:
        result_df (pd.DataFrame): DataFrame containing keywords, dates, and scores.
        top_n (int): Number of top keywords to display. Defaults to 6.
        png_path (Optional[str]): Path to save the PNG file. If None, a default path is used.

    Returns:
        str: Path to the saved PNG file.
    """
    if result_df.empty:
        logger.log_info("Result DataFrame is empty, visualization cannot be performed.")
        return ""

    if png_path is None:
        png_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'figures/top_keywords_trend.png'
        )
    
    min_date, max_date = result_df['date'].min(), result_df['date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date)
    
    keyword_stats = result_df.groupby('keyword').agg({'score': 'sum', 'date': 'count'}).reset_index()
    keyword_stats.columns = ['keyword', 'total_score', 'count']
    top_keywords = keyword_stats.nlargest(top_n, 'count')['keyword'].tolist()
    
    plt.figure(figsize=(15, 8))
    for keyword in top_keywords:
        keyword_data = result_df[result_df['keyword'] == keyword]
        keyword_data = (keyword_data.groupby('date')['score']
                        .sum()
                        .reindex(all_dates, fill_value=0)
                        .reset_index(name='score'))
        keyword_data['cumulative_score'] = keyword_data['score'].cumsum()
        plt.plot(keyword_data['date'], keyword_data['cumulative_score'], label=keyword)
    
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
    
    plt.title(f'Top {top_n} 新闻联播核心关键词趋势走向', fontsize=16)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('累积得分', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.legend(title='关键词', fontsize=12)
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    
    return png_path


def visualize_word_cloud(df: pd.DataFrame, png_path: Optional[str] = None) -> str:
    """
    Generate a word cloud visualization from keywords.

    Args:
        df (pd.DataFrame): DataFrame containing keywords and their scores.
        png_path (Optional[str]): Path to save the PNG file. If None, a default path is used.

    Returns:
        str: Path to the saved PNG file.
    """
    if png_path is None:
        png_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'figures/word_cloud.png'
        )
    
    try:
        frequencies = dict(zip(df['keyword'], df['score']))
        wordcloud = WordCloud(
            font_path=FONT_PATH, 
            width=800, 
            height=400, 
            background_color='white'
        ).generate_from_frequencies(frequencies)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('新闻联播关键词词云', fontsize=16)
        plt.savefig(png_path)
        plt.close()
        
        return png_path
    
    except KeyError as e:
        logger.log_error(f"Error: Missing column in DataFrame - {e}")
        return ""
    except Exception as e:
        logger.log_error(f"Error occurred: {e}")
        return ""


def visualize_locations(location_data: pd.DataFrame, location_type: str = 'province', png_path: Optional[str] = None) -> str:
    """
    Visualize location mention frequencies.

    Args:
        location_data (pd.DataFrame): DataFrame containing location data and counts.
        location_type (str): Type of location (province, city, or county). Defaults to 'province'.
        png_path (Optional[str]): Path to save the PNG file. If None, a default path is used.

    Returns:
        str: Path to the saved PNG file.
    """
    location_data = location_data.head(30)
    
    if png_path is None:
        png_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            f'figures/{location_type}_bar_chart.png'
        )
    
    plt.figure(figsize=(12, 8))
    plt.barh(location_data[location_type.capitalize()], location_data['Count'], color='lightgreen')
    plt.title(f'{location_type.capitalize()}提及频次')
    plt.xlabel('提及频次')
    plt.ylabel(location_type.capitalize())
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    
    return png_path


def run_visualizations(
    file_path: str,
    date_range: Optional[Tuple[str, str]] = None,
    algorithm: str = "textrank",
    fields: List[str] = ['title', 'content'],
    n_keywords: int = 10,
    result_data_path: Optional[str] = None,
    keywords_png_path: Optional[str] = None,
    top_keywords_trend_png_path: Optional[str] = None,
    provinces_png_path: Optional[str] = None,
    wordcloud_png_path: Optional[str] = None,
    heatmap_html_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Run the entire data processing and visualization pipeline.

    Args:
        file_path (str): Path to the input CSV file.
        date_range (Optional[Tuple[str, str]]): Date range for filtering data.
        algorithm (str): Algorithm to use for keyword extraction. Defaults to "textrank".
        fields (List[str]): Fields to use for keyword extraction. Defaults to ['title', 'content'].
        n_keywords (int): Number of keywords to extract. Defaults to 10.
        result_data_path (Optional[str]): Path to save the result data.
        keywords_png_path (Optional[str]): Path to save the keywords visualization.
        top_keywords_trend_png_path (Optional[str]): Path to save the top keywords trend visualization.
        provinces_png_path (Optional[str]): Path to save the provinces visualization.
        wordcloud_png_path (Optional[str]): Path to save the word cloud visualization.
        heatmap_html_path (Optional[str]): Path to save the heatmap HTML file.

    Returns:
        pd.DataFrame: DataFrame containing the extracted keywords and their scores.
    """
    analyzer = KeywordExtractor(algorithm)
    logger.log_info(f"Keyword extractor initialized; Using {algorithm} algorithm.")
    
    df = load_and_filter_data(file_path, date_range)
    logger.log_info(f"Data loaded from {file_path} between {date_range}")
    
    result_data = []
    current_date = datetime.now()
    grouped = df.groupby('date').agg({'title': '\n'.join, 'content': '\n'.join}).reset_index()
    
    for _, row in tqdm(grouped.iterrows(), total=len(grouped), desc="Extracting keywords"):
        txt = '\n'.join(row[fields])
        keywords = analyzer.extract_keywords(txt, n_keywords=n_keywords)
        for keyword, score in keywords.items():
            age_days = (current_date - row['date']).days / 7
            adjusted_score = score * (1 / (age_days + 1))
            result_data.append({'date': row['date'], 'keyword': keyword, 'score': adjusted_score})
    
    result_df = pd.DataFrame(result_data)
    logger.log_info("Keyword extraction completed.")
    
    keywords_png_path = visualize_keywords(result_df, keywords_png_path)
    logger.log_info(f"Keyword visualization saved to {keywords_png_path}")
    
    top_keywords_trend_png_path = visualize_keyword_trend(result_df, top_n=6, png_path=top_keywords_trend_png_path)
    logger.log_info(f"Top keywords trend visualization saved to {top_keywords_trend_png_path}")
    
    wordcloud_png_path = visualize_word_cloud(result_df, wordcloud_png_path)
    logger.log_info(f"Word cloud visualization saved to {wordcloud_png_path}")
    
    location_data = extract_location_counts(df, fields=fields)
    for location_type, data in location_data.items():
        png_path = provinces_png_path.replace('province', location_type) if provinces_png_path else None
        png_path = visualize_locations(data, location_type, png_path)
        logger.log_info(f"{location_type.capitalize()} visualization saved to {png_path}")
        
        heatmap_path = heatmap_html_path.replace('province', location_type) if heatmap_html_path else None
        heatmap_path = create_heatmap(data, location_type, heatmap_path)
        logger.log_info(f"{location_type.capitalize()} heatmap saved to {heatmap_path}")
    
    if result_data_path:
        result_df.to_csv(result_data_path, index=False, encoding='utf8')
    
    return result_df


if __name__ == "__main__":
    run_visualizations(DATA_CSV_PATH, date_range=('20240922', '20240926'))