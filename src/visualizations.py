
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager

class Visualizations:
    """可视化类，用于生成词云和频率图表"""

    def __init__(self, font_path: str):
        """初始化可视化类
        
        Args:
            font_path: 用于中文字体的路径
        """
        self.font_path = font_path

    def visualize_keywords(self, df: pd.DataFrame, save_path: str) -> None:
        """可视化关键词频率
        
        Args:
            df: 包含关键词及其频率的数据框
            save_path: 保存图表的路径
        """
        plt.figure(figsize=(12, 6))
        top_keywords = df.groupby('keyword')['count'].sum().nlargest(80).reset_index()
        sns.barplot(x='count', y='keyword', data=top_keywords)
        plt.title('Top 80 Keywords', fontproperties=font_manager.FontProperties(fname=self.font_path))
        plt.xlabel('Frequency', fontproperties=font_manager.FontProperties(fname=self.font_path))
        plt.ylabel('Keywords', fontproperties=font_manager.FontProperties(fname=self.font_path))
        plt.tight_layout()
        plt.savefig(save_path)  # 保存关键词频率柱状图
        plt.close()

    def visualize_provinces(self, pro_data: pd.DataFrame, save_path: str) -> None:
        """可视化省份频率
        
        Args:
            pro_data: 包含省份及其频率的数据框
            save_path: 保存图表的路径
        """
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Count', y='Province', data=pro_data)
        plt.title('Province Frequency', fontproperties=font_manager.FontProperties(fname=self.font_path))
        plt.xlabel('Frequency', fontproperties=font_manager.FontProperties(fname=self.font_path))
        plt.ylabel('Province', fontproperties=font_manager.FontProperties(fname=self.font_path))
        plt.tight_layout()
        plt.savefig(save_path)  # 保存省份频率柱状图
        plt.close()

    def build_word_cloud(self, keywords: list, save_path: str) -> None:
        """构建并可视化词云
        
        Args:
            keywords: 关键词列表
            save_path: 保存词云图的路径
        """
        text = ' '.join(keywords)
        wordcloud = WordCloud(font_path=self.font_path, width=800, height=400, background_color='white').generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')  # 不显示坐标轴
        plt.title('Word Cloud', fontproperties=font_manager.FontProperties(fname=self.font_path))
        plt.savefig(save_path)  # 保存词云图
        plt.close()