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
from datetime import datetime, timedelta

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

@app.route('/table')
def table():
    conn = sqlite3.connect('mydb.db')
    c = conn.cursor()
    c.execute("SELECT * FROM `customer`")
    r = c.fetchall()
    print(r)
    r_str = ""
    for row in r:
        r_str += f"[{row[2]}]\t<span style=\"color: red\">{row[0]}</span>顧客抽到了<span style=\"color: red;\">{REWARD_LIST[row[1]][0]}<span>\n"
    return r_str

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
            conn = sqlite3.connect("mydb.db")
            c = conn.cursor()
            c.execute("SELECT `timestamp` FROM `customer` WHERE `customer_id` = ?", (event.source.user_id, ))
            r = c.fetchone()
            if r:
                print(r[0])
                last_timestamp = datetime.strptime(r[0], '%Y-%m-%d %H:%M:%S')
                now_timestamp = datetime.now()
                delta = now_timestamp - last_timestamp
                if delta.seconds >= 3600:
                    lucky = random_choice()[1]
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"{REWARD_LIST[lucky][0]}")
                    )
                    c.execute("INSERT INTO `customer` (customer_id, reward_id) VALUES (?, ?)", [event.source.user_id, lucky])
                    conn.commit()
                    conn.close()
                else:
                    left = timedelta(hours=1) - delta
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"還要再{format_timedelta(left)}才能再抽獎喔!")
                    )
            else:
                lucky = random_choice()[1]
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{REWARD_LIST[lucky][0]}")
                )
                c.execute("INSERT INTO customer (customer_id, reward_id) VALUES (?, ?)", [event.source.user_id, lucky])
                conn.commit()
                conn.close()

            
def format_timedelta(delta: timedelta) -> str:
    """Formats a timedelta duration to [N days] %H:%M:%S format"""
    seconds = int(delta.total_seconds())

    secs_in_a_day = 86400
    secs_in_a_hour = 3600
    secs_in_a_min = 60

    days, seconds = divmod(seconds, secs_in_a_day)
    hours, seconds = divmod(seconds, secs_in_a_hour)
    minutes, seconds = divmod(seconds, secs_in_a_min)

    time_fmt = f"{hours:02d}小時{minutes:02d}分{seconds:02d}秒"

    if days > 0:
        suffix = "s" if days > 1 else ""
        return f"{days} day{suffix} {time_fmt}"

    return time_fmt
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
