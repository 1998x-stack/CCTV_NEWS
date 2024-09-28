import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import warnings
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager

from config.config import FONT_PATH, DATA_CSV_PATH

from util.log_utils import logger
from util.news_heatmap import create_heatmap
from util.keywords_extractor import KeywordExtractor
from util.utils import load_data, extract_location_counts

warnings.filterwarnings("ignore")

font_manager.fontManager.addfont(FONT_PATH)
plt.rcParams['font.family'] = 'SimHei'


def visualize_keywords(df: pd.DataFrame, png_path: str=None):
    """ 可视化关键词频率
    Args:
        df: 包含关键词和频率的数据框
    """
    png_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'figures/keywords_bar_chart.png'
    ) if png_path is None else png_path
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

def visualize_locations(pro_data: pd.DataFrame, kind='province', png_path: str=None):
    pro_data = pro_data.head(30)
    png_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        f'figures/{kind}_bar_chart.png'
    ) if png_path is None else png_path
    plt.figure(figsize=(12, 6))
    plt.barh(pro_data[kind.capitalize()], pro_data['Count'], color='lightgreen')
    plt.title(f'{kind} 提及频次')
    plt.xlabel('提及频次')
    plt.ylabel(kind.capitalize())
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    return png_path


def visualize_word_cloud(df: pd.DataFrame, png_path: str=None):
    """ 构建关键词词云
    Args:
        df: 包含关键词的数据框
    """
    png_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'figures/word_cloud.png'
    ) if png_path is None else png_path
    text = ' '.join(df['keyword'])
    wordcloud = WordCloud(font_path=FONT_PATH, width=800, height=400, background_color='white').generate(text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud')
    plt.savefig(png_path)
    plt.close()
    return png_path

def visualize_keyword_trend(result_df: pd.DataFrame, top_n: int = 6, png_path: str = None) -> str:
    """可视化出现次数最多的前N个关键词的累积得分趋势。
    
    Args:
        result_df (pd.DataFrame): 包含关键词、日期和得分的数据框。
        top_n (int): 要显示的关键词数量，默认为5。
        png_path (str): 保存图表的文件路径，默认为None。
    
    Returns:
        str: 图表保存的文件路径。
    """
    # 检查数据框是否为空
    if result_df.empty:
        print("结果数据框为空，无法进行可视化。")
        return
    
    # 设置默认PNG路径
    png_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'figures/top_keywords_trend.png'
    ) if png_path is None else png_path
    
    # 统计每个关键词的得分并获取出现次数最多的前N个关键词
    keyword_stats = result_df.groupby('keyword').agg({'score': 'sum', 'date': 'count'}).reset_index()
    keyword_stats.columns = ['keyword', 'total_score', 'count']
    top_keywords = keyword_stats.nlargest(top_n, 'count')['keyword'].tolist()

    # 获取最小和最大日期
    min_date = result_df['date'].min()
    max_date = result_df['date'].max()

    # 创建日期范围
    all_dates = pd.date_range(start=min_date, end=max_date)

    # 创建可视化
    plt.figure(figsize=(12, 7))
    
    for keyword in top_keywords:
        # 过滤数据
        keyword_data = result_df[result_df['keyword'] == keyword]
        
        # 按日期汇总得分
        keyword_data = (keyword_data.groupby('date')['score']
                        .sum()
                        .reindex(all_dates, fill_value=0)
                        .reset_index(name='score'))
        
        # 计算累积得分
        keyword_data['cumulative_score'] = keyword_data['score'].cumsum()
        keyword_data.columns = ['date','score', 'cumulative_score']
        
        # 绘制线图
        plt.plot(keyword_data['date'], keyword_data['cumulative_score'], label=keyword)

    # 添加标题和标签
    plt.title(f'Trend of Top {top_n} Most Appeared Keywords', fontsize=16)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('累积得分', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.legend(title='关键词', fontsize=12)

    # 调整布局并保存图表
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    
    return png_path


def run_visualizations(
        file_path: str, 
        date_range: tuple = None,
        algorithm = "textrank",
        fields = ['title', 'content'],
        n_keywords: int = 10,
        result_data_path: str=None,
        keywords_png_path: str=None,
        top_keywords_trend_png_path: str=None,
        provinces_png_path: str=None,
        wordcloud_png_path: str=None,
        heatmap_html_path: str=None,
    ):
    """ 主程序，负责运行整个数据处理流程
    Args:
        file_path: 输入数据的CSV文件路径
    """
    # if result_data_path is not None and \
    #     keywords_png_path is not None and \
    #         top_keywords_trend_png_path is not None and \
    #             provinces_png_path is not None and \
    #                 wordcloud_png_path is not None and \
    #                     os.path.exists(result_data_path) and \
    #                         os.path.exists(keywords_png_path) and \
    #                             os.path.exists(top_keywords_trend_png_path) and \
    #                                 os.path.exists(provinces_png_path) and \
    #                                     os.path.exists(wordcloud_png_path):
    #     logger.log_info(f"Visualizations already exist at {result_data_path}, {keywords_png_path}, {provinces_png_path}, {wordcloud_png_path}. Skipping.")
    #     return pd.read_csv(result_data_path)
    
    # 初始化关键字分析器
    analyzer = KeywordExtractor(algorithm)
    logger.log_info(f"Keyword extractor initialized; Using {algorithm} algorithm.")
    df = load_data(file_path, date_range)
    # 按日期分组并聚合标题和内容
    grouped = df.groupby('date').agg({'title': '\n'.join, 'content': '\n'.join}).reset_index()
    logger.log_info(f"Data loaded from {file_path} between {date_range}")
    
    # 进行关键词分析
    result_data = []
    # 获取当前日期
    current_date = datetime.now()
    for idx, row in tqdm(grouped.iterrows(), total=len(grouped), desc="Extracting keywords"):
        txt = f'\n'.join(row[fields])
        keywords = analyzer.extract_keywords(txt, n_keywords=n_keywords)
        for keyword, score in keywords.items():
            # 根据日期调整分数：越新，分数越高
            age_days = (current_date - row['date']).days / 7
            adjusted_score = score * (1 / (age_days + 1))  # 越新分数越高
            result_data.append({'date': row['date'], 'keyword': keyword, 'score': adjusted_score})
    
    logger.log_info(f"Keyword extraction completed.")
    result_df = pd.DataFrame(result_data)
    # 关键词可视化
    keywords_png_path = visualize_keywords(result_df, keywords_png_path)
    logger.log_info(f"Keyword visualization saved to {keywords_png_path}")
    top_keywords_trend_png_path = visualize_keyword_trend(result_df=result_df, top_n=6, png_path=top_keywords_trend_png_path)
    logger.log_info(f"Top keywords trend visualization saved to {top_keywords_trend_png_path}")
    
    
    # 省份信息提取与可视化
    location_data = extract_location_counts(df, fields=fields)
    province_data = location_data['province']
    city_data = location_data['city']
    county_data = location_data['county']
    
    
    city_png_path = provinces_png_path.replace('province', 'city') if provinces_png_path else None
    county_png_path = provinces_png_path.replace('province', 'county') if provinces_png_path else None
    provinces_png_path = visualize_locations(province_data, kind='province', png_path=provinces_png_path)
    logger.log_info(f"Province visualization saved to {provinces_png_path}")
    city_png_path = visualize_locations(city_data, kind='city', png_path=city_png_path)
    logger.log_info(f"City visualization saved to {city_png_path}")
    county_png_path = visualize_locations(county_data, kind='county', png_path=county_png_path)
    logger.log_info(f"County visualization saved to {county_png_path}")
    
    
    province_heatmap_html_path = heatmap_html_path.replace('province', 'province') if heatmap_html_path else None
    city_heatmap_html_path = heatmap_html_path.replace('province', 'city') if heatmap_html_path else None
    county_heatmap_html_path = heatmap_html_path.replace('province', 'county') if heatmap_html_path else None
    create_heatmap(province_data, 'province', province_heatmap_html_path)
    logger.log_info(f"Province heatmap saved to {province_heatmap_html_path}")
    create_heatmap(city_data, 'city', city_heatmap_html_path)
    logger.log_info(f"City heatmap saved to {city_heatmap_html_path}")
    create_heatmap(county_data, 'county', county_heatmap_html_path)
    logger.log_info(f"County heatmap saved to {county_heatmap_html_path}")
    
    # 词云可视化
    wordcloud_png_path = visualize_word_cloud(result_df, wordcloud_png_path)
    logger.log_info(f"Word cloud visualization saved to {wordcloud_png_path}")
    
    if result_data_path:
        result_df.to_csv(result_data_path, index=False, encoding='utf8')
    
    return result_df

if __name__ == "__main__":
    run_visualizations(DATA_CSV_PATH, date_range=(20240922, 20240926))