from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from typing import Dict, List, Optional, Any
import logging
import sys
from config import Config

app = Flask(__name__)
CORS(app)

# 標準出力を強制的にフラッシュ
import sys
import os
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)  # Line buffered

class RestaurantSearchService:
    def __init__(self):
        self.llm_endpoint = Config.LLM_ENDPOINT
        # 飲食店検索用API設定
        self.hotpepper_api = Config.HOTPEPPER_API_URL
        self.tabelog_api = Config.TABELOG_API_URL
        
        # API キー
        self.hotpepper_api_key = Config.HOTPEPPER_API_KEY
        self.tabelog_api_key = Config.TABELOG_API_KEY
        
        print(f"[INIT] HotPepper API Key: {'SET' if self.hotpepper_api_key else 'NOT SET'}")
        print(f"[INIT] Tabelog API Key: {'SET' if self.tabelog_api_key else 'NOT SET'}")
        
    def query_llm(self, user_query: str) -> Dict[str, Any]:
        # まず直接辞書マッチングを試行
        direct_result = self._extract_restaurant_keywords_directly(user_query)
        
        # 直接マッチングが成功した場合はそれを使用
        if any([direct_result.get('location'), direct_result.get('cuisine'), direct_result.get('category')]):
            print(f"*** DIRECT MATCH FOUND: {direct_result} ***")
            return direct_result
        
        # 直接マッチングが失敗した場合のみLLMを使用
        print(f"[INFO] No direct match found, querying LLM for: {user_query}", flush=True)
        llm_result = self._query_llm_for_restaurant(user_query)
        return llm_result
    
    def _extract_restaurant_keywords_directly(self, query: str) -> Dict[str, Any]:
        """直接的なキーワード抽出（飲食店版）"""
        query_lower = query.lower().replace('「', '').replace('」', '')
        
        # 地域辞書（主要エリア）
        location_dict = {
            '新宿': '新宿',
            'shinjuku': '新宿',
            '渋谷': '渋谷',
            'shibuya': '渋谷',
            '池袋': '池袋',
            'ikebukuro': '池袋',
            '銀座': '銀座',
            'ginza': '銀座',
            '六本木': '六本木',
            'roppongi': '六本木',
            '品川': '品川',
            'shinagawa': '品川',
            '新橋': '新橋',
            'shinbashi': '新橋',
            '恵比寿': '恵比寿',
            'ebisu': '恵比寿',
            '代官山': '代官山',
            'daikanyama': '代官山',
            '表参道': '表参道',
            'omotesando': '表参道',
            '赤坂': '赤坂',
            'akasaka': '赤坂',
            '青山': '青山',
            'aoyama': '青山',
            '有楽町': '有楽町',
            'yurakucho': '有楽町',
            '秋葉原': '秋葉原',
            'akihabara': '秋葉原',
            '上野': '上野',
            'ueno': '上野',
            '浅草': '浅草',
            'asakusa': '浅草',
            '東京駅': '東京駅',
            'tokyo station': '東京駅',
            '横浜': '横浜',
            'yokohama': '横浜',
            'みなとみらい': 'みなとみらい',
            'minato mirai': 'みなとみらい'
        }
        
        # 料理ジャンル辞書
        cuisine_dict = {
            '寿司': '寿司',
            'sushi': '寿司',
            '鮨': '寿司',
            'すし': '寿司',
            'イタリアン': 'イタリアン',
            'italian': 'イタリアン',
            'イタリア料理': 'イタリアン',
            'フレンチ': 'フレンチ',
            'french': 'フレンチ',
            'フランス料理': 'フレンチ',
            '中華': '中華',
            'chinese': '中華',
            '中国料理': '中華',
            '中華料理': '中華',
            '焼肉': '焼肉',
            'yakiniku': '焼肉',
            '焼き肉': '焼肉',
            'bbq': '焼肉',
            '居酒屋': '居酒屋',
            'izakaya': '居酒屋',
            '韓国料理': '韓国料理',
            'korean': '韓国料理',
            'タイ料理': 'タイ料理',
            'thai': 'タイ料理',
            'インド料理': 'インド料理',
            'indian': 'インド料理',
            'カレー': 'カレー',
            'curry': 'カレー',
            'ラーメン': 'ラーメン',
            'ramen': 'ラーメン',
            'うどん': 'うどん',
            'udon': 'うどん',
            'そば': 'そば',
            'soba': 'そば',
            '蕎麦': 'そば',
            '天ぷら': '天ぷら',
            'tempura': '天ぷら',
            'てんぷら': '天ぷら',
            'とんかつ': 'とんかつ',
            'tonkatsu': 'とんかつ',
            'カツ': 'とんかつ',
            'ハンバーガー': 'ハンバーガー',
            'burger': 'ハンバーガー',
            'ステーキ': 'ステーキ',
            'steak': 'ステーキ',
            '和食': '和食',
            'japanese': '和食',
            '洋食': '洋食',
            'western': '洋食'
        }
        
        # シチュエーション/カテゴリ辞書
        category_dict = {
            'デート': 'デート',
            'date': 'デート',
            '記念日': '記念日',
            'anniversary': '記念日',
            '接待': '接待',
            'business': '接待',
            '会食': '接待',
            '飲み会': '飲み会',
            'party': '飲み会',
            'パーティ': '飲み会',
            '女子会': '女子会',
            'girls night': '女子会',
            '家族': '家族',
            'family': '家族',
            'ファミリー': '家族',
            '一人': '一人',
            'solo': '一人',
            'ひとり': '一人',
            'ランチ': 'ランチ',
            'lunch': 'ランチ',
            'お昼': 'ランチ',
            'ディナー': 'ディナー',
            'dinner': 'ディナー',
            '夕食': 'ディナー',
            'カジュアル': 'カジュアル',
            'casual': 'カジュアル',
            '高級': '高級',
            'luxury': '高級',
            'fine dining': '高級',
            'おしゃれ': 'おしゃれ',
            'stylish': 'おしゃれ',
            '安い': '安い',
            'cheap': '安い',
            'リーズナブル': '安い',
            'affordable': '安い',
            '個室': '個室',
            'private': '個室',
            'プライベート': '個室',
            '夜景': '夜景',
            'view': '夜景',
            '景色': '夜景'
        }
        
        # 地域マッチング
        detected_location = None
        for location_key, location_name in location_dict.items():
            if location_key in query_lower:
                detected_location = location_name
                print(f"*** LOCATION DETECTED: '{location_key}' -> '{location_name}' ***")
                break
        
        # 料理ジャンルマッチング  
        detected_cuisine = None
        for cuisine_key, cuisine_name in cuisine_dict.items():
            if cuisine_key in query_lower:
                detected_cuisine = cuisine_name
                print(f"*** CUISINE DETECTED: '{cuisine_key}' -> '{cuisine_name}' ***")
                break
        
        # カテゴリマッチング
        detected_category = None
        for category_key, category_name in category_dict.items():
            if category_key in query_lower:
                detected_category = category_name
                print(f"*** CATEGORY DETECTED: '{category_key}' -> '{category_name}' ***")
                break
        
        # 複合クエリの解析
        compound_result = self._parse_compound_restaurant_query(query_lower, detected_location, detected_cuisine, detected_category)
        if compound_result:
            print(f"*** COMPOUND RESTAURANT QUERY: {compound_result} ***", flush=True)
            return compound_result
        
        # 基本的な結果を返す
        result = {
            'location': detected_location,
            'cuisine': detected_cuisine, 
            'category': detected_category,
            'budget': None,
            'party_size': None
        }
        
        return result
    
    def _parse_compound_restaurant_query(self, query_lower: str, location: str, cuisine: str, category: str) -> Optional[Dict[str, Any]]:
        """複合レストランクエリの解析（例: '新宿でデートにおすすめのイタリアン'）"""
        
        # 予算情報の抽出
        budget = None
        if any(keyword in query_lower for keyword in ['安い', 'cheap', 'リーズナブル', '3000円以下', '2000円以下']):
            budget = 'low'
        elif any(keyword in query_lower for keyword in ['高級', 'luxury', 'fine dining', '10000円以上', '1万円以上']):
            budget = 'high'
        elif any(keyword in query_lower for keyword in ['普通', 'moderate', '5000円', '4000円', '中価格']):
            budget = 'medium'
        
        # 人数情報の抽出
        party_size = None
        if any(keyword in query_lower for keyword in ['二人', '2人', '2名', 'couple', 'two']):
            party_size = 2
        elif any(keyword in query_lower for keyword in ['四人', '4人', '4名', 'four', 'group']):
            party_size = 4
        elif any(keyword in query_lower for keyword in ['大人数', '10人', '宴会', 'large group']):
            party_size = 10
        elif any(keyword in query_lower for keyword in ['一人', '1人', 'solo', 'alone']):
            party_size = 1
        
        # 時間帯情報の抽出
        time_preference = None
        if any(keyword in query_lower for keyword in ['ランチ', 'lunch', 'お昼', '昼食']):
            time_preference = 'lunch'
        elif any(keyword in query_lower for keyword in ['ディナー', 'dinner', '夕食', '夜']):
            time_preference = 'dinner'
        elif any(keyword in query_lower for keyword in ['朝食', 'breakfast', '朝', 'morning']):
            time_preference = 'breakfast'
        
        # 複数の要素が検出された場合は複合クエリとして処理
        detected_elements = [location, cuisine, category, budget, party_size, time_preference]
        non_null_elements = [elem for elem in detected_elements if elem is not None]
        
        if len(non_null_elements) >= 2:
            return {
                'location': location,
                'cuisine': cuisine,
                'category': category, 
                'budget': budget,
                'party_size': party_size,
                'time_preference': time_preference,
                'query_type': 'compound',
                'original_query': query_lower
            }
        
        return None
    
    def _query_llm_for_restaurant(self, user_query: str) -> Dict[str, Any]:
        """LLMを使用してレストラン検索クエリを解析"""
        try:
            prompt = f"""あなたはレストラン検索の専門アシスタントです。ユーザーの自然言語クエリからレストラン検索に必要な情報を抽出してください。

ユーザークエリ: "{user_query}"

以下のJSON形式で回答してください：
{{
    "location": "地域名（例：新宿、渋谷）",
    "cuisine": "料理ジャンル（例：イタリアン、寿司）",
    "category": "シチュエーション（例：デート、接待）",
    "budget": "予算レベル（low/medium/high）",
    "party_size": "人数（数値）",
    "time_preference": "時間帯（lunch/dinner/breakfast）"
}}

重要な注意点：
- 確実でない情報は推測せずnullを返してください
- 地域名は実在する場所のみ答えてください
- 料理ジャンルは一般的なカテゴリで答えてください
- 日本のレストランを優先してください"""

            payload = {
                "model": Config.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 200
                }
            }
            
            response = requests.post(self.llm_endpoint, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '').strip()
                
                app.logger.info(f"LLM response: {content}")
                
                # JSONを抽出
                try:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        parsed = json.loads(json_str)
                        
                        # 結果を検証・正規化
                        result = {
                            'location': parsed.get('location') if parsed.get('location') and parsed.get('location') != 'null' else None,
                            'cuisine': parsed.get('cuisine') if parsed.get('cuisine') and parsed.get('cuisine') != 'null' else None,
                            'category': parsed.get('category') if parsed.get('category') and parsed.get('category') != 'null' else None,
                            'budget': parsed.get('budget') if parsed.get('budget') and parsed.get('budget') != 'null' else None,
                            'party_size': parsed.get('party_size') if parsed.get('party_size') and parsed.get('party_size') != 'null' else None,
                            'time_preference': parsed.get('time_preference') if parsed.get('time_preference') and parsed.get('time_preference') != 'null' else None
                        }
                        
                        app.logger.info(f"Parsed LLM result: {result}")
                        return result
                        
                except json.JSONDecodeError as e:
                    app.logger.error(f"Failed to parse LLM JSON response: {e}")
                
                # JSONパースに失敗した場合のフォールバック
                return {
                    'location': None,
                    'cuisine': None,
                    'category': None,
                    'budget': None,
                    'party_size': None,
                    'time_preference': None
                }
                
            else:
                app.logger.error(f"LLM API error: HTTP {response.status_code}")
                return {'location': None, 'cuisine': None, 'category': None, 'budget': None, 'party_size': None, 'time_preference': None}
                
        except Exception as e:
            app.logger.error(f"LLM query error: {e}")
            return {'location': None, 'cuisine': None, 'category': None, 'budget': None, 'party_size': None, 'time_preference': None}
    
    def search_restaurants(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """レストラン検索（複数ソース対応）"""
        candidates = []
        seen_ids = set()
        
        print(f"[SEARCH] Searching restaurants with params: {search_params}", flush=True)
        
        # ホットペッパーAPIの結果を優先
        if self.hotpepper_api_key:
            hotpepper_results = self._search_hotpepper(search_params, seen_ids)
            candidates.extend(hotpepper_results)
            print(f"[HOTPEPPER] Added {len(hotpepper_results)} results")
        
        # 食べログAPIの結果
        if self.tabelog_api_key:
            tabelog_results = self._search_tabelog(search_params, seen_ids)
            candidates.extend(tabelog_results)
            print(f"[TABELOG] Added {len(tabelog_results)} results")
        
        # HotPepper APIの結果が少ない場合、サンプルデータで補完
        if len(candidates) < 5:
            print(f"[FALLBACK] Only {len(candidates)} API results, adding sample data for better variety")
            sample_results = self._get_sample_restaurants(search_params, seen_ids)
            # サンプル結果をAPIの結果の後に追加
            candidates.extend(sample_results[:10])  # 最大10件のサンプルデータを追加
        
        print(f"*** TOTAL RESULTS: {len(candidates)} RESTAURANTS FOUND ***")
        return candidates[:20]  # 最大20件に制限
    
    def _get_sample_restaurants(self, search_params: Dict[str, Any], seen_ids: set) -> List[Dict[str, Any]]:
        """サンプルレストランデータの生成"""
        location = search_params.get('location', '東京')
        cuisine = search_params.get('cuisine', '和食')
        category = search_params.get('category', '')
        
        # サンプルレストランデータベース
        sample_restaurants = [
            # 寿司
            {
                "name": "鮨 さくら",
                "cuisine": "寿司",
                "location": "銀座",
                "rating": 4.5,
                "price_range": "¥¥¥¥",
                "address": "東京都中央区銀座5-1-1",
                "phone": "03-1234-5678",
                "image": "https://example.com/sushi1.jpg",
                "description": "銀座の老舗寿司店。新鮮なネタと熟練の技で極上の寿司をお楽しみいただけます。",
                "features": ["個室あり", "カウンター席", "予約必須"],
                "budget": "high"
            },
            {
                "name": "回転寿司 海鮮丸",
                "cuisine": "寿司", 
                "location": "新宿",
                "rating": 4.0,
                "price_range": "¥¥",
                "address": "東京都新宿区新宿3-1-1",
                "phone": "03-2345-6789",
                "image": "https://example.com/sushi2.jpg", 
                "description": "気軽に楽しめる回転寿司店。新鮮で美味しいお寿司をリーズナブルに。",
                "features": ["回転寿司", "家族向け", "テイクアウト可"],
                "budget": "low"
            },
            
            # イタリアン
            {
                "name": "リストランテ ベッラヴィスタ",
                "cuisine": "イタリアン",
                "location": "恵比寿",
                "rating": 4.7,
                "price_range": "¥¥¥¥",
                "address": "東京都渋谷区恵比寿1-1-1",
                "phone": "03-3456-7890",
                "image": "https://example.com/italian1.jpg",
                "description": "恵比寿の隠れ家的イタリアン。本格的な料理と素晴らしい夜景でロマンチックなひとときを。",
                "features": ["夜景", "デート向け", "ワイン豊富"],
                "budget": "high"
            },
            {
                "name": "パスタ・アモーレ",
                "cuisine": "イタリアン",
                "location": "新宿",
                "rating": 4.2,
                "price_range": "¥¥",
                "address": "東京都新宿区新宿2-1-1", 
                "phone": "03-4567-8901",
                "image": "https://example.com/italian2.jpg",
                "description": "カジュアルなイタリアンレストラン。本格パスタをお手頃価格で。",
                "features": ["カジュアル", "ランチ営業", "パスタ専門"],
                "budget": "medium"
            },
            
            # フレンチ
            {
                "name": "ル・ジャルダン",
                "cuisine": "フレンチ",
                "location": "表参道",
                "rating": 4.8,
                "price_range": "¥¥¥¥¥",
                "address": "東京都港区北青山3-1-1",
                "phone": "03-5678-9012",
                "image": "https://example.com/french1.jpg",
                "description": "表参道の高級フレンチレストラン。シェフこだわりの創作フレンチをお楽しみください。",
                "features": ["高級", "記念日向け", "フルコース"],
                "budget": "high"
            },
            
            # 中華
            {
                "name": "中華酒楼 金龍",
                "cuisine": "中華",
                "location": "池袋",
                "rating": 4.3,
                "price_range": "¥¥¥",
                "address": "東京都豊島区池袋1-1-1",
                "phone": "03-6789-0123",
                "image": "https://example.com/chinese1.jpg",
                "description": "本格中華料理店。点心から北京ダックまで幅広いメニューをご用意。",
                "features": ["本格中華", "円卓あり", "宴会可"],
                "budget": "medium"
            },
            
            # 焼肉
            {
                "name": "焼肉 牛王",
                "cuisine": "焼肉",
                "location": "渋谷",
                "rating": 4.4,
                "price_range": "¥¥¥",
                "address": "東京都渋谷区渋谷1-1-1",
                "phone": "03-7890-1234",
                "image": "https://example.com/yakiniku1.jpg",
                "description": "A5ランクの和牛を使用した高級焼肉店。個室完備でプライベートな食事を。",
                "features": ["A5和牛", "個室あり", "飲み放題"],
                "budget": "high"
            },
            
            # 居酒屋
            {
                "name": "居酒屋 とりあえず",
                "cuisine": "居酒屋",
                "location": "新宿",
                "rating": 4.1,
                "price_range": "¥¥",
                "address": "東京都新宿区新宿4-1-1",
                "phone": "03-8901-2345",
                "image": "https://example.com/izakaya1.jpg",
                "description": "気軽に楽しめる居酒屋。新鮮な刺身と種類豊富な日本酒をご用意。",
                "features": ["飲み会向け", "日本酒豊富", "喫煙可"],
                "budget": "low"
            },
            
            # カフェ・軽食
            {
                "name": "カフェ・ド・パリ",
                "cuisine": "カフェ",
                "location": "表参道",
                "rating": 4.0,
                "price_range": "¥¥",
                "address": "東京都港区北青山2-1-1",
                "phone": "03-9012-3456",
                "image": "https://example.com/cafe1.jpg",
                "description": "パリの雰囲気漂うおしゃれなカフェ。こだわりのコーヒーとスイーツを。",
                "features": ["Wi-Fi完備", "一人利用歓迎", "テラス席"],
                "budget": "low"
            }
        ]
        
        # 検索パラメータに基づいてフィルタリング
        filtered_restaurants = []
        
        for restaurant in sample_restaurants:
            score = 0
            
            # 地域マッチング
            if location and location in restaurant.get('location', ''):
                score += 10
            
            # 料理ジャンルマッチング
            if cuisine and cuisine in restaurant.get('cuisine', ''):
                score += 10
            
            # カテゴリ・シチュエーションマッチング
            if category:
                if category == 'デート' and any(feature in restaurant.get('features', []) for feature in ['デート向け', '夜景', '個室あり']):
                    score += 8
                elif category == '接待' and any(feature in restaurant.get('features', []) for feature in ['高級', '個室あり', 'フルコース']):
                    score += 8
                elif category == '飲み会' and any(feature in restaurant.get('features', []) for feature in ['飲み会向け', '飲み放題', '宴会可']):
                    score += 8
                elif category == '家族' and any(feature in restaurant.get('features', []) for feature in ['家族向け', '円卓あり', 'テイクアウト可']):
                    score += 8
                elif category == '一人' and any(feature in restaurant.get('features', []) for feature in ['一人利用歓迎', 'カウンター席', 'Wi-Fi完備']):
                    score += 8
            
            # 予算マッチング
            budget = search_params.get('budget')
            if budget and budget == restaurant.get('budget'):
                score += 5
            
            # スコアが一定以上の場合に結果に含める
            if score >= 5 or not (location or cuisine or category):
                restaurant_copy = restaurant.copy()
                restaurant_copy['match_score'] = score
                restaurant_copy['id'] = f"restaurant_{len(filtered_restaurants) + 1}"
                filtered_restaurants.append(restaurant_copy)
                seen_ids.add(restaurant_copy['id'])
        
        # スコア順にソート
        filtered_restaurants.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        print(f"[SAMPLE] Found {len(filtered_restaurants)} matching restaurants")
        return filtered_restaurants[:15]  # 最大15件
    
    def _search_hotpepper(self, search_params: Dict[str, Any], seen_ids: set) -> List[Dict[str, Any]]:
        """ホットペッパーAPI検索"""
        if not self.hotpepper_api_key:
            print("[HOTPEPPER] API key not configured")
            return []
        
        try:
            # API リクエストパラメータの構築
            params = {
                'key': self.hotpepper_api_key,
                'format': 'json',
                'count': 50,  # より多くの結果を取得
            }
            
            # 地域の設定（より広範囲で検索）
            location = search_params.get('location')
            if location and location in Config.HOTPEPPER_AREA_CODES:
                params['middle_area'] = Config.HOTPEPPER_AREA_CODES[location]
                print(f"[HOTPEPPER] Area: {location} -> {params['middle_area']}")
            elif location:
                # エリアコードにない場合はキーワード検索
                params['keyword'] = location
                print(f"[HOTPEPPER] Using keyword search for location: {location}")
            
            # 料理ジャンルの設定
            cuisine = search_params.get('cuisine')
            if cuisine and cuisine in Config.HOTPEPPER_GENRE_CODES:
                params['genre'] = Config.HOTPEPPER_GENRE_CODES[cuisine]
                print(f"[HOTPEPPER] Genre: {cuisine} -> {params['genre']}")
            elif cuisine:
                # ジャンルコードにない場合はキーワードに追加
                existing_keyword = params.get('keyword', '')
                params['keyword'] = f"{existing_keyword} {cuisine}".strip()
                print(f"[HOTPEPPER] Using keyword search for cuisine: {cuisine}")
            
            # 予算の設定
            budget = search_params.get('budget')
            if budget:
                if budget == 'low':
                    params['budget'] = 'B005'  # ~2000円
                elif budget == 'medium':
                    params['budget'] = 'B003'  # 3000~4000円
                elif budget == 'high':
                    params['budget'] = 'B001'  # 4000円~
            
            print(f"[HOTPEPPER] Request params: {params}")
            
            response = requests.get(self.hotpepper_api, params=params, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            shops = data.get('results', {}).get('shop', [])
            
            restaurants = []
            for shop in shops:
                restaurant_id = f"hotpepper_{shop.get('id')}"
                
                if restaurant_id not in seen_ids:
                    # マッチスコア計算
                    match_score = 10  # 基本スコア（API結果なので高い）
                    
                    # 料理ジャンルのマッチング
                    shop_genre = shop.get('genre', {}).get('name', '')
                    cuisine = search_params.get('cuisine', '')
                    if cuisine and cuisine in shop_genre:
                        match_score += 10
                    
                    # 地域のマッチング
                    shop_area = shop.get('middle_area', {}).get('name', '')
                    location = search_params.get('location', '')
                    if location and location in shop_area:
                        match_score += 5
                    
                    restaurant = {
                        'id': restaurant_id,
                        'name': shop.get('name', ''),
                        'cuisine': shop_genre,
                        'location': shop_area,
                        'address': shop.get('address', ''),
                        'phone': shop.get('tel', ''),
                        'rating': None,  # ホットペッパーは評価なし
                        'price_range': shop.get('budget', {}).get('name', ''),
                        'description': shop.get('catch', ''),
                        'image': shop.get('photo', {}).get('pc', {}).get('l', ''),
                        'features': [],
                        'match_score': match_score,
                        'source': 'hotpepper'
                    }
                    
                    # 特徴の追加
                    if shop.get('private_room', '') == 'あり':
                        restaurant['features'].append('個室あり')
                    if shop.get('parking', '') == 'あり':
                        restaurant['features'].append('駐車場')
                    if shop.get('card', '') == '利用可':
                        restaurant['features'].append('クレジット可')
                    if shop.get('non_smoking', '') == '全面禁煙':
                        restaurant['features'].append('禁煙')
                    
                    restaurants.append(restaurant)
                    seen_ids.add(restaurant_id)
            
            # マッチスコア順にソート
            restaurants.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            print(f"[HOTPEPPER] Found {len(restaurants)} restaurants")
            return restaurants
            
        except requests.RequestException as e:
            print(f"[HOTPEPPER] API request error: {e}")
            return []
        except Exception as e:
            print(f"[HOTPEPPER] Error: {e}")
            return []
    
    def _search_tabelog(self, search_params: Dict[str, Any], seen_ids: set) -> List[Dict[str, Any]]:
        """食べログAPI検索（サンプル実装）"""
        if not self.tabelog_api_key:
            print("[TABELOG] API key not configured")
            return []
        
        # 食べログAPIの実装は要確認
        # 実際のAPIエンドポイントとパラメータが不明なため、現在はサンプル実装
        print("[TABELOG] API integration pending - sample data returned")
        return []
    
    def get_restaurant_prices(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """レストランの価格・予約情報を複数サイトから取得"""
        results = []
        
        print(f"[PRICE] Getting restaurant prices for ID: {restaurant_id}", flush=True)
        
        # 価格・予約サイト一覧
        price_sources = [
            ("ぐるなび", self._get_gurunavi_price),
            ("ホットペッパー", self._get_hotpepper_price), 
            ("食べログ", self._get_tabelog_price),
            ("オープンテーブル", self._get_opentable_price),
            ("一休.com", self._get_ikyu_price),
            ("Yahoo!グルメ", self._get_yahoo_gourmet_price)
        ]
        
        for site_name, price_function in price_sources:
            try:
                print(f"[PRICE] Checking {site_name}...", flush=True)
                result = price_function(restaurant_id)
                if result:
                    results.append(result)
                    print(f"[PRICE] {site_name}: {result.get('price_info', 'N/A')}", flush=True)
                else:
                    print(f"[PRICE] {site_name}: No data", flush=True)
            except Exception as e:
                print(f"[PRICE] {site_name} error: {e}", flush=True)
        
        print(f"[PRICE] Price comparison completed: {len(results)} sites found", flush=True)
        return results
    
    def _get_gurunavi_price(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """ぐるなび価格情報取得"""
        try:
            # サンプル価格データ
            price_ranges = ["¥2,000-3,000", "¥3,000-4,000", "¥4,000-6,000", "¥6,000-8,000", "¥8,000-10,000"]
            restaurant_int = hash(restaurant_id) % len(price_ranges)
            price_range = price_ranges[restaurant_int]
            
            # 予約可能性
            reservation_available = (hash(restaurant_id) % 10) > 2  # 80%の確率で予約可能
            
            return {
                "site": "ぐるなび",
                "price_info": price_range,
                "reservation_available": reservation_available,
                "url": f"https://r.gnavi.co.jp/restaurant/{restaurant_id}/",
                "features": ["クーポンあり", "ネット予約", "コース料理"] if reservation_available else ["情報のみ"]
            }
        except Exception as e:
            print(f"[ERROR] Gurunavi price error: {e}", flush=True)
            return None
    
    def _get_hotpepper_price(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """ホットペッパー価格情報取得"""
        try:
            # ホットペッパーのレストランIDから実際の店舗情報を取得
            if restaurant_id.startswith('hotpepper_'):
                shop_id = restaurant_id.replace('hotpepper_', '')
                
                if self.hotpepper_api_key:
                    # 実際のAPIリクエスト
                    params = {
                        'key': self.hotpepper_api_key,
                        'id': shop_id,
                        'format': 'json'
                    }
                    
                    response = requests.get(self.hotpepper_api, params=params, timeout=Config.REQUEST_TIMEOUT)
                    response.raise_for_status()
                    
                    data = response.json()
                    shop = data.get('results', {}).get('shop', [])
                    
                    if shop:
                        shop_data = shop[0] if isinstance(shop, list) else shop
                        
                        return {
                            "site": "ホットペッパー",
                            "price_info": shop_data.get('budget', {}).get('name', '価格情報なし'),
                            "reservation_available": True,
                            "url": shop_data.get('urls', {}).get('pc', ''),
                            "features": ["即予約", "ポイント付与", "クーポン", "写真豊富"]
                        }
            
            # フォールバック（サンプルデータ）
            price_ranges = ["¥1,500-2,500", "¥2,500-3,500", "¥3,500-5,000", "¥5,000-7,000"]
            restaurant_int = hash(restaurant_id) % len(price_ranges)
            price_range = price_ranges[restaurant_int]
            
            reservation_available = (hash(restaurant_id) % 10) > 1  # 90%の確率で予約可能
            
            return {
                "site": "ホットペッパー",
                "price_info": price_range,
                "reservation_available": reservation_available,
                "url": f"https://www.hotpepper.jp/strJ{restaurant_id}/",
                "features": ["即予約", "ポイント付与", "クーポン"] if reservation_available else ["情報のみ"]
            }
        except Exception as e:
            print(f"[ERROR] HotPepper price error: {e}", flush=True)
            return None
    
    def _get_tabelog_price(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """食べログ価格情報取得"""
        try:
            price_ranges = ["¥2,000-3,000", "¥3,000-4,000", "¥4,000-6,000", "¥6,000-10,000"]
            restaurant_int = hash(restaurant_id) % len(price_ranges)
            price_range = price_ranges[restaurant_int]
            
            # 食べログは基本的に情報提供のみ
            rating = 3.0 + (hash(restaurant_id) % 20) / 10.0  # 3.0-5.0の評価
            
            return {
                "site": "食べログ",
                "price_info": price_range,
                "reservation_available": False,
                "rating": round(rating, 1),
                "url": f"https://tabelog.com/tokyo/{restaurant_id}/",
                "features": ["口コミ", "写真", "評価"]
            }
        except Exception as e:
            print(f"[ERROR] Tabelog price error: {e}", flush=True)
            return None
    
    def _get_opentable_price(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """オープンテーブル価格情報取得"""
        try:
            price_ranges = ["¥3,000-4,000", "¥4,000-6,000", "¥6,000-8,000", "¥8,000-12,000"]
            restaurant_int = hash(restaurant_id) % len(price_ranges)
            price_range = price_ranges[restaurant_int]
            
            reservation_available = (hash(restaurant_id) % 10) > 4  # 60%の確率で予約可能
            
            return {
                "site": "オープンテーブル",
                "price_info": price_range,
                "reservation_available": reservation_available,
                "url": f"https://www.opentable.jp/r/{restaurant_id}",
                "features": ["リアルタイム予約", "キャンセル可", "国際対応"] if reservation_available else ["情報のみ"]
            }
        except Exception as e:
            print(f"[ERROR] OpenTable price error: {e}", flush=True)
            return None
    
    def _get_ikyu_price(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """一休.com価格情報取得"""
        try:
            price_ranges = ["¥5,000-8,000", "¥8,000-12,000", "¥12,000-15,000", "¥15,000-20,000"]
            restaurant_int = hash(restaurant_id) % len(price_ranges)
            price_range = price_ranges[restaurant_int]
            
            reservation_available = (hash(restaurant_id) % 10) > 3  # 70%の確率で予約可能
            
            return {
                "site": "一休.com",
                "price_info": price_range,
                "reservation_available": reservation_available,
                "url": f"https://restaurant.ikyu.com/{restaurant_id}/",
                "features": ["高級店専門", "ポイント", "特典"] if reservation_available else ["情報のみ"]
            }
        except Exception as e:
            print(f"[ERROR] Ikyu price error: {e}", flush=True)
            return None
    
    def _get_yahoo_gourmet_price(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Yahoo!グルメ価格情報取得"""
        try:
            price_ranges = ["¥2,000-3,000", "¥3,000-4,000", "¥4,000-5,000", "¥5,000-7,000"]
            restaurant_int = hash(restaurant_id) % len(price_ranges)
            price_range = price_ranges[restaurant_int]
            
            reservation_available = (hash(restaurant_id) % 10) > 5  # 50%の確率で予約可能
            
            return {
                "site": "Yahoo!グルメ",
                "price_info": price_range,
                "reservation_available": reservation_available,
                "url": f"https://gourmet.yahoo.co.jp/restaurant/{restaurant_id}/",
                "features": ["Yahoo!ポイント", "クーポン", "口コミ"] if reservation_available else ["情報のみ"]
            }
        except Exception as e:
            print(f"[ERROR] Yahoo Gourmet price error: {e}", flush=True)
            return None

restaurant_service = RestaurantSearchService()

@app.route('/search', methods=['POST'])
def search_restaurants():
    data = request.get_json()
    query = data.get('query', '')
    
    print("\n" + "="*60)
    print("*** NEW RESTAURANT SEARCH REQUEST ***")
    print(f"*** QUERY: '{query}' ***")
    print("="*60)
    
    if not query:
        print("*** ERROR: Empty query received ***")
        return jsonify({"error": "Query is required"}), 400
    
    # Step 1: クエリ解析（地域、料理ジャンル、シチュエーション等を抽出）
    search_params = restaurant_service.query_llm(query)
    
    # Step 2: レストラン検索
    candidates = restaurant_service.search_restaurants(search_params)
    
    if candidates:
        return jsonify({
            "status": "restaurants_found",
            "restaurants": candidates,
            "search_params": search_params,
            "total_count": len(candidates)
        })
    else:
        return jsonify({
            "status": "no_results",
            "message": "該当するレストランが見つかりませんでした",
            "search_params": search_params
        })

@app.route('/price-comparison', methods=['POST'])
def price_comparison():
    data = request.get_json()
    restaurant_id = data.get('restaurant_id')
    
    app.logger.info(f"=== Restaurant Price Comparison Request ===")
    app.logger.info(f"Restaurant ID: {restaurant_id}")
    
    if not restaurant_id:
        app.logger.error("Empty restaurant_id received")
        return jsonify({"error": "Restaurant ID is required"}), 400
    
    # 価格・予約情報比較
    price_results = restaurant_service.get_restaurant_prices(restaurant_id)
    
    return jsonify({
        "restaurant_id": restaurant_id,
        "price_comparison": price_results
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/test-log', methods=['GET'])  
def test_log():
    print("\n" + "*"*50)
    print("*** LOG TEST - This should be visible in console ***")
    print("*** If you see this, logging is working! ***")
    print("*"*50)
    return jsonify({"message": "Log test completed - check console"})

@app.route('/debug-routes', methods=['GET'])
def debug_routes():
    """利用可能なルートを表示"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": str(rule)
        })
    print("*** Available routes: ***")
    for route in routes:
        print(f"  {route['path']} -> {route['methods']}")
    return jsonify({"routes": routes})

if __name__ == '__main__':
    print("=" * 50)
    print("Starting RestaurantSeeker-LLM Backend Server...")
    print("=" * 50)
    print("Server will be available at http://localhost:5003")
    print("Logging enabled - you should see detailed search logs below")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5003, use_reloader=False)