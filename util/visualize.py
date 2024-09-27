import pandas as pd
import jieba
from collections import Counter
import cpca
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import font_manager


stopwords_zh_path = 'stopwords-zh.txt'
with open(stopwords_zh_path, 'r', encoding='utf-8') as file:
    stopwords_zh = file.read().splitlines()
stopwords_zh = set(stopwords_zh)

font_path = 'SimHei.ttf'
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'SimHei'

class KeywordAnalyzer:
    """ 关键字分析类 """

    def __init__(self, stopwords: list, blacklist: list):
        self.stopwords = stopwords
        self.blacklist = blacklist
        for word in self.stopwords:
            jieba.add_word(word)

    def analyze_keywords(self, content: str) -> dict:
        """ 分析关键词并返回计数 """
        words = [word for word in jieba.cut(content) if len(word) > 1 and word not in stopwords_zh]
        word_count = dict(Counter(words))
        return {k: v for k, v in word_count.items() if k not in self.blacklist}

def load_data(file_path: str) -> pd.DataFrame:
    """ 从CSV文件加载数据 """
    df = pd.read_csv(file_path, encoding='utf8')
    return df[df.content.notnull()]

def extract_provinces(data: pd.DataFrame) -> pd.DataFrame:
    """ 使用cpca包提取省份信息，并生成频率统计 """
    provinces = cpca.transform(data['content'].tolist())
    province_counts = provinces['省'].value_counts().reset_index()
    province_counts.columns = ['Province', 'Count']
    return province_counts

def visualize_keywords(df: pd.DataFrame):
    """ 可视化关键词频率 """
    plt.figure(figsize=(12, 6))
    top_keywords = df.groupby('keyword')['count'].sum().nlargest(80).reset_index()
    plt.barh(top_keywords['keyword'], top_keywords['count'], color='skyblue')
    plt.title('Top 80 Keywords')
    plt.xlabel('Frequency')
    plt.ylabel('Keywords')
    plt.tight_layout()
    plt.savefig('keywords_bar_chart.png')  # 保存关键词频率柱状图
    plt.show()

def visualize_provinces(pro_data: pd.DataFrame):
    """ 可视化省份频率 """
    plt.figure(figsize=(12, 6))
    plt.barh(pro_data['Province'], pro_data['Count'], color='lightgreen')
    plt.title('Province Frequency')
    plt.xlabel('Frequency')
    plt.ylabel('Province')
    plt.tight_layout()
    plt.savefig('province_bar_chart.png')  # 保存省份频率柱状图
    plt.show()

def build_word_cloud(df: pd.DataFrame):
    """ 构建并可视化词云 """
    text = ' '.join(df['keyword'])
    wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color='white').generate(text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # 不显示坐标轴
    plt.title('Word Cloud')
    plt.savefig('word_cloud.png')  # 保存词云图
    plt.show()

def main(file_path: str):
    """ 主函数 """
    # 定义黑名单和停用词
    blacklist = ['责任编辑', '一定', '一年', '一起', '一项', '一点儿', '一度', '一系列', '一道', '一次', 
                 '一亿', '进行', '实现', '已经', '指出', '为什么', '是不是', '”', '一个', '一些', 'cctv', 
                 '一边', '一部', '一致', '一窗', '万亿元', '亿元', '一致同意', '本台记住', '发生', 
                 '上述', '不仅', '不再', '下去', '首次', '合作', '发展', '国家', '加强', '共同', 
                 '重要', '我们', '你们', '他们', '目前', '领导人', '推进', '中方', '坚持', '支持', 
                 '表示', '时间', '协调', '制度', '工作', '强调', '推动', '通过', '北京时间', 
                 '有没有', '新闻联播', '本台消息', '这个', '那个', '就是', '今天', '明天', '参加', 
                 '今年', '明天']
    
    stopwords = ['一带一路', '雄安新区', '区块链', '数字货币', '虚拟货币', '比特币', '对冲基金', '自贸区', 
                  '自由贸易区', '乡村振兴', '美丽中国', '共享经济', '租购同权', '新零售', '共有产权房', 
                  '楼市调控', '产权保护', '互联网金融', '5G', '4G', '国企改革', '大湾区', '长江经济带']
    
    analyzer = KeywordAnalyzer(stopwords, blacklist)
    df = load_data(file_path)
    
    result_data = []
    
    for idx, row in df.iterrows():
        keywords = analyzer.analyze_keywords(row['content'])
        for keyword, count in keywords.items():
            result_data.append({'date': row['date'], 'keyword': keyword, 'count': count})
    
    result_df = pd.DataFrame(result_data)
    
    # 关键词可视化
    visualize_keywords(result_df)
    
    # 省份提取与可视化
    province_data = extract_provinces(df)
    visualize_provinces(province_data)
    
    # 构建词云
    build_word_cloud(result_df)

if __name__ == "__main__":
    main('data.csv')  # Update this path to your CSV file