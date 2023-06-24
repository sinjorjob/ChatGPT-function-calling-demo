import sqlite3
from .presets import *


def db_connect():
    """SQLiteDBへ接続"""
    conn = sqlite3.connect(DB_FILE) 
    print("database connection OK")
    return conn


def get_table_names(conn):
    """テーブル名のリストを返す"""
    table_names = []
    tables = conn.execute("select name from sqlite_master where type='table';")
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names

def get_column_names(conn, table_name):
    """テーブルのカラム名のリストを返す"""
    column_names = []
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        column_names.append(col[1])
    return column_names

def get_database_info(conn):
    """テーブル名とカラムの情報を辞書のリストで返す"""
    table_dicts = []
    for table_name in get_table_names(conn):
        columns_names = get_column_names(conn, table_name)
        table_dicts.append({"table_name": table_name, "column_names": columns_names})
    return table_dicts


def get_db_schema(conn):    
    """
    この行は、get_database_info()が返す辞書のリストを繰り返し、各テーブル名とカラム名を
    整形することで、データベーススキーマの文字列表現を作成する。
    get_database_info()が返す辞書のリストを繰り返し、各テーブルのテーブル名とカラム名を
    フォーマットすることで、データベーススキーマの文字列表現を作成します。    
    """
    database_schema_dict = get_database_info(conn)

    database_schema_string = "\n".join(
        f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
        for table in database_schema_dict
    )
    return database_schema_string