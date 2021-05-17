from linebot.models import (
    CarouselTemplate,
    CarouselColumn,
    URITemplateAction,
    PostbackTemplateAction,
    TemplateSendMessage
)

# 旋轉木馬訊息設置
def CarouselTemplate_icook(RecipesInformation):
    CarouselTemplateList = []
    for EachInformation in RecipesInformation:
        col = CarouselColumn(
            # 測試用(正式上線請註解)
            thumbnail_image_url=EachInformation[3],
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
                    label='很普通🥱',
                    data=str(EachInformation[0]) + '_1'
                    ),
                PostbackTemplateAction(
                    label='我很喜歡❤️',
                    data=str(EachInformation[0]) + '_5'
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
