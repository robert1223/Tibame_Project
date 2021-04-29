# 載入相關套件
from flask import Flask, request, abort
from datetime import datetime
import json
import mysql.connector

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
# from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage , TemplateSendMessage , CarouselTemplate
from linebot.models import *


# 讀取linebot和mysql連線資訊
secretFile = json.load(open('./secretFile.txt', 'r'))

# 建立Flask
app = Flask(__name__)

# 讀取LineBot驗證資訊
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
handler = WebhookHandler(secretFile['channelSecret'])





# linebot接收訊息
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value: 驗證訊息來源
    signature = request.headers['X-Line-Signature']

    # get request body as text: 讀取訊息內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# linebot處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # 使用者ID
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id, timeout=None)

    # 製作主題字典，用來if-else判斷
    ThemeDict = {"增肌減脂": 0, "美白保養": 1, "提神醒腦": 2, "終結疲勞": 3, "護眼保固": 4}


    if event.message.text == '功能提示':
        # linebot回傳訊息

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='''歡迎使用功能提示:
        \n若想利用食材來搜尋食譜，可以透過\n🍴傳送食材照片\n或是\n🍴輸入食材關鍵字\n來搜尋(ex.雞肉)
        \n另外還可以按\n🍴主題推薦\n我們將推薦各類型的主題食譜給您喔!''')
        )

    elif event.message.text == '加入會員':

        # linebot回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='https://e49b5ade1949.ngrok.io/?userID={}'.format(user_id))
        )

    elif event.message.text == '主題推薦':

        message = ImagemapSendMessage(
            base_url="https://i.imgur.com/1Wo4oxD.jpg",  # 暫時測試用圖片
            # base_url=
            alt_text="主題推薦",
            base_size=BaseSize(height=2000, width=2000),
            actions=[
                MessageImagemapAction(
                    text='增肌減脂',
                    area=ImagemapArea(x=0, y=0, width=1000, height=1000)
                    ),
                MessageImagemapAction(
                    text='美白保養',
                    area=ImagemapArea(x=1000, y=0, width=1000, height=1000)
                    ),
                MessageImagemapAction(
                    text='提神醒腦',
                    area=ImagemapArea(x=0, y=1000, width=1000, height=1000)
                    ),
                MessageImagemapAction(
                    text='終結疲勞',
                    area=ImagemapArea(x=1000, y=1000, width=1000, height=1000)
                    ),
                ]
        )
        # linebot回傳訊息
        line_bot_api.reply_message(event.reply_token, message)
        # print(user_id)
        # print(profile)



    elif event.message.text in ThemeDict.keys():

        import Carousel_template

        # 連線資料庫，將資料抓出
        conn = mysql.connector.connect(
            host=secretFile['host'],  # 連線主機名稱
            port=secretFile['port'],  # 連線主機port號
            user=secretFile['user'],  # 登入帳號
            password=secretFile['passwd'])  # 登入密碼
        cursor = conn.cursor()
        query = "select Recipeid, RecipeName from ceb102_project.營養素分群_final where `group` = {};"\
            .format(ThemeDict[event.message.text])
        cursor.execute(query)
        RecipesInformation = cursor.fetchall()[:5]
        conn.close()

        # 設定回傳訊息的物件
        message = Carousel_template.CarouselTemplate_icook(RecipesInformation)
        # linebot回傳訊息
        line_bot_api.reply_message(event.reply_token, message)




# 收到"我喜歡"的 PostbackEvent，儲存使用者喜好方便推薦系統分析
@handler.add(PostbackEvent)
def add_favorite(event):

    # 使用者ID
    user_id = event.source.user_id
    user_data = event.postback.data

    # 儲存使用者搜尋紀錄
    while True:
        try:
            conn = mysql.connector.connect(
                host=secretFile['host'],  # 連線主機名稱
                port=secretFile['port'],  # 連線主機port號
                user=secretFile['user'],  # 登入帳號
                password=secretFile['passwd'])  # 登入密碼
            cursor = conn.cursor()
            query = 'INSERT INTO linebot.UserFavorite (UserID, Time, Favorite) VALUES (%s, %s, %s)'
            value = (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_data)
            cursor.execute(query, value)
            conn.commit()
            conn.close()
            # print(user_id)
            break
        except Exception as e:
            print('連線失敗:', e)
            break



# linebot處理照片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):

    # 使用者ID
    user_id = event.source.user_id

    # 使用者傳送的照片
    message_content = line_bot_api.get_message_content(event.message.id)

    # 照片儲存名稱
    fileName = event.message.id + '.jpg'

    # 儲存照片
    with open('./image/' + fileName, 'wb')as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # linebot回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='收到您上傳的照片囉!'))

    # 將照片路徑資訊紀錄至資料庫
    while True:
        try:
            conn = mysql.connector.connect(
                host=secretFile['host'],  # 連線主機名稱
                port=secretFile['port'],  # 連線主機port號
                user=secretFile['user'],  # 登入帳號
                password=secretFile['passwd'])  # 登入密碼
            cursor = conn.cursor()
            query = 'INSERT INTO linebot.upload_fig (time, file_path) VALUES (%s, %s)'
            value = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fileName)
            cursor.execute(query, value)
            conn.commit()
            conn.close()
            break
        except:
            pass


# 開始運作Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) # 0.0.0.0 全部人都可以進入 port預設為5000
