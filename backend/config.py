import os

class Config:
    # LLM設定
    LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', 'http://localhost:11434/api/generate')
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama3')
    
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