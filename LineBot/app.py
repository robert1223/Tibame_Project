# 載入相關套件
from flask import Flask, request, abort, send_file, render_template
from datetime import datetime
import json
from sqlalchemy import create_engine
import pandas as pd
import pymysql

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *


# 讀取linebot和mysql連線資訊
secretFile = json.load(open('./secretFile.txt', 'r'))

# 建立Flask
app = Flask(__name__, static_folder='./static', static_url_path='/static')

# 讀取LineBot驗證資訊
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
handler = WebhookHandler(secretFile['channelSecret'])

# 讀取資料庫中食材名稱，放入List，用來比對使用者傳入食材名稱
conn = pymysql.connect(
            host=secretFile['host'],  # 連線主機名稱
            port=secretFile['port'],  # 連線主機port號
            user=secretFile['user'],  # 登入帳號
            password=secretFile['passwd'])  # 登入密碼
cursor = conn.cursor()
query = 'SELECT Ingredient FROM ceb102_project.Ingredient_icook_1;'
cursor.execute(query)
Ingredients = cursor.fetchall()
conn.close()

# 抓出來的資料每一筆都是tuple，將其轉成字串放入list
IngredientsList = []
for Ingredient in Ingredients:
    IngredientsList.append(Ingredient[0])

dict = {}


# 存放食譜相關圖片網站
@app.route("/picture", methods=['GET'])
def picture():
    file_path = './static/{}.jpg'.format(request.args.get('RecipeID'))
    return send_file(file_path, mimetype='image/jpg')
    # return '<img src=/static/{}.jpg>'.format(request.args.get('RecipeID'))



# 使用者填寫基本資料網站
@app.route("/apply" ,  methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        userID = request.args.get('userID')   #?userID=12345678aaasss
        dict['UserID'] = userID
        print(userID)

    if request.method == 'POST':
        dict['UserName'] = request.form.get('username')
        dict['gender'] = request.form.get('gender')
        dict['age'] = request.form.get('age')
        dict['height'] = request.form.get('height')
        dict['weight'] = request.form.get('weight')
        dict['exercise'] = request.form.get('exercise')
        dict['job'] = str(request.form.getlist('job'))  # 多選list
        dict['style'] = str(request.form.getlist('style'))
        dict['date'] = datetime.now().strftime("%Y-%m-%d")
        print(dict)
        df = pd.DataFrame([dict])

        # 建立資料庫連線引擎
        connect = create_engine('mysql+pymysql://root:ceb102@18.183.16.220:3306/linebot?charset=utf8mb4')
        df.to_sql(name='UserInformation', con=connect, if_exists='append', index=False)

        return render_template("thank.html")

    return render_template("questionnaire.html")



# Linebot接收訊息
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value: 驗證訊息來源(數位簽章)
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


# Linebot處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # 使用者ID
    user_id = event.source.user_id


    # 製作主題字典，用來if-else判斷
    ThemeDict = {"增肌減脂": 0, "美白保養": 1, "提神醒腦": 2, "終結疲勞": 3, "保護眼睛": 4}

    if event.message.text == '小幫手':

        # linebot回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='''歡迎使用小幫手功能:
        \n若想利用食材來搜尋食譜，可以透過\n🍴傳送食材照片\n或是\n🍴輸入食材關鍵字\n來搜尋(ex.雞肉)
        \n另外還可以按\n🍴主題推薦\n我們將推薦各類型的主題食譜給您喔!''')
        )

    elif event.message.text == '加入會員':

        # Linebot回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='https://7011417f79ab.ngrok.io/apply?userID={}'.format(user_id))  # ngrok
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
                    # ),
                # MessageImagemapAction(
                #     text='保護眼睛',
                #     area=ImagemapArea(x=0, y=0, width=0, height=0)
                )
                ]
        )
        # Linebot回傳訊息
        line_bot_api.reply_message(event.reply_token, message)


    # 判斷是否符合主題文字(增肌減脂、美白保養.....等)
    elif event.message.text in ThemeDict.keys():

        import Carousel_template

        # 連線資料庫，將資料抓出
        conn = pymysql.connect(
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

        # 設定回傳訊息的物件(旋轉木馬訊息)
        message = Carousel_template.CarouselTemplate_icook(RecipesInformation)
        # Linebot回傳訊息
        line_bot_api.reply_message(event.reply_token, message)

    # 使用者用食材搜尋時
    elif event.message.text in IngredientsList:

        Ingredient = event.message.text

        # MyPackage
        import Carousel_template
        import Match

        # 連線資料庫，將使用者搜尋的食材相關食譜抓出，在依照使用者喜好的風格做比對推薦
        recommend = Match.Recipe_Match(secretFile, user_id, Ingredient)
        # 設定回傳訊息的物件
        message = Carousel_template.CarouselTemplate_icook(recommend)
        # # linebot回傳訊息
        line_bot_api.reply_message(event.reply_token, message)

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='''很抱歉!無法搜尋您的資料''')
        )



# 收到"我喜歡"的 PostbackEvent，儲存使用者喜好方便推薦系統分析
@handler.add(PostbackEvent)
def add_favorite(event):

    # 使用者ID
    user_id = event.source.user_id
    user_data = event.postback.data # 使用者按下"我喜歡"的PostbackTemplateAction後，裡面會有記錄該筆食譜的ID(data)，把data取出存入DB

    # 儲存使用者搜尋紀錄
    while True:
        try:
            conn = pymysql.connect(
                host=secretFile['host'],  # 連線主機名稱
                port=secretFile['port'],  # 連線主機port號
                user=secretFile['user'],  # 登入帳號
                password=secretFile['passwd'])  # 登入密碼
            cursor = conn.cursor()
            query = 'INSERT INTO linebot.UserPreferences (UserID, Preference, Time) VALUES (%s, %s, %s)'
            value = (user_id, user_data, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute(query, value)
            conn.commit()
            conn.close()
            print('已將資料存進資料庫')
            break
        except Exception as e:
            print('連線失敗:', e)
            pass



# linebot處理照片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):

    # 使用者ID
    user_id = event.source.user_id

    # 使用者傳送的照片
    Img_message_content = line_bot_api.get_message_content(event.message.id)  # type :
                                                                              # Linebot.models.responses.Content object

    # 照片儲存名稱
    fileName = event.message.id + '.jpg'

    # 儲存照片
    with open('./image/' + fileName, 'wb')as f:
        for chunk in Img_message_content.iter_content(): # 用迴圈將linebot.models取出
            f.write(chunk)


    # DetectionResult 圖片辨認出的食譜文字
    DetectionResult = '胡蘿蔔' # 測試用(正式上線請註解)

    if DetectionResult in IngredientsList:

        # import MyPackage
        import Carousel_template
        import Match

        # 連線資料庫，將使用者搜尋的食材相關食譜抓出，在依照使用者喜好的風格做比對推薦
        recommend = Match.Recipe_Match(secretFile, user_id, DetectionResult)

        # 設定回傳訊息的物件
        message = Carousel_template.CarouselTemplate_icook(recommend)
        # # linebot回傳訊息
        line_bot_api.reply_message(event.reply_token, message)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='''很抱歉!無法搜尋您的資料''')
        )


# 開始運作Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) # 0.0.0.0 全部人都可以進入 port預設為5000
