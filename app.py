from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

import os

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
    # command starts with '!'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
