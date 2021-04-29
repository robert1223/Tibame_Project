
from linebot.models import *
def CarouselTemplate_icook(RecipesInformation): # 旋轉木馬訊息設置

    CarouselTemplateList = []
    for EachInformation in RecipesInformation:
        col = CarouselColumn(
            thumbnail_image_url='https://2de75e59a1bd.ngrok.io/static/{}.jpg'.format(EachInformation[0]), # 需連接HDFS內的圖片位置 這裡只是做示範
            title=EachInformation[1],
            text=' ',
            actions=[
                URITemplateAction(
                    label='前往觀看',
                    uri='https://icook.tw/recipes/{}'.format(EachInformation[0])
                    ),
                PostbackTemplateAction(
                    label='我喜歡❤️',
                    text=' ',
                    data=EachInformation[0]
                    )
                ]
            )
        CarouselTemplateList.append(col)

    # 建立 Carousel Template(Message types)
    CarouseltemplateMessage = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(columns=CarouselTemplateList)
        )
    return CarouseltemplateMessage