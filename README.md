# RestaurantSeeker-LLM

🍽️ 自然言語でレストランを検索し、価格・予約情報を比較できるアプリケーション

## 機能

- **自然言語検索**: 「新宿で美味しい寿司屋」「デートにおすすめのイタリアン」などの自然な表現で検索
- **複数API統合**: ホットペッパー、食べログなど複数のレストラン情報源から検索
- **価格比較**: 複数サイトの価格・予約情報を一括比較
- **リアルタイム検索**: LLM（Large Language Model）による高精度なクエリ解析

## アーキテクチャ

### フロントエンド
- HTML/CSS/JavaScript
- モダンなレスポンシブデザイン
- 非同期API通信

### バックエンド
- Python Flask
- LLM統合（Ollama）
- 複数API統合（ホットペッパー、食べログ）

## セットアップ

### 1. 依存関係のインストール

```bash
# バックエンド
cd backend
pip install flask flask-cors requests beautifulsoup4 python-dotenv

# フロントエンド
cd ../frontend
# 追加の依存関係は必要ありません（純粋なHTML/CSS/JS）
```

### 2. 環境変数の設定

```bash
# .envファイルを作成
cp backend/.env.example backend/.env

# APIキーを設定（詳細はAPI_SETUP_GUIDE.mdを参照）
# HOTPEPPER_API_KEY=your_hotpepper_api_key
# TABELOG_API_KEY=your_tabelog_api_key
```

### 3. サーバー起動

```bash
# バックエンドサーバー
cd backend
python app.py
# http://localhost:5003 で起動

# フロントエンドサーバー（別ターミナル）
cd frontend
python -m http.server 3000
# http://localhost:3000 でアクセス
```

## 使用方法

1. http://localhost:3000 にアクセス
2. 検索ボックスに自然な日本語でレストランの条件を入力
   - 例: 「渋谷で高級フレンチ」
   - 例: 「新宿でファミリー向けの焼肉店」
   - 例: 「銀座でデートにおすすめのイタリアン」
3. 検索結果から気になるレストランを選択
4. 「価格・予約情報を比較する」をクリックして複数サイトの情報を確認

## API統合状況

### ✅ 実装済み
- **ホットペッパーAPI**: リクルートWebサービス（無料10,000リクエスト/月）
- **サンプルデータ**: APIキー未設定時のフォールバック

### 🔄 実装予定
- **食べログAPI**: 審査待ち（3-4営業日）

### ❌ 利用不可
- **ぐるなびAPI**: 個人向け提供終了
- **Yahoo!グルメAPI**: サービス終了

## 技術仕様

### LLM統合
- **モデル**: Ollama (gpt-oss-20b)
- **機能**: 自然言語クエリの構造化
- **フォールバック**: 辞書ベースの直接マッチング

### データ構造
- 地域、料理ジャンル、シチュエーション、予算、人数を自動抽出
- 複合クエリに対応（複数条件の組み合わせ）

### API仕様
```
POST /search
{
  "query": "自然言語での検索クエリ"
}

POST /price-comparison  
{
  "restaurant_id": "レストランID"
}
```

## 開発情報

### プロジェクト構造
```
RestaurantSeeker-LLM/
├── backend/
│   ├── app.py              # メインアプリケーション
│   ├── config.py           # 設定管理
│   ├── .env.example        # 環境変数テンプレート
│   └── requirements.txt    # Python依存関係
├── frontend/
│   ├── index.html          # メインページ
│   ├── script.js           # JavaScript
│   └── style.css           # スタイルシート
├── API_SETUP_GUIDE.md      # API設定ガイド
└── README.md               # このファイル
```

### ベースプロジェクト
BookSeeker-LLMをベースに、レストラン検索向けに最適化

## ライセンス

このプロジェクトは学習・開発目的で作成されています。商用利用の際は各API提供者の利用規約を確認してください。

## トラブルシューティング

一般的な問題と解決方法については [API_SETUP_GUIDE.md](./API_SETUP_GUIDE.md) を参照してください。