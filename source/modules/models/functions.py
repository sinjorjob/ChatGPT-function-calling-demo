# データベーススキーマを関数に挿入していることに注意。
# これはモデルが知るべき重要な情報
from ..db_loader import *
database_schema_string = get_db_schema(db_connect()),


functions=[
    {
        "name": "ask_database",
        "description": "この関数を使用して、音楽に関するユーザーの質問に答えます。出力は完全に形成されたSQLクエリでなければなりません。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        ユーザーの質問に答えるための情報を抽出するSQLクエリ。
                        SQLは、以下のデータベーススキーマを使って書かなければならない：
                        データベーススキーマ：{database_schema_string}
                        クエリーはJSONではなく、プレーンテキストで返す必要があります。
                    """,
                },
            },
            "required": ["query"],
        },
    },

    {
        "name": "ask_weather",
        "description": "この関数を使用して特定の都市の天気情報の質問に答えます。都市名のプレーンテキストでなければなりません。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                        ユーザーの質問に答えるため、知りたい天気情報の都市名を返さなければならない。
                        例：
                        【質問】：「東京都のお天気情報を教えてください。」
                        【回答】：東京都
                    """,
                },
            },
            "required": ["query"],
        },
    },

]