from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, JoinEvent, FollowEvent
)

import os
import sqlite3
import load_env
from datetime import datetime
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

WAIT_TIME = 3600

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

@handler.add(FollowEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="受人之託，忠人之事。我們往生堂性質特殊肩付著雙倍責任，一定會讓兩個世界的人都滿意。"),
            TextSendMessage(text="往生堂LineBot讓您更方便接收我們的服務及活動資訊！"),
            TextSendMessage(text="輸入 ”kurumi” 可查看可輸入指令。")
        ]
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    command = event.message.text
    if command == 'kurumi':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="往生堂堂主在此聽候差遣，以下為可輸入指令：\n"
                "限時活動\n"
                "抽木牌\n"
                "查看木牌\n"
                "七七")
        )
    elif command == '限時活動':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="11月4日至12月25日，往生堂提供一日往生體驗服務，全程免費！\n"
                "帶伴侶來還可以體驗我們的「在天願作比翼鳥」服務！\n"
                "真的很不錯，歡迎來體驗！")
        )
    elif command == '抽木牌':
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
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text="抽木牌規則，每七天可祈願一次，祈願後，七天後才能再次祈願！"),
                        TextSendMessage(text="哦呀？哦呀呀？不久前才抽過才對，別這麼急著跨越生死的邊界嘛！"),
                    ]
                )
        else:
            lucky = random_choice()[1]
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text="抽木牌規則，每七天可祈願一次，祈願後，七天後才能再次祈願！"),
                    TextSendMessage(text=f"（來看看木牌後面有什麼字吧）\n{REWARD_LIST[lucky][0]}"),
                ]
            )
            c.execute("INSERT INTO customer (customer_id, reward_id) VALUES (?, ?)", [event.source.user_id, lucky])
            conn.commit()
            conn.close()
    elif command == "七七":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="看到七七了嗎？快告訴我她在哪，我要把她藏起來，嘿！")
        )
    elif command == "查看木牌":
        conn = sqlite3.connect("mydb.db")
        c = conn.cursor()
        c.execute("SELECT `reward_id` FROM `customer` WHERE `customer_id` = ?", (event.source.user_id, ))
        r = c.fetchone()
        if r:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="來看看搜集的木牌有什麼吧！\n"
                    f"{REWARD_LIST[r[0]][0]}"
                )
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="來看看搜集的木牌有什麼吧！\n"
                    "你還沒有抽過木牌喔~"
                )
            )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="無望坡不是一般人會踏足的地方，是迷路了嗎？有需要的話叫我（kurumi)，我可以為你指路。")
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
