# 求人情報処理アプリケーション

このアプリケーションは、求人情報を受け取り、AI（OpenAI API）を使用してデータを処理し、指定されたフォーマットに変換した後、Notion データベースに保存するシステムです。フロントエンドは React（Vite）で、バックエンドは Python（Flask）で構築されています。

## 機能

- Web インターフェースで求人情報を入力
- OpenAI API を使用して求人情報を指定された CSV フォーマットに変換
- 変換されたデータを Notion データベースに保存
- API リクエストのレート制限機能

## 必要条件

- Python 3.8 以上
- Node.js 14 以上
- npm 6 以上
- OpenAI API キー
- Notion API キーとデータベース ID

## プロジェクト構造

```
job-registration-app/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## セットアップ

### バックエンド

1. バックエンドディレクトリに移動:

   ```
   cd backend
   ```

2. 仮想環境を作成し、アクティベート:

   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 依存関係をインストール:

   ```
   pip install -r requirements.txt
   ```

4. `.env` ファイルを作成し、環境変数を設定:
   ```
   OPENAI_API_KEY=your_openai_api_key
   NOTION_TOKEN=your_notion_api_key
   NOTION_DATABASE_ID=your_notion_database_id
   ```

### フロントエンド

1. フロントエンドディレクトリに移動:

   ```
   cd frontend
   ```

2. 依存関係をインストール:
   ```
   npm install
   ```

## 起動方法

### バックエンド

バックエンドディレクトリで:

```
python app.py
```

サーバーが http://localhost:5000 で起動します。

### フロントエンド

フロントエンドディレクトリで:

```
npm run dev
```

開発サーバーが（通常）http://localhost:5173 で起動します。

## 使用方法

1. ブラウザで http://localhost:5173 を開きます。
2. 表示されたフォームに求人情報を入力します。
3. 「送信」ボタンをクリックして、求人情報を処理します。
4. 処理結果がページに表示されます。成功した場合、データが Notion データベースに保存されます。

## API エンドポイント

- POST `/process_job`: 求人情報を処理
  - リクエストボディ: `{ "content": "求人情報のテキスト" }`
  - レスポンス: 処理結果と変換されたデータ

## トラブルシューティング

- OpenAI API のレート制限エラー: `backend/app.py` の `RATE_LIMIT` 変数を調整。
- Notion データベース書き込みエラー: データベースの権限設定を確認。
- CORS エラー: バックエンドの CORS 設定を確認。
- 接続エラー: フロントエンドの API エンドポイント URL が正しいか確認。

## 開発

- バックエンドの変更: `backend/app.py` を編集。
- フロントエンドの変更: `frontend/src/` 内のファイルを編集。
- 新しい依存関係の追加:
  - バックエンド: `pip install <package>` 後、`pip freeze > requirements.txt`
  - フロントエンド: `npm install <package>`

## 注意事項

- 開発環境用のセットアップです。本番環境ではセキュリティ対策を実装してください。
- OpenAI API の利用には料金が発生する可能性があります。利用状況を定期的に確認してください。
- Notion API の利用には適切な権限設定が必要です。

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) の下で公開されています。

## 貢献

バグ報告や機能リクエストは GitHub の Issue で受け付けています。プルリクエストも歓迎です。
# notion-job-registration-app
