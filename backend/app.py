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
CORS(app)
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
    フォーマット: 名前,タグ,仕事内容,勤務地,勤務時間,必須スキル,案件タイトル,案件内容,歓迎スキル,給与,開発環境,雇用形態

    求人情報:
    {data}

    変換後のCSV形式で出力してください。
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts job information to CSV format."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def create_notion_page(row):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "名前": {"title": [{"text": {"content": row.get("名前", "")}}]},
            "タグ": {"multi_select": [{"name": tag.strip()} for tag in row.get("タグ", "").split(",") if tag.strip()]},
            "仕事内容": {"rich_text": [{"text": {"content": row.get("仕事内容", "")}}]},
            "勤務地": {"rich_text": [{"text": {"content": row.get("勤務地", "")}}]},
            "勤務時間": {"rich_text": [{"text": {"content": row.get("勤務時間", "")}}]},
            "必須スキル": {"rich_text": [{"text": {"content": row.get("必須スキル", "")}}]},
            "案件タイトル": {"rich_text": [{"text": {"content": row.get("案件タイトル", "")}}]},
            "案件内容": {"rich_text": [{"text": {"content": row.get("案件内容", "")}}]},
            "歓迎スキル": {"rich_text": [{"text": {"content": row.get("歓迎スキル", "")}}]},
            "給与": {"rich_text": [{"text": {"content": row.get("給与", "")}}]},
            "開発環境": {"rich_text": [{"text": {"content": row.get("開発環境", "")}}]},
            "雇用形態": {"rich_text": [{"text": {"content": row.get("雇用形態", "")}}]},
        }
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=NOTION_HEADERS, json=data)
    return response

@app.route('/process_job', methods=['POST'])
def process_job():
    try:
        logging.debug("Received request: %s", request.json)
        content = request.json['content']
        
        logging.debug("Transforming data with AI")
        transformed_data = transform_data_with_ai(content)
        logging.debug("Transformed data: %s", transformed_data)

        csv_file = StringIO(transformed_data)
        reader = csv.DictReader(csv_file)
        row = next(reader)
        logging.debug("Parsed row: %s", row)

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

if __name__ == '__main__':
    app.run(debug=True)
