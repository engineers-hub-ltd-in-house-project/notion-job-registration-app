# 求人情報登録アプリ - バックエンド

求人情報をOpenAIのAPIを使って解析し、Notionデータベースに登録するバックエンドAPIです。

## 機能
* 求人情報テキストをAIで解析してCSV形式に変換
* 変換したデータをNotionデータベースに登録
* CORSに対応したREST API

## 技術スタック
* Python 3.12
* Flask
* OpenAI API
* Notion API

## ローカル開発環境のセットアップ

### 前提条件
* Python 3.12以上
* pip
* Notionアカウントとデータベース
* OpenAIのAPIキー

### インストール手順

* リポジトリをクローン
```bash
git clone <repository-url>
cd notion-job-registration-app/backend
```

* 仮想環境を作成して有効化
```bash
python -m venv venv
source venv/bin/activate # Windowsの場合: venv\Scripts\activate
```

* 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

* 環境変数を設定
```bash
cp .env.example .env
```
.envファイルを編集して必要な情報を入力

* サーバーを起動
```bash
python app.py
```
サーバーはhttp://localhost:5555で起動します。

### 環境変数
.envファイルに以下の環境変数を設定してください：
```
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
OPENAI_API_KEY=your_openai_api_key
```

## API エンドポイント
* POST `/process_job`: 求人情報を処理してNotionに登録
* GET `/ping`: APIの動作確認用エンドポイント
* GET `/debug_database`: Notionデータベースの構造を確認
* GET `/test_notion`: テストデータでNotionへの登録をテスト

## Herokuへのデプロイ手順

### 1. 準備

#### 1.1 Heroku CLIのインストール

**macOS (Homebrew)**
```bash
brew install heroku/brew/heroku
```

**Windows**  
https://devcenter.heroku.com/articles/heroku-cli からインストーラーをダウンロード

**Ubuntu**
```bash
sudo snap install heroku --classic
```

#### 1.2 Heroku CLIでログイン
```bash
heroku login
```

### 2. プロジェクトの準備

#### 2.1 必要なファイルの作成

プロジェクトのルートディレクトリに**Procfile**（拡張子なし）を作成：
```
web: cd backend && gunicorn app:app
```

**runtime.txt**を作成：
```
python-3.12.7
```

**requirements.txt**に**gunicorn**が含まれていることを確認：
```
flask==3.1.0
flask-cors==5.0.1
python-dotenv==1.0.1
requests==2.32.3
openai==1.68.2
gunicorn==21.2.0
```

### 3. Herokuアプリの作成とデプロイ

#### 3.1 新しいHerokuアプリの作成
プロジェクトのルートディレクトリで実行
```bash
heroku create notion-job-registration-api
```

#### 3.2 Herokuへのデプロイ
```bash
git push heroku main
```

#### 3.3 環境変数の設定
```bash
heroku config:set NOTION_TOKEN=your_notion_token
heroku config:set NOTION_DATABASE_ID=your_database_id
heroku config:set OPENAI_API_KEY=your_openai_api_key
```

### 4. デプロイの確認

#### 4.1 アプリを開く
```bash
heroku open
```
または、ブラウザで`https://notion-job-registration-api.herokuapp.com/ping`にアクセスして、APIが正常に動作しているか確認します。

#### 4.2 ログの確認
```bash
heroku logs --tail
```

### 5. CORS設定の更新

フロントエンドのドメインに合わせてCORS設定を更新します：

**app.py**
```python
CORS(app, resources={r"/*": {"origins": ["https://your-frontend-domain.vercel.app", "http://localhost:5173"]}})
```

変更後、再デプロイします：
```bash
git add app.py
git commit -m "Update CORS settings"
git push heroku main
```

## トラブルシューティング

* **デプロイエラー**: `heroku logs --tail`でログを確認
* **アプリケーションエラー**: `heroku ps`でプロセスを確認
* **依存関係の問題**: `requirements.txt`を更新して再デプロイ
* **CORS問題**: フロントエンドのドメインがCORS設定に含まれているか確認

## ライセンス
MIT
