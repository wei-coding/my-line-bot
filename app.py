from fastapi import FastAPI, Header, Request, HTTPException
from typing import Optional
from pydantic import BaseModel

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
        raise HTTPException(status_code=400, details="handle body error.")

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text[0] == '!':
        command, message = event.message.text.split('_', 1)
        command = command[1:]
        if command == 'join':
            db = json.load(open('db.json', 'r'))
            db['join'] = message
            f = open('db.json', 'w')
            json.dump(db, f)
            f.close()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="[系統提示]\n入群訊息設定成功!")
            )

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="哈囉各位")
    )

@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    f = open('db.json', 'r')
    db = json.load(f)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=db['join'])
    )
    f.close()