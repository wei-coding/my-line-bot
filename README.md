# Line 群組機器人

原本是遊戲公會內的機器人在新人加入時很容易出現沒有發送歡迎詞的狀況，想重寫一個來代替

~~目前只支援單一server對應一line群組~~ 8/5更新已支援

## 架構

使用python faatapi + line bot sdk開發，要保存的資料會自動寫入`db.json`

## 使用方法

**記得改token和secret，預設是在系統環境變數的`TOKEN`和`SECRET`下**
**若有`.env`檔案，可以直接`from load_env import dotenv`後`dotenv.load_env()`**

- `\.env`
```
TOKEN = "MYTOKEN"
SECRET = "MYSECRET"
```

```
pip install -r requirements.txt
uvicorn app:app --host=0.0.0.0 --port=80
```

再開一個命令列

```
ngrok http 80
```

依照提示將網址填入line後端即可

## 開發

若要新增或修改指令可查看`app.py`的`handle_message`函數，內有註解

## 開發日誌

* 7/22:第一版上線
* 8/5:新增`!help`、運勢等功能，支援多群組