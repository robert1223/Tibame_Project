import requests
import json
from linebot import LineBotApi, WebhookHandler

# 讀取linebot相關訊息
secretFile = json.load(open('secretFile.txt', 'r'))

# 製作Line菜單選項
# 需使用POST方法將機器人的channelAccessToken，及要設定的Menu介面帶到Line的指定api接口
headers = {
           "Authorization": 'Bearer '+secretFile['channelAccessToken'],
           "Content-Type": "application/json"
           }

body = {
    "size": {"width": 2500, "height": 843},
    "selected": "true",
    "name": "ceb102_project",
    "chatBarText": "查看更多資訊",
    'areas': [
        # {
        # "bounds": {"x": 0, "y": 0, "width": 1000, "height": 843},
        # "action": {"type": "uri", "label": "", "uri": "https://e49b5ade1949.ngrok.io/?userID=Ue5fb50f1e370cd5c0ff2cacc6515dada"}
        # },
        {
        "bounds": {"x": 0, "y": 0, "width": 1000, "height": 843},
        "action": {"type": "message", "label": "加入會員", "text": "加入會員"}
        },

        {
        "bounds": {"x": 1001, "y": 0, "width": 750, "height": 843},
        "action": {"type": "message", "label": "主題推薦", "text": "主題推薦"}
        },
        {
        "bounds": {"x": 1752, "y": 0, "width": 750, "height": 843},
        "action": {"type": "message", "label": "功能提示", "text": "功能提示"}
        }
    ]
}

req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
                       headers=headers, data=json.dumps(body).encode('utf-8'))
print(req)  # 測試是否成功 => response[200]
RichMenuID = json.loads(req.text)["richMenuId"]  # 回傳內容是用字串包著的dict，用json.loads轉成dict，再取值
print(RichMenuID)
print('----------')

# 將圖片設定到Rich Menu
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
with open("./RichMenuIMG/test.jpg", 'rb') as f:
    line_bot_api.set_rich_menu_image(RichMenuID, "image/jpeg", f)
result = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/' + RichMenuID,
                          headers = headers)
print(result.text)  # 測試是否成功 = > {}

