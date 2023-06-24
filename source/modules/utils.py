# -*- coding:utf-8 -*-
from modules.presets import *
import logging
import os
import json
import time
import gradio as gr

def save_key(api_key):
    data = {}
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data = json.load(f)
    data["api_key"] = api_key
    with open(KEY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_key2(api_key):
    data = {}
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data = json.load(f)
    data["api_wheather_token"] = api_key
    with open(KEY_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
def load_key():
    if not os.path.isfile(KEY_FILE):
        return None
    with open(KEY_FILE, "r") as f:
        data = json.load(f)
    return data.get("api_key")

def load_wheather_token():
    if not os.path.isfile(KEY_FILE):
        return None
    with open(KEY_FILE, "r") as f:
        data = json.load(f)
    return data.get("api_wheather_token")

def reset_textbox():
    logging.debug("テキストボックスをリセットする")
    return gr.update(value="")

def start_outputing():
    # キャンセルボタンを表示し、実行ボタンを非表示にする。
    return (
        gr.Button.update(visible=False), 
        gr.Button.update(visible=True)
    )

def end_outputing():
    # 実行ボタンを表示し、キャンセルボタンを非表示にする。
    return (
        gr.Button.update(visible=True),
        gr.Button.update(visible=False),
    )
def transfer_input(inputs):
    # 一回の応答で処理を終え、遅延を低減する
    #textbox = reset_textbox()
    #outputing = start_outputing()
    return (
        inputs,
        gr.update(value=""),
        gr.Button.update(visible=False),
        gr.Button.update(visible=True),
    )
    
      
        
def start_outputing():
    logging.debug("Cancelボタンを表示し、Sendボタンを非表示にする。")
    return gr.Button.update(visible=False), gr.Button.update(visible=True)
    
def construct_text(role, text):
    return {"role": role, "content": text}

def construct_user(text):
    return construct_text("user", text)

def construct_system(text):
    return construct_text("system", text)

def construct_assistant(text):
    return construct_text("assistant", text)
 
def reset(current_model, *args):
    """質問をリセットする"""
    return current_model.reset(*args)


def predict(current_model, inputs, chatbot):
    """
    OpenAIのChatCompletion.create()メソッドを使用して、Chatbotの回答を取得します。
    """
    iter = current_model.predict(inputs, chatbot)
    for chatbot in iter:
        time.sleep(0.03)
        yield chatbot

def set_temperature(current_model, *args):
    current_model.set_temperature(*args)
    
def set_top_p(current_model, *args):
    current_model.set_top_p(*args)
    
def set_stop_sequence(current_model, *args):
    current_model.set_stop_sequence(*args)
    
def set_presence_penalty(current_model, *args):
    current_model.set_presence_penalty(*args)

def set_frequency_penalty(current_model, *args):
    current_model.set_frequency_penalty(*args)
           
def set_key(current_model, *args):
    return current_model.set_key(*args)

def set_key2(current_model, *args):
    return current_model.set_key2(*args)

def set_model(current_model, *args):
    return current_model.set_model(*args)

def hide_middle_chars(s):
    if s is None:
        return ""
    if len(s) <= 8:
        return s
    else:
        head = s[:4]
        tail = s[-4:]
        hidden = "*" * (len(s) - 8)
        return head + hidden + tail
    
    
