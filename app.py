from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
)

import os

import sqlite3

import random


from load_env import dotenv
dotenv.load_env()

app = Flask(__name__)

token = os.environ['TOKEN']
secret = os.environ['SECRET']
line_bot_api = LineBotApi(token)
handler = WebhookHandler(secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@app.route("/test")
def test():
    return 'Server is running!'

# handle event: please check https://developers.line.biz/en/reference/messaging-api/#webhook-event-objects for all event

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    is_account = 0
    # command start with "!"
    if event.message.text[0] == '!':
        command = event.message.text.split('!')[-1]
        if command == '今日運勢':
            lucky = random.randint(60, 100)
            hint = "還不錯喔" if lucky >= 80 else "運氣有點差"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"今天運氣指數{lucky}，{hint}")
            )

        if command == '記帳':
            # TODO
            is_account = 1
            text_message = TextSendMessage(text='請選擇分類，或是自行手動輸入',
                               quick_reply=QuickReply(items=[
                                   QuickReplyButton(action=MessageAction(label="吃的", text="吃的")),
                                   QuickReplyButton(action=MessageAction(label="喝的", text="喝的")),
                                   QuickReplyButton(action=MessageAction(label="用的", text="用的"))
                               ]))
            line_bot_api.reply_message(
                event.reply_token,
                text_message
            )
        

        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text=command)
        # )
    if is_account:
        # TODO
        if event.message.text == '吃的':
            None
        elif event.message.text == '喝的':
            None
        elif event.message.text == '用的':
            None
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
