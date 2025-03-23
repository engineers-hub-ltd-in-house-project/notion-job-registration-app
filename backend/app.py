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
import re

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

# グローバル変数
data = ""  # 入力データを保存するグローバル変数

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

    各フィールドの詳細な説明と抽出ルール:
    1. 名前: 【業務名】セクションから抽出。例: "福祉事業会社向け 社内システム開発支援"
    2. タグ: 業種・業界、技術キーワードをカンマ区切りで。例: "Ruby,Rails,Web開発"
    3. 仕事内容: 【作業概要】セクションの内容。
    4. 勤務地: 【作業場所】セクションから場所情報を抽出。例: "基本リモート作業（地方の方可能）"
    5. 勤務時間: 【稼働】や勤務時間に関する情報。
    6. 必須スキル: 【スキル】の<マスト>セクションの内容。
    7. 案件タイトル: 【業務名】セクションの内容。
    8. 案件内容: 【作業概要】セクションの内容。
    9. 歓迎スキル: 【スキル】の<Better>セクションの内容。
    10. 給与: 【単金】セクションの内容。例: "85万（スキル見合い）（精算 140-180/月）"
    11. 開発環境: 【環境】セクションの「開発環境」に記載されている技術スタックのみ。例: "Ruby、Ruby on Rails、TypeScript、React.js"
    12. 雇用形態: 契約形態（業務委託など）。
    13. 業種業界: 業種・業界に関する情報。例: "福祉事業"
    14. ポジション: 【募集】セクションの内容。例: "バックエンドエンジニア × SE 8名"
    15. プロダクト: 開発対象のプロダクト情報。
    16. 期間: 【作業期間】セクションの内容。例: "2025年4月〜"
    17. 稼働率: 【単金】セクションの精算情報。例: "140-180/月"
    18. 働き方: 【作業場所】や働き方に関する情報。例: "基本リモート作業"
    19. 期待する人物像: 【備考】から期待する人物像を抽出。例: "主体的・自律的に行動できる方"
    20. その他: その他の重要情報。

    重要な注意点:
    - 各フィールドは必ず対応するセクションから情報を抽出し、混同しないでください。
    - 【環境】の開発環境と【単金】の情報を混同しないでください。
    - 【作業期間】と開発環境の情報を混同しないでください。
    - 給与情報は必ず【単金】セクションから抽出してください。
    - 期間情報は必ず【作業期間】セクションから抽出してください。
    - 開発環境は【環境】セクションの「開発環境」部分から技術スタックのみを抽出してください。
    - 情報がない場合は「情報なし」と出力してください。
    - 必ず1行のCSV形式で出力し、ヘッダー行は含めないでください。

    求人情報:
    {data}
    """
    
    logging.debug("Sending prompt to OpenAI: %s", prompt)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts job information to CSV format."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )
    
    result = response.choices[0].message.content.strip()
    logging.debug("OpenAI response: %s", result)
    return result

def create_notion_page(row):
    url = f"https://api.notion.com/v1/pages"
    
    # データの最終検証
    final_validate_data(row)
    
    # Notionプロパティの作成
    properties = {
        "名前": {"title": [{"text": {"content": row["名前"]}}]},
        "タグ": {"multi_select": [{"name": tag.strip()} for tag in row["タグ"].split(",") if tag.strip()]},
        "仕事内容": {"rich_text": [{"text": {"content": row["仕事内容"][:2000] if len(row["仕事内容"]) > 2000 else row["仕事内容"]}}]},
        "勤務地": {"rich_text": [{"text": {"content": row["勤務地"]}}]},
        "勤務時間": {"rich_text": [{"text": {"content": row["勤務時間"]}}]},
        "必須スキル": {"rich_text": [{"text": {"content": row["必須スキル"][:2000] if len(row["必須スキル"]) > 2000 else row["必須スキル"]}}]},
        "案件タイトル": {"rich_text": [{"text": {"content": row["案件タイトル"]}}]},
        "案件内容": {"rich_text": [{"text": {"content": row["案件内容"][:2000] if len(row["案件内容"]) > 2000 else row["案件内容"]}}]},
        "歓迎スキル": {"rich_text": [{"text": {"content": row["歓迎スキル"][:2000] if len(row["歓迎スキル"]) > 2000 else row["歓迎スキル"]}}]},
        "給与": {"rich_text": [{"text": {"content": row["給与"]}}]},
        "開発環境": {"rich_text": [{"text": {"content": row["開発環境"]}}]},
        "雇用形態": {"rich_text": [{"text": {"content": row["雇用形態"]}}]},
        "業種業界": {"rich_text": [{"text": {"content": row["業種業界"]}}]},
        "ポジション": {"rich_text": [{"text": {"content": row["ポジション"]}}]},
        "プロダクト": {"rich_text": [{"text": {"content": row["プロダクト"]}}]},
        "期間": {"rich_text": [{"text": {"content": row["期間"]}}]},
        "稼働率": {"rich_text": [{"text": {"content": row["稼働率"]}}]},
        "働き方": {"rich_text": [{"text": {"content": row["働き方"]}}]},
        "期待する人物像": {"rich_text": [{"text": {"content": row["期待する人物像"]}}]},
        "その他": {"rich_text": [{"text": {"content": row["その他"]}}]}
    }
    
    # リクエストデータの作成
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties
    }
    
    logging.debug("Notion API request data: %s", json.dumps(data, ensure_ascii=False))
    
    # Notionにリクエスト送信
    response = requests.post(url, headers=NOTION_HEADERS, json=data)
    return response

def final_validate_data(row):
    """Notionに送信する前の最終データ検証"""
    
    # すべてのフィールドが存在することを確認
    required_fields = ["名前", "タグ", "仕事内容", "勤務地", "勤務時間", "必須スキル", "案件タイトル", "案件内容", 
                      "歓迎スキル", "給与", "開発環境", "雇用形態", "業種業界", "ポジション", "プロダクト", 
                      "期間", "稼働率", "働き方", "期待する人物像", "その他"]
    
    for field in required_fields:
        if field not in row:
            row[field] = "情報なし"
        elif not row[field] or row[field].strip() == "":
            row[field] = "情報なし"
    
    # 文字数制限チェック（Notionの制限に合わせる）
    for field in row:
        if isinstance(row[field], str) and len(row[field]) > 2000:
            row[field] = row[field][:1997] + "..."

@app.route('/process_job', methods=['POST', 'GET'])
def process_job():
    if request.method == 'GET':
        return jsonify({"message": "APIは正常に動作しています。POSTリクエストを送信してください。"}), 200
        
    try:
        logging.debug("Received request: %s", request.json)
        content = request.json['content']
        
        # グローバル変数に保存（validate_and_fix_data関数で使用）
        global data
        data = content
        
        logging.debug("Transforming data with AI")
        transformed_data = transform_data_with_ai(content)
        logging.debug("Transformed data: %s", transformed_data)

        # CSVヘッダーを明示的に定義
        headers = ["名前", "タグ", "仕事内容", "勤務地", "勤務時間", "必須スキル", "案件タイトル", "案件内容", 
                  "歓迎スキル", "給与", "開発環境", "雇用形態", "業種業界", "ポジション", "プロダクト", 
                  "期間", "稼働率", "働き方", "期待する人物像", "その他"]
        
        # ヘッダーがない場合は追加
        if not transformed_data.startswith("名前,タグ"):
            csv_data = StringIO(transformed_data)
        else:
            # ヘッダーがある場合は除去
            lines = transformed_data.split('\n')
            if len(lines) > 1:
                csv_data = StringIO('\n'.join(lines[1:]))
            else:
                return jsonify({"message": "AIが適切なCSV形式を生成できませんでした"}), 400
        
        # CSVリーダーを作成（ヘッダーを明示的に指定）
        reader = csv.DictReader(csv_data, fieldnames=headers)
        
        try:
            row = next(reader)
            # データの検証と修正
            validate_and_fix_data(row)
            
            # 正規表現を使った直接抽出（AIの解析が不十分な場合のバックアップ）
            direct_extract_data(row, content)
                
            logging.debug("Parsed row with all fields: %s", row)
        except StopIteration:
            return jsonify({"message": "AIが適切なCSV形式を生成できませんでした"}), 400
        
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

def validate_and_fix_data(row):
    """データの検証と修正を行う関数"""
    
    # 空の値をチェック
    for key, value in row.items():
        if value is None:
            row[key] = "情報なし"
        elif isinstance(value, str) and value.strip() == '':
            row[key] = "情報なし"
        elif isinstance(value, list):
            row[key] = ", ".join(str(item) for item in value)
    
    # 特定のフィールドの検証と修正
    
    # 1. 期間フィールドの検証
    if "期間" in row:
        # 期間フィールドに技術スタックや給与情報が混入している場合
        if any(tech in row["期間"].lower() for tech in ["ruby", "rails", "jest", "typescript", "react", "aws", "docker"]):
            # 期間情報を再抽出
            row["期間"] = "情報なし"
            # 入力データから期間情報を探す
            period_pattern = re.compile(r'【作業期間】\s*・?([^【]+)')
            match = period_pattern.search(data)
            if match:
                row["期間"] = match.group(1).strip()
    
    # 2. 給与フィールドの検証
    if "給与" in row:
        # 給与情報が含まれていない場合
        if not any(word in row["給与"].lower() for word in ["万", "円", "千", "k", "万円"]):
            # 給与情報を再抽出
            salary_pattern = re.compile(r'【単金】\s*・?([^【]+)')
            match = salary_pattern.search(data)
            if match:
                row["給与"] = match.group(1).strip()
    
    # 3. 開発環境フィールドの検証
    if "開発環境" in row:
        # 開発環境に給与情報が混入している場合
        if any(word in row["開発環境"].lower() for word in ["万円", "万", "円", "85万", "単金"]):
            # 開発環境情報を再抽出
            row["開発環境"] = "情報なし"
            # 入力データから開発環境情報を探す
            env_pattern = re.compile(r'【環境】\s*[^開]*開発環境\s*([^【]+)')
            match = env_pattern.search(data)
            if match:
                env_text = match.group(1).strip()
                # 技術スタックのみを抽出（行ごとに分割して最初の数行を取得）
                env_lines = env_text.split('\n')
                if env_lines:
                    row["開発環境"] = env_lines[0].strip()
    
    # 4. タグの検証（最低3つ確保）
    if "タグ" in row:
        tags = [tag.strip() for tag in row["タグ"].split(",") if tag.strip()]
        if len(tags) < 3:
            # タグが3つ未満の場合、他のフィールドから抽出
            potential_tags = set()
            for key, value in row.items():
                if isinstance(value, str) and key not in ["タグ", "名前"]:
                    # 技術キーワードを抽出
                    for tech in ["Ruby", "Rails", "Python", "Java", "AWS", "Docker", "Web", "フロントエンド", "バックエンド", "設計", "開発"]:
                        if tech.lower() in value.lower():
                            potential_tags.add(tech)
            
            # 既存のタグと合わせる
            all_tags = set(tags) | potential_tags
            if len(all_tags) >= 3:
                row["タグ"] = ", ".join(list(all_tags)[:5])  # 最大5つまで
            else:
                # それでも足りない場合、デフォルトタグを追加
                default_tags = ["システム開発", "エンジニア", "IT"]
                all_tags = set(tags) | potential_tags | set(default_tags)
                row["タグ"] = ", ".join(list(all_tags)[:5])
    
    # 5. 勤務地の検証
    if "勤務地" in row and (row["勤務地"] == "情報なし" or not row["勤務地"]):
        # 勤務地情報を再抽出
        location_pattern = re.compile(r'【作業場所】\s*・?([^【]+)')
        match = location_pattern.search(data)
        if match:
            row["勤務地"] = match.group(1).strip()
    
    # 6. ポジションの検証
    if "ポジション" in row and (row["ポジション"] == "情報なし" or not row["ポジション"]):
        # ポジション情報を再抽出
        position_pattern = re.compile(r'【募集】\s*・?([^【]+)')
        match = position_pattern.search(data)
        if match:
            row["ポジション"] = match.group(1).strip()

def direct_extract_data(row, content):
    """正規表現を使って直接データを抽出する関数"""
    
    # 重要なフィールドを正規表現で直接抽出
    patterns = {
        "名前": r'【業務名】\s*・?([^【]+)',
        "仕事内容": r'【作業概要】\s*([^【]+)',
        "勤務地": r'【作業場所】\s*・?([^【]+)',
        "必須スキル": r'【スキル】\s*.*?<マスト>\s*([^<【]+)',
        "案件タイトル": r'【業務名】\s*・?([^【]+)',
        "歓迎スキル": r'<Better>\s*([^【]+)',
        "給与": r'【単金】\s*・?([^【]+)',
        "開発環境": r'【環境】\s*[^開]*開発環境\s*([^【]+)',
        "ポジション": r'【募集】\s*・?([^【]+)',
        "期間": r'【作業期間】\s*・?([^【]+)',
        "働き方": r'【作業場所】\s*・?([^【]+)'
    }
    
    # 各パターンでマッチングを試行
    for field, pattern in patterns.items():
        # 現在の値が「情報なし」または空の場合のみ抽出を試みる
        if field in row and (row[field] == "情報なし" or not row[field]):
            match = re.search(pattern, content, re.DOTALL)
            if match:
                extracted_value = match.group(1).strip()
                # 複数行の場合は整形
                extracted_value = re.sub(r'\s+', ' ', extracted_value)
                row[field] = extracted_value
    
    # 特殊なケース: 開発環境
    if "開発環境" in row and (row["開発環境"] == "情報なし" or "万" in row["開発環境"]):
        env_match = re.search(r'【環境】\s*.*?開発環境\s*(.*?)(?=\s*[【]|$)', content, re.DOTALL)
        if env_match:
            env_text = env_match.group(1).strip()
            # 最初の行だけを取得（技術スタックが記載されている可能性が高い）
            env_lines = env_text.split('\n')
            if env_lines:
                tech_stack = []
                for line in env_lines[:3]:  # 最初の3行まで
                    # 技術名のみを抽出
                    techs = re.findall(r'([A-Za-z0-9.]+(?:\s*[A-Za-z0-9.]+)*)', line)
                    tech_stack.extend(techs)
                if tech_stack:
                    row["開発環境"] = ", ".join(tech_stack)

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

@app.route('/test_ai_transform', methods=['POST'])
def test_ai_transform():
    try:
        content = request.json['content']
        transformed_data = transform_data_with_ai(content)
        
        # CSVヘッダーを明示的に定義
        headers = ["名前", "タグ", "仕事内容", "勤務地", "勤務時間", "必須スキル", "案件タイトル", "案件内容", 
                  "歓迎スキル", "給与", "開発環境", "雇用形態", "業種業界", "ポジション", "プロダクト", 
                  "期間", "稼働率", "働き方", "期待する人物像", "その他"]
        
        # CSVデータをパース
        csv_data = StringIO(transformed_data)
        reader = csv.DictReader(csv_data, fieldnames=headers)
        
        try:
            row = next(reader)
            return jsonify({"transformed_data": transformed_data, "parsed_data": row}), 200
        except StopIteration:
            return jsonify({"message": "AIが適切なCSV形式を生成できませんでした", "raw_data": transformed_data}), 400
            
    except Exception as e:
        logging.exception("An error occurred")
        return jsonify({"message": f"エラーが発生しました: {str(e)}"}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong", "status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # PORTが設定されていない場合はデフォルト5000を使用
    app.run(host="0.0.0.0", port=port, debug=True)
