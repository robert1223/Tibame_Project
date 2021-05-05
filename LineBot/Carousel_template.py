
from linebot.models import CarouselTemplate, CarouselColumn, URITemplateAction, PostbackTemplateAction ,TemplateSendMessage
def CarouselTemplate_icook(RecipesInformation): # 旋轉木馬訊息設置

    CarouselTemplateList = []
    for EachInformation in RecipesInformation:
        col = CarouselColumn(
            # 測試用(正式上線請註解)
            thumbnail_image_url='https://tokyo-kitchen.icook.network/uploads/recipe/cover/257813/286e59025c452a90.jpg',
            # request 自己用Flask架設的 Web server內的圖片位置
            # thumbnail_image_url='https://cf3f3b7280ce.ngrok.io/picture?RecipeID={}'.format(RecipesInformation[0]),
            title=EachInformation[1],
            text='推薦適合您的食譜!',
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