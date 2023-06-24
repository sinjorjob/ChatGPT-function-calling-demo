
import gradio as gr
from modules.presets import *
from modules.utils import *
from modules.models.models import get_model


with open("assets/custom.css", "r", encoding="utf-8") as f:
    customCSS = f.read()

def create_new_model():
    current_model = get_model(model_name = ONLINE_MODELS[DEFAULT_MODEL])
    return current_model


with gr.Blocks(css=customCSS, theme='gradio/soft') as demo:
    user_name = gr.State("")
    user_question = gr.State("")
    user_api_key = gr.State(load_key())
    user_api_key2 = gr.State(load_wheather_token())
    current_model = gr.State(create_new_model)
    with gr.Row():
        gr.HTML(CHUANHU_TITLE, elem_id="app_title")
        status_display = gr.Markdown(elem_id="status_display")
        
    #画面左側のメインエリアの定義
    with gr.Row().style(equal_height=True):
        
        with gr.Column(scale=5):
            gr.Markdown(APP_DESCRIPTION)
            with gr.Row():
                chatbot = gr.Chatbot(elem_id="chuanhu_chatbot").style(height="100%")
            with gr.Row():
                with gr.Column(min_width=225, scale=10):
                    user_input = gr.Textbox(
                        elem_id="user_input_tb",
                        show_label=False, placeholder=("ここに入力してください"),
                        lines = 1,
                    ).style(container=False)
                with gr.Column(min_width=42, scale=2):
                    submitBtn = gr.Button(value="実行",variant="primary", elem_id="submit_btn",)
             

                    cancelBtn = gr.Button(value="キャンセル", visible=False, elem_id="cancel_btn")
            with gr.Row():
                emptyBtn = gr.Button(
                    ("\U0001F195 新しい会話♪"), elem_id="empty_btn"
                )
     

        with gr.Column():
            with gr.Column(min_width=50, scale=1):
                with gr.Tab(label=("基本設定")):
                    keyTxt = gr.Textbox(
                        show_label=True,
                        placeholder=f"OpenAIのAPI-keyをここに入力してください...",
                        value=load_key(),
                        type="password",
                        visible=True,
                        label="OpenAI-API-Key",
                    )
                    keyTxt2 = gr.Textbox(
                        show_label=True,
                        placeholder=f"OpenWeatherMAPのAPI-keyをここに入力してください...",
                        value=load_wheather_token(),
                        type="password",
                        visible=True,
                        label="Open-WeatherMap-API-Key",
                    )                    
                    model_select_dropdown = gr.Dropdown(
                        label=("OpenAIモデルを選択してください。"), choices=ONLINE_MODELS, multiselect=False, value=ONLINE_MODELS[DEFAULT_MODEL], interactive=True
                    )
                    use_streaming_checkbox = gr.Checkbox(
                        label=("ストリーム出力"), 
                        value=True,
                        info="出力結果をリアルタイムに表示するモード")


                    
                with gr.Tab(label=("詳細設定")):
                    gr.Markdown(("# ⚠️ 変更は慎重に ⚠️\n\nもし動作しない場合は、デフォルト設定に戻してください。"))
                    
                    temperature_slider = gr.Slider(
                        minimum=-0,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        interactive=True,
                        label="temperature",
                        info="0に近づく程回答が固定、2に近づくほどランダムになる(Default=1)"
                    )
                    top_p_slider = gr.Slider(
                        minimum=-0,
                        maximum=1.0,
                        value=1.0,
                        step=0.05,
                        interactive=True,
                        label="top-p",
                        info="1に近づくほど多彩な単語が出力される(Default=1)"
                    )
                    stop_sequence_txt = gr.Textbox(
                        show_label=True,
                        placeholder=("ここにストップ文字を英語のカンマで区切って入力してください..."),
                        label="stop",
                        value="",
                        lines=1,
                        info="指定した文字にマッチした場合に回答の出力をストップする",
                    )

                    presence_penalty_slider = gr.Slider(
                        minimum=-2.0,
                        maximum=2.0,
                        value=0.0,
                        step=0.01,
                        interactive=True,
                        label="presence penalty",
                        info="値が大きいほど新しいネタを提案してくれる可能性が上がる(Default=0)"
                    )
                    frequency_penalty_slider = gr.Slider(
                        minimum=-2.0,
                        maximum=2.0,
                        value=0.0,
                        step=0.01,
                        interactive=True,
                        label="frequency penalty",
                        info="値が大きいほど同じ単語が出現する確率が低下する(Default=0)"
                    )



                                       
    # 前処理(実行ボタンを非表示にしてキャンセルボタンをアクティブ化)
    transfer_input_args = dict(
        fn=transfer_input, inputs=[user_input], outputs=[user_question, user_input, submitBtn, cancelBtn], show_progress=True
    )
    # 後処理(キャンセルボタンを非表示にして実行ボタンをアクティブ化)
    end_outputing_args = dict(
        fn=end_outputing, inputs=[], outputs=[submitBtn, cancelBtn]
    )
    # ChatGPT-APIをCall
    chatgpt_predict_args = dict(
        fn=predict,
        inputs=[
            current_model,  #OpenAIのモデルインスタンス
            user_question,  #ユーザの入力文
            chatbot,  #初期は空
        ],
        outputs=[chatbot],  # 戻り値の形式 →   [('<質問文>','<回答文>')]
        show_progress=True,
    )

    #API-CALL
    submitBtn.click(**transfer_input_args).then(**chatgpt_predict_args, api_name="predict").then(**end_outputing_args)

    #質問をリセット
    emptyBtn.click(reset,inputs=[current_model],outputs=[chatbot, status_display],show_progress=True,)   

    
    def create_greeting(request: gr.Request):
        current_model = get_model(model_name = ONLINE_MODELS[DEFAULT_MODEL])
        current_model.load_config() #API_KEYのロード

        return current_model

    demo.load(inputs=None, outputs=[ current_model], api_name="load")
    
   
    #詳細設定のパラメータ変更を反映
    temperature_slider.change(set_temperature, [current_model, temperature_slider], None)
    top_p_slider.change(set_top_p, [current_model, top_p_slider], None)
    stop_sequence_txt.change(set_stop_sequence, [current_model, stop_sequence_txt], None)
    presence_penalty_slider.change(set_presence_penalty, [current_model, presence_penalty_slider], None)
    frequency_penalty_slider.change(set_frequency_penalty, [current_model, frequency_penalty_slider], None)

    # OpenAI_API_Keyの更新
    keyTxt.change(set_key, [current_model, keyTxt], [user_api_key, status_display], api_name="set_key")
    # WeatherMap_API_Keyの更新
    keyTxt2.change(set_key2, [current_model, keyTxt2], [user_api_key2, status_display], api_name="set_key2")

    # モデルの選択
    model_select_dropdown.change(set_model, [current_model,model_select_dropdown], [status_display] ,api_name="get_model")
if __name__ == "__main__":
    demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
        server_port=7777,
    )


