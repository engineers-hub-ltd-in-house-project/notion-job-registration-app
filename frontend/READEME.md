# 求人情報登録アプリ - フロントエンド

求人情報をOpenAIのAPIを使って解析し、Notionデータベースに登録するアプリケーションのフロントエンドです。

## 機能

* 求人情報テキストの入力フォーム
* バックエンドAPIとの連携
* レスポンシブデザイン

## 技術スタック

* Vite
* React
* JavaScript
* HTML/CSS

## ローカル開発環境のセットアップ

### 前提条件

* Node.js 22.14.0以上
* npm 10.9.2以上
* バックエンドAPIの稼働環境

### インストール手順

1. リポジトリをクローン
```bash
git clone https://github.com/engineers-hub-ltd-in-house-project/notion-job-registration-app.git
cd notion-job-registration-app/frontend
```

2. 依存パッケージをインストール
```bash
npm install
```

3. 環境変数を設定
```bash
cp .env.example .env
```
.envファイルを編集して必要な情報を入力

4. 開発サーバーを起動
```bash
npm run dev
```
開発サーバーはデフォルトで http://localhost:5173 で起動します。

### 環境変数

`.env`ファイルに以下の環境変数を設定してください：

```
VITE_API_URL=https://your-backend-api-url.com
```

ローカル開発時は、`vite.config.js`のプロキシ設定により、APIリクエストは自動的にローカルのバックエンドサーバーにリダイレクトされます。

## Vercelへのデプロイ手順

### 1. 準備

#### 1.1 Vercelアカウントの作成

[Vercel公式サイト](https://vercel.com/signup)でアカウントを作成します。GitHubアカウントでのサインアップが最も簡単です。

#### 1.2 環境変数の確認

フロントエンドで使用している環境変数を確認します。特にバックエンドAPIのURLを指定する変数（`VITE_API_URL`）が重要です。

### 2. デプロイ方法

#### 2.1 GitHubリポジトリからのデプロイ（推奨）

1. GitHubにプロジェクトをプッシュします
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. [Vercelダッシュボード](https://vercel.com/dashboard)にログインします

3. 「New Project」をクリックします

4. GitHubリポジトリを選択し、「Import」をクリックします

5. プロジェクト設定を行います：
   - **Project Name**: 任意のプロジェクト名
   - **Framework Preset**: 自動検出されるはずですが、手動で「Vite」を選択することもできます
   - **Root Directory**: フロントエンドコードがルートディレクトリにない場合は、`frontend`などのディレクトリを指定します
   - **Build Command**: デフォルトのままで問題ありません（`npm run build`）
   - **Output Directory**: デフォルトのままで問題ありません（`dist`）

6. 「Environment Variables」セクションで必要な環境変数を設定します：
   ```
   VITE_API_URL=https://notion-job-registration-api.herokuapp.com
   ```

7. 「Deploy」ボタンをクリックしてデプロイを開始します

#### 2.2 Vercel CLIを使用したデプロイ

1. Vercel CLIをインストールします
   ```bash
   npm install -g vercel
   ```

2. フロントエンドディレクトリに移動します
   ```bash
   cd frontend
   ```

3. Vercelにログインします
   ```bash
   vercel login
   ```

4. デプロイを実行します
   ```bash
   vercel
   ```

5. プロンプトに従って設定を行います：
   - プロジェクト設定を確認
   - 環境変数を設定（`VITE_API_URL`など）

6. デプロイが完了すると、デプロイURLが表示されます

### 3. 環境変数の設定

Vercelダッシュボードから環境変数を設定できます：

1. プロジェクトページに移動
2. 「Settings」タブをクリック
3. 「Environment Variables」セクションで変数を追加：
   - `VITE_API_URL`: バックエンドAPIのURL（例：`https://notion-job-registration-api.herokuapp.com`）

### 4. API接続の設定

#### 4.1 vercel.json の設定

プロダクション環境でAPIリクエストを正しくルーティングするために、`vercel.json`ファイルを更新します：

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://notion-job-registration-api.herokuapp.com/:path*"
    }
  ]
}
```

#### 4.2 CORS設定の確認

バックエンドのCORS設定が、フロントエンドのVercelドメインを許可していることを確認してください。

### 5. デプロイ後の設定

#### 5.1 カスタムドメインの設定（オプション）

1. Vercelダッシュボードでプロジェクトを選択
2. 「Settings」→「Domains」に移動
3. カスタムドメインを追加し、指示に従ってDNS設定を行う

#### 5.2 継続的デプロイの設定

GitHubリポジトリからデプロイした場合、デフォルトで継続的デプロイが有効になっています。mainブランチに変更をプッシュするたびに、自動的に新しいデプロイが作成されます。

## トラブルシューティング

### APIへの接続問題

フロントエンドがバックエンドAPIに接続できない場合：

1. 環境変数`VITE_API_URL`が正しく設定されているか確認
2. `vercel.json`のリライト設定が正しいか確認
3. バックエンドのCORS設定が正しいか確認
4. バックエンドが実際に稼働しているか確認

### ビルドエラー

ビルドエラーが発生した場合は、Vercelダッシュボードの「Deployments」タブでログを確認できます。

### ルーティング問題

SPAのルーティングが機能しない場合は、`vercel.json`ファイルに以下の設定を追加します：

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

## ライセンス

Private
