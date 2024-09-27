import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import cpca
import warnings
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager

from config.config import FONT_PATH, DATA_CSV_PATH

from util.log_utils import logger
from util.utils import load_data
from util.keywords_extractor import KeywordExtractor

warnings.filterwarnings("ignore")
font_manager.fontManager.addfont(FONT_PATH)
plt.rcParams['font.family'] = 'SimHei'

def extract_provinces(data: pd.DataFrame, fields = ['title', 'content']) -> pd.DataFrame:
    """ 使用cpca提取省份信息
    Args:
        data: 包含文本内容的数据框
    Returns:
        包含省份统计结果的数据框
    """
    texts = data[fields].apply(lambda x:'\n'.join(x), axis=1)
    provinces = cpca.transform(texts.tolist())
    # provinces = cpca.transform(data['content'].tolist())
    province_counts = provinces['省'].value_counts().reset_index()
    province_counts.columns = ['Province', 'Count']
    return province_counts


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
    plt.figure(figsize=(12, 6))
    top_keywords = df.groupby('keyword')['score'].sum().nlargest(40).reset_index()
    plt.barh(top_keywords['keyword'], top_keywords['score'], color='skyblue')
    plt.title('Top 40 Keywords')
    plt.xlabel('Frequency')
    plt.ylabel('Keywords')
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    return png_path


def visualize_provinces(pro_data: pd.DataFrame, png_path: str=None):
    """ 可视化省份频率
    Args:
        pro_data: 包含省份和频率的数据框
    """
    png_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'figures/province_bar_chart.png'
    ) if png_path is None else png_path
    plt.figure(figsize=(12, 6))
    plt.barh(pro_data['Province'], pro_data['Count'], color='lightgreen')
    plt.title('Province Frequency')
    plt.xlabel('Frequency')
    plt.ylabel('Province')
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


def run_visualizations(
        file_path: str, 
        date_range: tuple = None,
        algorithm = "textrank",
        fields = ['title', 'content'],
        n_keywords: int = 10,
        result_data_path: str=None,
        keywords_png_path: str=None,
        provinces_png_path: str=None,
        wordcloud_png_path: str=None,
    ):
    """ 主程序，负责运行整个数据处理流程
    Args:
        file_path: 输入数据的CSV文件路径
    """
    
    # 初始化关键字分析器
    analyzer = KeywordExtractor(algorithm)
    logger.log_info(f"Keyword extractor initialized; Using {algorithm} algorithm.")
    df = load_data(file_path, date_range)
    logger.log_info(f"Data loaded from {file_path} between {date_range}")
    
    # 进行关键词分析
    result_data = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Extracting keywords"):
        txt = '\n'.join(row[fields])
        keywords = analyzer.extract_keywords(txt, n_keywords=n_keywords)
        for keyword, score in keywords.items():
            result_data.append({'date': row['date'], 'keyword': keyword, 'score': score})
    
    logger.log_info(f"Keyword extraction completed.")
    
    result_df = pd.DataFrame(result_data)
    # 关键词可视化
    keywords_png_path = visualize_keywords(result_df, keywords_png_path)
    logger.log_info(f"Keyword visualization saved to {keywords_png_path}")
    # 省份信息提取与可视化
    province_data = extract_provinces(df, fields=fields)
    provinces_png_path = visualize_provinces(province_data, provinces_png_path)
    logger.log_info(f"Province visualization saved to {provinces_png_path}")
    # 词云可视化
    wordcloud_png_path = visualize_word_cloud(result_df, wordcloud_png_path)
    logger.log_info(f"Word cloud visualization saved to {wordcloud_png_path}")
    
    if result_data_path:
        result_df.to_csv(result_data_path, index=False, encoding='utf8')
    
    return result_df

if __name__ == "__main__":
    run_visualizations(DATA_CSV_PATH, date_range=(20240920, 20240926))  # 请将此路径更新为实际的CSV文件路径