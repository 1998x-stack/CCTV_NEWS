import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

PROXIES = {
    'https' : f"http://{os.environ['PROXY']}",
    'http' : f"http://{os.environ['PROXY']}",
} if 'PROXIES' in os.environ else {}

EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS'] if 'EMAIL_ADDRESS' in os.environ else ''
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD'] if 'EMAIL_PASSWORD' in os.environ else ''
TO_EMAILS = os.environ['TO_EMAILS'] if 'TO_EMAILS' in os.environ else ''
TO_EMAILS = TO_EMAILS.split(',')

BASIC_IMAGE_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'figures',
)

BASIC_DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'data',
)

# 停用词文件路径
BLACKWORDS_ZH_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'config/blackwords-zh.txt',
)
BLACKWORDS_EN_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'config/blackwords-en.txt',
)

# 字体路径，用于支持中文显示
FONT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'config/SimHei.ttf'
)

DATA_CSV_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'data/data.csv'
)
DATA_JSONL_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'data/data.jsonl'
)
Domestic_Broadcast_News_CSV_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'data/Domestic_Broadcast_News.csv'
)
Domestic_Broadcast_News_JSONL_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'data/Domestic_Broadcast_News.jsonl'
)

ALLOWED_WORDS = ['一带一路', '雄安新区', '区块链', '数字货币', '虚拟货币', '比特币', '对冲基金', '自贸区', 
                '自由贸易区', '乡村振兴', '美丽中国', '共享经济', '租购同权', '新零售', '共有产权房', 
                '楼市调控', '产权保护', '互联网金融', '5G', '4G', '国企改革', '大湾区', '长江经济带']