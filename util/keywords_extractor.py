# coding=utf-8
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import pke
import jieba
import warnings
from typing import List, Tuple

warnings.filterwarnings("ignore")

from config.config import BLACKWORDS_ZH_PATH, ALLOWED_WORDS

class KeywordExtractor:
    """关键词抽取类，支持 TF-IDF、TextRank 和 YAKE 等算法。

    Attributes:
        algorithm: str 指定关键词抽取算法的名称。
        stopwords: List[str] 停用词列表，用于过滤无关词汇。
    """

    def __init__(self, algorithm: str, stopword_path: str=BLACKWORDS_ZH_PATH):
        """
        初始化关键词提取器，选择算法并加载停用词。

        Args:
            algorithm: str 关键词提取算法，支持 'tfidf', 'textrank', 'yake'。
            stopword_path: str 停用词文件路径，用于加载停用词列表。
        """
        self.algorithm = algorithm.lower()
        self.stopwords = self._load_stopwords(stopword_path)
        self._check_algorithm()
        for word in ALLOWED_WORDS:
            jieba.add_word(word)  # 将停用词加入结巴分词的词典

    def _load_stopwords(self, stopword_path: str) -> List[str]:
        """加载停用词列表。

        Args:
            stopword_path: str 停用词文件的路径。

        Returns:
            List[str]: 停用词列表。
        """
        try:
            with open(stopword_path, 'r', encoding='utf-8') as file:
                stopwords = [line.strip() for line in file.readlines()]
            return set(stopwords)
        except FileNotFoundError:
            raise FileNotFoundError(f"Stopword file not found at {stopword_path}")

    def _check_algorithm(self):
        """检查算法参数是否有效。"""
        valid_algorithms = ['tfidf', 'textrank', 'yake']
        if self.algorithm not in valid_algorithms:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}. Supported algorithms are {valid_algorithms}")

    def _preprocess_text(self, text: str) -> str:
        """使用 jieba 对中文文本进行分词。

        Args:
            text: str 输入的原始文本。

        Returns:
            str: 分词后的文本，以空格分隔。
        """
        return ' '.join(jieba.cut(text))
        # tokens = pseg.cut(text)
        # return ' '.join([token for token, pos in tokens if pos.startswith('n')])

    def extract_keywords(self, text: str, n_keywords: int = 50) -> List[Tuple[str, float]]:
        """根据选择的算法提取关键词。

        Args:
            text: str 输入的文本。
            n_keywords: int 返回的关键词数量。

        Returns:
            List[Tuple[str, float]]: 提取的关键词及其对应的权重。
        """
        # 文本预处理
        processed_text = self._preprocess_text(text)

        # 根据算法进行关键词提取
        if self.algorithm == 'tfidf':
            keywords = self._extract_tfidf(processed_text, n_keywords)
        elif self.algorithm == 'textrank':
            keywords = self._extract_textrank(processed_text, n_keywords)
        elif self.algorithm == 'yake':
            keywords = self._extract_yake(processed_text, n_keywords)
        
        for word, score in keywords:
            if word in self.stopwords:
                keywords.remove((word, score))
        return {word.replace(' ', ''): score for word, score in keywords if word.replace(' ', '') not in self.stopwords}

    def _extract_tfidf(self, text: str, n_keywords: int) -> List[Tuple[str, float]]:
        """使用 TF-IDF 提取关键词。"""
        extractor = pke.unsupervised.TfIdf()
        extractor.load_document(input=text, language='zh', stoplist=self.stopwords)
        extractor.candidate_selection()
        extractor.candidate_weighting()
        return extractor.get_n_best(n=n_keywords)

    def _extract_textrank(self, text: str, n_keywords: int) -> List[Tuple[str, float]]:
        """使用 TextRank 提取关键词。"""
        extractor = pke.unsupervised.TextRank()
        extractor.load_document(input=text, language='zh', stoplist=self.stopwords)
        extractor.candidate_selection()
        extractor.candidate_weighting()
        return extractor.get_n_best(n=n_keywords)

    def _extract_yake(self, text: str, n_keywords: int) -> List[Tuple[str, float]]:
        """使用 YAKE 提取关键词。"""
        extractor = pke.unsupervised.YAKE()
        extractor.load_document(input=text, language='zh', stoplist=self.stopwords)
        extractor.candidate_selection()
        extractor.candidate_weighting()
        return extractor.get_n_best(n=n_keywords)

# 使用示例
if __name__ == "__main__":
    text = "自然语言处理是计算机科学领域及人工智能领域中的一个重要方向。"
    extractor = KeywordExtractor(algorithm='textrank', stopword_path=BLACKWORDS_ZH_PATH)
    keywords = extractor.extract_keywords(text, n_keywords=5)
    from pprint import pprint
    pprint(keywords)