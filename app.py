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
import sqlite3
import random
import load_env
from utils.reward import random_choice, REWARD_LIST

app = Flask(__name__)
conn = sqlite3.connect("mydb.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS `customer`(
    `customer_id` INT PRIMERY KEY,
    `reward_id` INT,
    `timestamp` TIMESTAMP DEFAULT (datetime('now', 'localtime')) NOT NULL
)
""")
conn.commit()
c.close()
conn.close()

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

        if command == '抽獎':
            lucky = random_choice()[1]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{REWARD_LIST[lucky]}")
            )
            conn = sqlite3.connect("mydb.db")
            c = conn.cursor()
            c.execute("INSERT INTO customer (customer_id, reward_id) VALUES (?, ?)", [event.source.user_id, REWARD_LIST.index(lucky)])
            conn.commit()
            
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
