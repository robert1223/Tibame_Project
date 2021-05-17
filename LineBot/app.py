# 載入相關套件
from flask import Flask, request, abort, send_file, render_template
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
import pymysql
import configparser
from confluent_kafka import Producer


from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *


# 讀取Linebot、mysql、kafka連線資訊
CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

# 建立Flask
app = Flask(__name__, static_folder='./static', static_url_path='/static')

# 讀取LineBot驗證資訊
# line_bot_api = LineBotApi(secretFile['channelAccessToken'])
# handler = WebhookHandler(secretFile['channelSecret'])
line_bot_api = LineBotApi(CONFIG['LINE_BOT']['ACCESS_TOKEN'])
handler = WebhookHandler(CONFIG['LINE_BOT']['SECRET'])

# 建立Producer
KafkaProducer = Producer({"bootstrap.servers": CONFIG["KAFKA"]["HOST"]})


# 讀取資料庫中食材名稱，放入List，用來比對使用者傳入食材名稱
conn = pymysql.connect(
            host=CONFIG['MYSQL']['HOST'],  # 連線主機名稱
            port=int(CONFIG['MYSQL']['PORT']),  # 連線主機port號
            user=CONFIG['MYSQL']['USER'],  # 登入帳號
            password=CONFIG['MYSQL']['PASSWD'])  # 登入密碼
cursor = conn.cursor()
query = 'SELECT Ingredient FROM ceb102_project.Ingredient_CodeName;'
cursor.execute(query)
Ingredients = cursor.fetchall()
conn.close()

# 抓出來的資料每一筆都是tuple，將其轉成字串放入list
IngredientsList = []
for Ingredient in Ingredients:
    IngredientsList.append(Ingredient[0])

# 建立使用者會員資料的dict
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

    # 使用者進入加入會員的網站後，會把linebot上的的useID當作參數一起帶入，我們將參數取出作為會員資料庫的KEY值
    if request.method == 'GET':
        userID = request.args.get('userID')
        dict['UserID'] = userID

    #  使用者填完資料後，將裡面所填寫的資料抓出，與上面所抓的userid值一併放在dict裡，轉成df後再存入資料庫
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
        df = pd.DataFrame([dict])

        # 建立資料庫連線引擎並將資料存入MYSQL
        connect = create_engine('mysql+pymysql://{}:{}@18.183.16.220:3306/linebot?charset=utf8mb4'
                                .format(CONFIG['MYSQL']['USER'], CONFIG['MYSQL']['PASSWD']))
        df.to_sql(name='UserInformation', con=connect, if_exists='append', index=False)

        return render_template("thank.html")
    return render_template("questionnaire.html")

# Linebot接收訊息驗證
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
    ThemeDict = {"增肌減脂": 0, "美白": 1, "提神醒腦": 2, "終結疲勞": 3, "護眼營養": 4}

    if event.message.text == '小幫手':

        # linebot回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='''歡迎使用小幫手功能:
        \n若想利用食材來搜尋食譜，可以透過\n🍴傳送食材照片\n或是\n🍴輸入食材關鍵字\n來搜尋(ex.雞肉)
        \n另外還可以按\n🍴主題推薦\n我們將推薦各類型的主題食譜給您喔!''')
        )

    elif event.message.text == '會員專區':

        # Linebot回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='https://bf14084716cc.ngrok.io/apply?userID={}'.format(user_id))  # ngrok
        )

    elif event.message.text == '主題推薦':

        message = ImagemapSendMessage(
            base_url="https://i.imgur.com/DQYAc6A.jpg",
            alt_text="主題推薦",
            base_size=BaseSize(height=1177, width=2000),
            actions=[
                MessageImagemapAction(
                    text='增肌減脂',
                    area=ImagemapArea(x=150, y=160, width=400, height=420)
                    ),
                MessageImagemapAction(
                    text='美白',
                    area=ImagemapArea(x=840, y=160, width=400, height=420)
                    ),
                MessageImagemapAction(
                    text='提神醒腦',
                    area=ImagemapArea(x=1480, y=160, width=400, height=420)
                    ),
                MessageImagemapAction(
                    text='終結疲勞',
                    area=ImagemapArea(x=500, y=620, width=400, height=420)
                    ),
                MessageImagemapAction(
                    text='護眼營養',
                    area=ImagemapArea(x=1200, y=620, width=400, height=420)
                    )
                ]
            )

        # Linebot回傳訊息
        line_bot_api.reply_message(event.reply_token, message)


    # 判斷是否符合主題文字(增肌減脂、美白保養.....等)
    elif event.message.text in ThemeDict.keys():

        # Mypackage
        import Carousel_template

        # 連線資料庫，將資料抓出
        conn = pymysql.connect(
            host=CONFIG['MYSQL']['HOST'],  # 連線主機名稱
            port=int(CONFIG['MYSQL']['PORT']),  # 連線主機port號
            user=CONFIG['MYSQL']['USER'],  # 登入帳號
            password=CONFIG['MYSQL']['PASSWD'])  # 登入密碼
        cursor = conn.cursor()
        query = '''
        select a.Recipeid, a.RecipeName, a.`group`, b.IMGURL from
        ceb102_project.Recipe_Groups as a 
        left join ceb102_project.Recipes_IMGURL as b on a.Recipeid = b.Recipeid 
        where `group` = {};
        '''.format(ThemeDict[event.message.text])
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
        import Kafka_Consumer_Result

        # 將使用者搜尋的食材傳送至Kafka
        KafkaProducer.produce(CONFIG["KAFKA"]["TOPIC_1"], key=user_id, value=event.message.text)

        # 將使用者資料Consum下來做運算
        recommend = Kafka_Consumer_Result.Kafka_Consumer_Result(CONFIG)
        # print(recommend)
        # # 連線資料庫，將使用者搜尋的食材相關食譜抓出，在依照使用者喜好的風格做比對推薦
        # recommend = Match.Recipe_Match(CONFIG, user_id, Ingredient)
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

    # 使用者按下"我喜歡"的PostbackTemplateAction後，裡面會有記錄該筆食譜的ID(data)
    user_data = event.postback.data

    # 將使用者對食譜的喜好傳送至Kafka
    KafkaProducer.produce(CONFIG["KAFKA"]["TOPIC_2"], key=user_id, value=user_data)


# linebot處理照片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):

    # 使用者ID
    user_id = event.source.user_id

    # 使用者傳送的照片
    Img_message_content = line_bot_api.get_message_content(event.message.id)  # type :
                                                                              # Linebot.models.responses.Content object

    # 照片儲存路徑
    fileName = './Datasets/image/image.jpg'

    # 儲存照片
    with open(fileName + fileName, 'wb')as f:
        for chunk in Img_message_content.iter_content(): # 用迴圈將linebot.models取出
            f.write(chunk)

    # import MyPackage
    import Picture_Dectection
    DetectionResult = Picture_Dectection.PictureDetection()  # 辨認使用者傳送的食材


    # # DetectionResult 圖片辨認出的食譜文字
    # DetectionResult = '胡蘿蔔' # 測試用(正式上線請註解)

    if DetectionResult in IngredientsList:

        # import MyPackage
        import Carousel_template
        import Match

        # 連線資料庫，將使用者搜尋的食材相關食譜抓出，在依照使用者喜好的風格做比對推薦
        recommend = Match.Recipe_Match(CONFIG, user_id, DetectionResult)

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
