import logging
import colorama
import openai
import requests
import json
from ..presets import *
from ..utils import *
from ..db_loader import *
from tenacity import retry, wait_random_exponential, stop_after_attempt
from modules.db_loader import *
from .functions import functions

class OpenAIClient():
    def __init__(
        self,
        model_name,
        system_prompt="",
        temperature=1.0,
        top_p=1.0,
        stop=None,
        presence_penalty=0,
        frequency_penalty=0,
        api_key = None,
        wheather_token = None,
        functions = functions,
    ) -> None:
        self.history = []
        self.model_name = model_name
        self.interrupted = False
        self.system_prompt = system_prompt
        self.api_key = load_key()
        self.wheather_token = load_wheather_token()
        self.temperature = temperature
        self.top_p = top_p
        self.stop = stop
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        #self.functions = self.set_functions()
        self.functions = functions
      

    def predict(self, inputs,chatbot):
        """
        OpenAIのChatCompletion.create()メソッドを使用して、Chatbotの回答を取得します。
        """
        logging.info(
            "入力は：" + colorama.Fore.RED + f"{inputs}" + colorama.Style.RESET_ALL
        )
        openai.api_key = self.api_key
        # StreamモードでChatCompletion.create()メソッドを呼び出す
        self.history = []
        self.add_message("user", inputs)
        try:
            response, message = self.chat_completion_with_function_execution(self.history)
        
            if message == "function_less":
                answer = ""
                answer += response
                chatbot = [(inputs.strip(), answer)]
                print("chatbot=", chatbot)
                yield chatbot
            
            else:
                answer = ""
                for message in response:
                    content = message['choices'][0]['delta'].get('content')
                    if content != None:
                        answer += content
                    chatbot = [(inputs.strip(), answer)]
                    
                    yield chatbot
                
            print("最終回答:chatbot=", chatbot)

        except Exception as e:
            #エラーを返す
            chatbot = [(inputs.strip(), e)]
            yield chatbot

    
    def ask_weather(self, query):
        try:
            response = requests.get(OPEN_WEATHERMAP_RUL,
            params={
                "q": query,

                "appid": self.wheather_token,
                "units": "metric",
                "lang": "ja",
                }
                )
            response = json.loads(response.text)
            description = response['weather'][0]['description']
            temp_min = response['main']['temp_min']
            temp_max = response['main']['temp_max']
            return "{}の天気は{}です。最低気温は{}℃で、最大気温は{}℃です。".format(query,description,temp_min,temp_max)
        
        except Exception as e:
            # API実行に失敗した場合、エラーメッセージとともに例外を発生
            raise Exception(f"Wheather API error: {e}")

    def ask_database(self, conn, query):
        """
        指定されたSQLクエリでSQliteデータベースに問い合わせを行う関数。
        
        Return:
        conn(sqlite3.Connection):SQLiteデータベースへの接続オブジェクト。
        query(str):データベースに対して実行するSQLクエリを含む文字列。
        
        Return:
        list:  クエリの結果を含むタプルのリスト。
        
        Raises:
        Exception:SQLクエリーの実行に問題があった場合。
        """
        try:
            # 与えられたSQLiteデータベース接続オブジェクトに対してSQLクエリを実行し、すべての結果を取得
            results = conn.execute(query).fetchall()
            return results
        except Exception as e:
            # SQLクエリの実行に失敗した場合、エラーメッセージとともに例外を発生
            raise Exception(f"SQL error: {e}")


    def call_function(self, messages, full_message,functions):
        """
        excecutes function calls using model generated function arguments.
        """
        if full_message["message"]["function_call"]["name"] == "ask_database":
            query = eval(full_message["message"]["function_call"]["arguments"])
            print(f"Prepped query is {query}")
            print("query['query']=", query["query"])
            try:
                conn = db_connect()
                results = self.ask_database(conn, query["query"])
            except Exception as e:
                print(e)
                
                # SQLにエラーがある場合は自動修正を試みる。
                messages.append(
                    {
                        "role": "system",
                        "content": f"""Query: {query['query']}
                        The previous query received the error {e}.
                        Please return a fixed SQL query in plain text.
                        Your response should consist of ONLY the SQL query with the separator sql_start at the beginning and sql_end at the end""",
                    }
                )
                response = self.chat_completion_request(messages, functions)
                try:
                    cleaned_query = response["choices"][0]["message"]["content"].split("sql_start")[1]
                    cleaned_query = cleaned_query.split("sql_end")[0]
                    print(cleaned_query)
                    results = self.ask_database(conn, cleaned_query)
                    print(results)
                    print("自動修正したSQLで再実行します。")
                except Exception as e:
                    print("自動リトライでエラーが発生しました。")
                    print(f"Function execution failed")
                    print(f"Error message: {e}")
                    
            results = str(results)+ "\n" + "発行された以下のSQL文を回答に含めてください。" + "\n" + query["query"]
            print("results=",results)
            messages.append(
                {"role": "function", "name": "ask_database", "content":results } 
            )
            try:
                response = self.chat_completion_request(messages, stream=True)
                return response
            except Exception as e:
                print(type(e))
                print(e)
                raise Exception("Function ask_database request failed")

        elif full_message["message"]["function_call"]["name"] == "ask_weather":

            query = eval(full_message["message"]["function_call"]["arguments"])

            print("query['query']=", query["query"])
            try:
                results = self.ask_weather(query["query"])
            except Exception as e:
                print(e)
                
            messages.append(
                {"role": "function", "name": "ask_weather", "content": str(results)}
            )
            try:
                response = self.chat_completion_request(messages,stream=True)
                return response
            except Exception as e:
                print(type(e))
                print(e)
                raise Exception("Function ask_weather request failed")        
        else:
            raise Exception("Function does not exist and cannot be called")



    @retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self, messages,stream):
        try:
            openai.api_key = self.api_key
            response = openai.ChatCompletion.create(
                model=self.model_name,
                temperature = self.temperature,
                stream = stream,
                top_p = self.top_p,
                stop = self.stop,
                presence_penalty = self.presence_penalty,
                frequency_penalty = self.frequency_penalty,
                messages=messages,
                functions= self.functions,
                function_call="auto",
            )
            return response


        except Exception as e:
            print("Unable to generate ChatCompletion response1")
            print(f"Exception:{e}")
            return e
        
    def chat_completion_with_function_execution(self, messages):
        """
        この関数はChatCompletion APIコールを行い、関数コールが要求された場合、その関数を実行する。
        
        Parameters:
        messages(list): 会話履歴を表す文字列のリスト
        functions(list): モデルから呼び出すことができる関数を表す辞書のリスト（オプション）
        
        Return:
        dict: ChatCompletion API呼び出しによるレスポンス、または関数呼び出しの結果を含む辞書。
        """ 
        try:
            response = self.chat_completion_request(messages,stream=False)
            full_message = response["choices"][0]
            if full_message["finish_reason"] == "function_call":
                print(f"Function generation requested, calling function")
                message ="function_needed"
                return self.call_function(messages, full_message,self.functions), message
            else:
                # functionが使われない質問をした場合（ここでは回答しないように制御する）
                print(f"function not required, responding to user")
                message ="function_less"
                response = "このツールに関連しない質問にはお答えできません。"
                return response, message
                #return response["choices"][0]["message"]["content"], message
            
        except Exception as e:
            print("Unable to generate ChatCompletion response2")
            print(f"Exception:{e}")
            return e


        
    def add_message(self, role, content):
    # 会話履歴にメッセージを追加するメソッド    
        message = {"role": role, "content":content}
        self.history.append(message)
       
    def set_temperature(self, new_temperature):
        self.temperature = new_temperature
       
    def set_top_p(self, new_top_p):
        self.top_p = new_top_p

    def set_stop_sequence(self, new_stop_sequence: str):
        new_stop_sequence = new_stop_sequence.split(",")
        self.stop_sequence = new_stop_sequence

    def set_max_tokens(self, new_max_tokens):
        self.max_generation_token = new_max_tokens

    def set_presence_penalty(self, new_presence_penalty):
        self.presence_penalty = new_presence_penalty

    def set_frequency_penalty(self, new_frequency_penalty):
        self.frequency_penalty = new_frequency_penalty

    def set_system_prompt(self, new_system_prompt):
        self.system_prompt = new_system_prompt

    
    def set_key(self, new_access_key):
        self.api_key = new_access_key.strip()
        save_key(self.api_key)
        msg = "APIキーが変更されました。" + hide_middle_chars(self.api_key)
        logging.info(msg)
        return self.api_key, msg
 
 
    def set_key2(self, new_access_key):
        self.wheather_token = new_access_key.strip()
        save_key2(self.wheather_token)
        msg = "APIキーが変更されました。" + hide_middle_chars(self.wheather_token)
        logging.info(msg)
        return self.wheather_token, msg
       
    def load_config(self):
        self.api_key = load_key()
        self.wheather_token = load_wheather_token()

        return self.api_key
        
    def set_model(self, new_model):
        self.model_name = new_model.strip()
        msg = "モデルが変更されました。" + self.model_name
        logging.info(msg)
        return msg
    
    def reset(self):
        self.history = []
        msg = "会話をリセットしました。"
        logging.info(msg)
        return [] , msg


def get_model(model_name) -> OpenAIClient:
    msg = "OpenAIモデルを読み込んでいます：" + f" {model_name}"
    model = None
    try:
        
        logging.info(f"OpenAIモデルを読み込んでいます：: {model_name}")
        model = OpenAIClient(model_name=model_name)

        logging.info(msg)
    except Exception as e:
        logging.error(e)
        msg = f"{STANDARD_ERROR_MSG}: {e}"
        logging.error(msg)
    return model

