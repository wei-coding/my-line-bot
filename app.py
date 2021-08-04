from fastapi import FastAPI, Header, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, JoinEvent
)
from linebot.models.events import MemberJoinedEvent

import os
import json
import random

# from load_env import dotenv
# dotenv.load_env()

app = FastAPI()

token = os.environ['TOKEN']
secret = os.environ['SECRET']
line_bot_api = LineBotApi(token)
handler = WebhookHandler(secret)

if not os.path.exists('db.json'):
    f = open('db.json', 'w')
    json.dump({}, f)
    f.close()

@app.post("/callback")
async def callback(request: Request, X_Line_Signature: Optional[str] = Header(None)):

    # get request body as text
    body = await request.body()

    # handle webhook body
    try:
        handler.handle(body.decode("utf-8"), X_Line_Signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="handle body error.")

    return 'OK'

@app.get("/test")
async def test(request: Request):
    return 'Server is running!'

# handle event: please check https://developers.line.biz/en/reference/messaging-api/#webhook-event-objects for all event

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # command starts with '!'
    if event.message.text[0] == '!':
        group_id = event.source.group_id
        try:
            command, message = event.message.text.split('_', 1)
        except ValueError:
            command = event.message.text
            message = None
        command = command[1:]
        if command == 'join':
            db = json.load(open('db.json', 'r'))
            db[group_id] = {'join': message}
            f = open('db.json', 'w')
            json.dump(db, f)
            f.close()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="[系統提示]\n入群訊息設定成功!")
            )
        if command == 'test':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="[系統提示]\n測試成功，系統正常運行!")
            )
        if command == 'help':
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="[系統提示]\n"
                "!help:顯示此訊息\n"
                "!join:入群提示設定，\"_\"後方為入群要顯示的訊息\n"
                "!test:測試服務是否正常運行")
            )
        # add your commad here
        # if command == 'some_command':
        #   do_something_here()
    if event.message.text.find("運勢") != -1:
        subject = event.message.text.split("運勢")[0]
        rand_num = random.randint(30, 99)
        def _rand_comment():
            if rand_num < 50:
                return "QQ"
            elif rand_num < 70:
                return "還不錯喔"
            elif rand_num < 90:
                return "真是幸運"
            else:
                return "你去買樂透吧!"
        reply = "{}幸運指數是{}，{}".format(subject, rand_num, _rand_comment())
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="哈囉各位")
    )

@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    group_id = event.source.group_id
    f = open('db.json', 'r')
    db = json.load(f)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=db[group_id]['join'])
    )
    f.close()