# Line 群組機器人

原本是遊戲公會內的機器人在新人加入時很容易出現沒有發送歡迎詞的狀況，想重寫一個來代替

**此為分支版本，使用`flask`架設**

## 架構

使用python flask + line bot sdk開發

## 使用方法

**記得改token和secret，預設是在系統環境變數的`TOKEN`和`SECRET`下**
**若有`.env`檔案，可以直接`import load_env`**

- `\.env`
```
TOKEN = "MYTOKEN"
SECRET = "MYSECRET"
```

```
pip install -r requirements.txt
python app.py
```

再開一個命令列

```
ngrok http 8000
```

依照提示將網址填入line後端即可