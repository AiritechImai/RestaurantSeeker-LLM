import os
from dotenv import load_dotenv

# .env ファイルの読み込み
load_dotenv()

class Config:
    # LLM設定
    LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', 'http://localhost:11434/api/generate')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-oss-20b')
    
    # ホットペッパーAPI設定
    HOTPEPPER_API_KEY = os.getenv('HOTPEPPER_API_KEY', '')
    HOTPEPPER_API_URL = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
    
    # 食べログAPI設定 
    TABELOG_API_KEY = os.getenv('TABELOG_API_KEY', '')
    TABELOG_API_URL = 'https://api.gnavi.co.jp/RestSearchAPI/v3/'  # 実際のURLは要確認
    
    # HTTP設定
    REQUEST_TIMEOUT = 10
    REQUEST_DELAY = 1
    USER_AGENT = 'RestaurantSeeker/1.0'
    
    # デフォルト検索パラメータ
    DEFAULT_MAX_RESULTS = 20
    
    # ホットペッパー料理ジャンルコード（実際のAPIレスポンスに基づく）
    HOTPEPPER_GENRE_CODES = {
        '居酒屋': 'G001',
        'ダイニングバー': 'G002', 
        '創作料理': 'G003',
        '和食': 'G004',
        '洋食': 'G005',
        'イタリアン': 'G006',
        '中華': 'G007',  # 実際のAPIレスポンスで確認済み
        'フレンチ': 'G008',  # 仮設定 - 要確認
        '焼肉・ホルモン': 'G009',
        'アジア・エスニック料理': 'G010',
        '各国料理': 'G011',
        'カラオケ・パーティ': 'G012',
        'バー・カクテル': 'G013',
        'カフェ・スイーツ': 'G014',
        'その他グルメ': 'G015',
        'ラーメン': 'G016',
        'お好み焼き・もんじゃ': 'G017',
        '韓国料理': 'G017',  
        '寿司': 'G004',  # 和食カテゴリ内
        '焼肉': 'G009'  # 焼肉・ホルモンの短縮形
    }
    
    # ホットペッパーエリアコード（実際のコード）
    HOTPEPPER_AREA_CODES = {
        '新宿': 'Y005',  # 新宿の正しいコード
        '渋谷': 'Y006', 
        '池袋': 'Y007',
        '銀座': 'Y008',
        '六本木': 'Y009',
        '恵比寿': 'Y010',
        '品川': 'Y011',
        '上野': 'Y012',
        '浅草': 'Y013',
        '秋葉原': 'Y014',
        '横浜': 'Y020'
    }
    
    # API設定
    OPENBD_API = 'https://api.openbd.jp/v1/get'
    CALIL_API = 'http://api.calil.jp/check'
    RAKUTEN_API_KEY = os.getenv('RAKUTEN_API_KEY', '')
    
    # スクレイピング設定
    SCRAPING_DELAY = 2  # サイト間のリクエスト間隔（秒）
    REQUEST_TIMEOUT = 10  # リクエストタイムアウト（秒）
    
    # HTTP設定
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # 対象ECサイト設定
    SCRAPING_SITES = {
        'amazon': {
            'name': 'Amazon',
            'search_url': 'https://www.amazon.co.jp/s?k={isbn}',
            'enabled': True
        },
        'rakuten': {
            'name': '楽天',
            'search_url': 'https://search.rakuten.co.jp/search/mall/{isbn}/',
            'enabled': True
        },
        'bookoff': {
            'name': 'ブックオフオンライン',
            'search_url': 'https://www.bookoffonline.co.jp/old/0016/search?keyword={isbn}',
            'enabled': True
        }
    }