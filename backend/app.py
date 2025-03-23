import os
import json
import csv
from io import StringIO
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from openai import OpenAI

# 環境変数の読み込み
load_dotenv()

# Flaskアプリケーションの設定
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.DEBUG)

# 環境変数の設定
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Notion API の設定
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# OpenAI クライアントの初期化
client = OpenAI(api_key=OPENAI_API_KEY)

def transform_data_with_ai(data):
    prompt = f"""
    以下の求人情報を、指定されたCSVフォーマットに変換してください。
    
    フォーマット: 名前,タグ,仕事内容,勤務地,勤務時間,必須スキル,案件タイトル,案件内容,歓迎スキル,給与,開発環境,雇用形態,業種業界,ポジション,プロダクト,期間,稼働率,働き方,期待する人物像,その他
    
    変換ルール:
    1. 名前: 案件タイトルと同じ値を使用
    2. タグ: 業種・業界、技術キーワードをカンマ区切りで
    3. 仕事内容: 【業務】セクションの内容
    4. 勤務地: 【働き方】セクションから場所情報を抽出
    5. 勤務時間: 【稼働】や勤務時間に関する情報
    6. 必須スキル: 【必須経験】セクションの内容
    7. 案件タイトル: 【案件タイトル】セクションの内容
    8. 案件内容: 【プロダクト】や業務内容の詳細
    9. 歓迎スキル: 【歓迎経験】セクションの内容
    10. 給与: 【報酬】セクションの内容
    11. 開発環境: 技術スタックや開発環境情報
    12. 雇用形態: 契約形態（業務委託など）
    13. 業種業界: 【業種・業界】セクションの内容
    14. ポジション: 【ポジション】セクションの内容
    15. プロダクト: 【プロダクト】セクションの内容
    16. 期間: 【期間】セクションの内容
    17. 稼働率: 【稼働】セクションの内容
    18. 働き方: 【働き方】セクションの内容
    19. 期待する人物像: 【期待する人物像】セクションの内容
    20. その他: 【その他】セクションの内容
    
    各フィールドが空の場合でも、必ず空文字列として出力してください。
    必ず1行のCSV形式で出力し、ヘッダー行も含めてください。
    
    求人情報:
    {data}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts job information to CSV format."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()

def create_notion_page(row):
    # すべてのフィールドに対してNoneや空の値を空文字列に変換する関数
    def get_safe_value(value):
        return value if value is not None else ""
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "名前": {"title": [{"text": {"content": get_safe_value(row.get("名前", ""))}}]},
            "タグ": {"multi_select": [{"name": tag.strip()} for tag in get_safe_value(row.get("タグ", "")).split(",") if tag.strip()]},
            "仕事内容": {"rich_text": [{"text": {"content": get_safe_value(row.get("仕事内容", ""))}}]},
            "勤務地": {"rich_text": [{"text": {"content": get_safe_value(row.get("勤務地", ""))}}]},
            "勤務時間": {"rich_text": [{"text": {"content": get_safe_value(row.get("勤務時間", ""))}}]},
            "必須スキル": {"rich_text": [{"text": {"content": get_safe_value(row.get("必須スキル", ""))}}]},
            "案件タイトル": {"rich_text": [{"text": {"content": get_safe_value(row.get("案件タイトル", ""))}}]},
            "案件内容": {"rich_text": [{"text": {"content": get_safe_value(row.get("案件内容", ""))}}]},
            "歓迎スキル": {"rich_text": [{"text": {"content": get_safe_value(row.get("歓迎スキル", ""))}}]},
            "給与": {"rich_text": [{"text": {"content": get_safe_value(row.get("給与", ""))}}]},
            "開発環境": {"rich_text": [{"text": {"content": get_safe_value(row.get("開発環境", ""))}}]},
            "雇用形態": {"rich_text": [{"text": {"content": get_safe_value(row.get("雇用形態", ""))}}]},
            # 追加プロパティ
            "業種業界": {"rich_text": [{"text": {"content": get_safe_value(row.get("業種業界", ""))}}]},
            "ポジション": {"rich_text": [{"text": {"content": get_safe_value(row.get("ポジション", ""))}}]},
            "プロダクト": {"rich_text": [{"text": {"content": get_safe_value(row.get("プロダクト", ""))}}]},
            "期間": {"rich_text": [{"text": {"content": get_safe_value(row.get("期間", ""))}}]},
            "稼働率": {"rich_text": [{"text": {"content": get_safe_value(row.get("稼働率", ""))}}]},
            "働き方": {"rich_text": [{"text": {"content": get_safe_value(row.get("働き方", ""))}}]},
            "期待する人物像": {"rich_text": [{"text": {"content": get_safe_value(row.get("期待する人物像", ""))}}]},
            "その他": {"rich_text": [{"text": {"content": get_safe_value(row.get("その他", ""))}}]},
        }
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=NOTION_HEADERS, json=data)
    return response

@app.route('/process_job', methods=['POST', 'GET'])
def process_job():
    if request.method == 'GET':
        return jsonify({"message": "APIは正常に動作しています。POSTリクエストを送信してください。"}), 200
        
    try:
        logging.debug("Received request: %s", request.json)
        content = request.json['content']
        
        logging.debug("Transforming data with AI")
        transformed_data = transform_data_with_ai(content)
        logging.debug("Transformed data: %s", transformed_data)

        # CSVヘッダーが含まれているか確認
        if "名前,タグ,仕事内容" not in transformed_data:
            # ヘッダーを追加
            transformed_data = "名前,タグ,仕事内容,勤務地,勤務時間,必須スキル,案件タイトル,案件内容,歓迎スキル,給与,開発環境,雇用形態\n" + transformed_data

        csv_file = StringIO(transformed_data)
        reader = csv.DictReader(csv_file)
        
        try:
            row = next(reader)
        except StopIteration:
            return jsonify({"message": "AIが適切なCSV形式を生成できませんでした"}), 400
            
        logging.debug("Parsed row: %s", row)
        
        # 各フィールドの値を個別にログ出力
        for key, value in row.items():
            logging.debug("Field %s: %s (type: %s)", key, value, type(value))

        logging.debug("Creating Notion page")
        response = create_notion_page(row)
        logging.debug("Notion API response: %s", response.text)
        
        if response.status_code != 200:
            logging.error("Failed to create Notion page: %s", response.text)
            return jsonify({"message": "Notionページの作成中にエラーが発生しました"}), 500

        return jsonify({"message": "処理が完了しました"}), 200
    except Exception as e:
        logging.exception("An error occurred")
        return jsonify({"message": f"エラーが発生しました: {str(e)}"}), 500

@app.route('/debug_database', methods=['GET'])
def debug_database():
    try:
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
        response = requests.get(url, headers=NOTION_HEADERS)
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test_notion', methods=['GET'])
def test_notion():
    try:
        # テスト用の固定データ
        test_data = {
            "名前": "ECサイトリニューアル基本設計担当",
            "タグ": "自動車,システム設計,C#",
            "仕事内容": "ECサイトリニューアルの基本設計・詳細設計業務",
            "勤務地": "リモート（月1～2回千代田区）",
            "勤務時間": "週3～4日",
            "必須スキル": "Webアプリケーション設計経験5年以上",
            "案件タイトル": "急募 ECサイトリニューアル基本設計担当",
            "案件内容": "ECサイトシステム刷新プロジェクト",
            "歓迎スキル": "ECサイト開発・設計の実務経験",
            "給与": "65万円/月",
            "開発環境": "C#, ASP.NET, MySQL",
            "雇用形態": "業務委託"
        }
        
        response = create_notion_page(test_data)
        return jsonify({"status": response.status_code, "response": response.json()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong", "status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # PORTが設定されていない場合はデフォルト5000を使用
    app.run(host="0.0.0.0", port=port, debug=True)
