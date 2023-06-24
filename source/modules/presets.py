import os
# 現在のスクリプトのディレクトリパスを取得
script_dir = os.path.dirname(__file__)

CHUANHU_TITLE =("&#x1f30e; ChatGPT-Function-Calling-API &#x1f30e;")
APP_DESCRIPTION = """
## ChatGPT APIのFunction calling機能を使ったデモアプリです。
| Function | 説明 | 例 |
| :--- | :--- | :--- |
| DB問合せ機能 | アルバムの売上データ(SQliteDB)から取得したいデータをテキスト文章で問合せることができる機能 | <b>[Question]</b>:売れているTOP3のアルバムは何ですか？<br><b>[Answer]</b>:売れているTOP3のアルバムは「Minha Historia」、「Greatest Hits」、「Unplugged」です。 |
| 天気機能 | お天気APIをCALLして都道府県の天気情報（天気、最低気温、最高気温）を返す機能。 |<b>[Question]</b>:東京都の天気を教えてください！<br><b>[Answer]</b>:東京都の天気は厚い雲で、最低気温は21.27℃、最高気温は24.37℃です。 |

※上記に関係ない質問についてはLLM(GPT-3.5-turbo-16k)が普通に回答を生成して返します。
"""

USAGE_API_URL="https://api.openai.com/dashboard/billing/usage"
#DB_FILE = r"C:\Users\sinfo\Desktop\chatgpt\chatgpt-func-calling\source\database\chinook.db"
DB_FILE = os.path.join(script_dir, "..", "database", "chinook.db")
KEY_FILE = "config.json"

ONLINE_MODELS = [
    "gpt-3.5-turbo-16k",
]
DEFAULT_MODEL = 0

# ChatGPTの設定
COMPLETION_URL = "https://api.openai.com/v1/chat/completions"
OPEN_WEATHERMAP_RUL = "https://api.openweathermap.org/data/2.5/weather"

# エラーメッセージ
STANDARD_ERROR_MSG = "☹️一般的なエラーメッセージの先頭に表示される標準的な接頭辞を示す。" 

CONCURRENT_COUNT = 100 # 同時に使用できるユーザー数の上限
