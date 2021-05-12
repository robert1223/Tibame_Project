import requests
from bs4 import BeautifulSoup
import time
import os
import json

from pymongo import MongoClient

# 讀取MongoDB連線資訊
MongoDBInformation = json.load(open('./MongoDB_Information.txt', 'r'))

# 建立MongoDB數據庫連接 IP='10.1.16.67', port=27017
uri = 'mongodb://{}:{}@18.183.16.220:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false'\
    .format(MongoDBInformation['host'],MongoDBInformation['passwd'])
client = MongoClient(uri)
db = client['Recipe_OriginData']
collection = db['cookpad']

# ----建立爬蟲用的header----
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
headers = {
    'user-agent': UserAgent,
    'upgrade-insecure-requests': '1',
    'cookie': 'ab_session=0.0859812173151494; f_unique_id=53681aaa-c678-4bc1-912b-684e6e652494; _ga=GA1.2.1824671364.1615515506; _pxvid=38ec0c80-82d9-11eb-acb4-23d8e2d5314f; _pxhd=d5aab9548783d6dd8ab3acda50d4a181e6ab79b7f42bb0008573cf5cf201ebe9:38ec0c80-82d9-11eb-acb4-23d8e2d5314f; keyword_history_zh-TW=%5B%22%E9%9B%9E%E8%82%89%22%2C%22%E5%85%8D%E7%83%A4%E8%9B%8B%E7%B3%95%22%2C%22%E8%9B%8B%E7%B3%95%22%2C%22%E5%81%A5%E5%BA%B7%22%5D; _gid=GA1.2.2092251865.1616755165; seen_bookmark_reminder=true; recipe_view_count_zh-TW=3; access_token_global=eyJfcmFpbHMiOnsibWVzc2FnZSI6IkltSTJOek5qTm1ZMVpHWTRNMk16WWpBNFlqYzFNamhqTmpRelpqUXpOMlk1TVdGbE1ERmxZemd4WlRJMk1XRXhaV1EwWVRJeE5qSmhNamRsWkdGaE9EY2kiLCJleHAiOm51bGwsInB1ciI6ImNvb2tpZS5hY2Nlc3NfdG9rZW5fZ2xvYmFsIn19--4ac12450abd6490759238bff828bff739fdaf73a; _gat=1; _gat_sampledTracker=1; _px2=eyJ1IjoiMTBjYWQ1NjAtOGUyMy0xMWViLThkODQtN2I0YWQzMGQ1YWY5IiwidiI6IjM4ZWMwYzgwLTgyZDktMTFlYi1hY2I0LTIzZDhlMmQ1MzE0ZiIsInQiOjE2MTY3NTY5ODQ3MTYsImgiOiIxMjgwMzQ4ZDJkYzA3OTQwNGIwMDE2MDU4NGZkZTdjY2YwZDJmNTBhNTMzZDMxNWI4ODM3MTRkOTg0MWExZDQ0In0=; _global_web_session=Og79S2xXQA9AtZJJIXDv%2FW%2FCkiuDGSFzHf0FZ393GB3tUZyeElLD4lDkALAz14Pd4oB4Ha1XRXDDrYgmtp7ND4nkNibYK4rOkUox%2F2JI71GmWtYgNMU0sbxSyKK5unAhwE6f%2FhoaQvrShi6zI8B6OybTBeOKDQrMS%2FhWkC6HEuFHZpafwibe0wwChrDbo8nfjk2WaUZXVBXUb55xl4ZCoqfqEKkotY2TxuI%2FXBmdAHaHtA8ifDOJDM%2F1TCfFzWrFMVkdQyGs%2FuwnlSVa2%2FXkSTc%2BQE5vJdBEHbSM--cKOV%2Fnsha1N1AZvB--Sq9sL%2FcIrbt7nuBWSp5oEw%3D%3D'
}

# ----對分類網站進行requests----
url = 'https://cookpad.com/tw/search_categories'
res = requests.get(url=url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# ---將子類別名稱及網址做成dict放在list方便用回圈依序爬蟲----
SubCategories = [{x.text.replace(' ', '').replace('\n', ''): 'https://cookpad.com' + x['href']}
                 for x in soup.select('div[class="flex flex-wrap links"] > div > a')]

for SubCategory in SubCategories:
    SubCategoryName = list(SubCategory.keys())[0]
    SubCategoryURL = list(SubCategory.values())[0]
    page = 1

    # ----依類別建立儲存圖片的資料夾---
    Img_Dir_Path = './cookpad_img/SubCategory_' + SubCategoryName
    if not os.path.exists(Img_Dir_Path):
        os.makedirs(Img_Dir_Path)

    # ----建立儲存JsonFile的資料夾----
    JsonFile_Dir_Path = './cookpad_jsonfile/SubCategory_' + SubCategoryName
    if not os.path.exists(JsonFile_Dir_Path):
        os.makedirs(JsonFile_Dir_Path)

    # ----建立存放各食譜資訊的LIST----
    RecipesList = list()
    while True:
        try:
            # ---- 對類別網頁進行 requests----
            SubCategoryRes = requests.get(url=SubCategoryURL + '?page={}'.format(page), headers=headers)
            # print(SubCategoryRes)
            SubCategorySoup = BeautifulSoup(SubCategoryRes.text, 'html.parser')
            TotalRecipes = SubCategorySoup.select('li[class="flex flex-col p-rg md:px-0 text-cookpad-14 md:text-cookpad-16 ranked-list__item bg-cookpad-white md:bg-white-transparent"]')
            TmpList = list()

            # ----對食譜網頁進行requests----
            for Recipe in TotalRecipes:
                RecipeURL = 'https://cookpad.com' + Recipe.select('a[class="media"]')[0]['href']
                RecipeRes = requests.get(url=RecipeURL, headers=headers)
                RecipeSoup = BeautifulSoup(RecipeRes.text, 'html.parser')

                try:
                    # ----食譜名稱及敘述----
                    RecipeName = RecipeSoup.select('section[class="intro-container document-section"] > h1')[0].text\
                        .replace('\n', '').strip().replace('/', '_')
                    Description = RecipeSoup.select('div[data-collapse-target="content"]')[0].text.replace('\n', '').strip()

                    # ---- 把食譜圖片抓下 ----
                    RecipeImgURL = RecipeSoup.select('div[class="tofu_image"] > picture > img')[0]['src']
                    Img_conetent = requests.get(RecipeImgURL, headers).content
                    if not os.path.exists(Img_Dir_Path + '/' + RecipeImgURL.split('/')[-1]):
                        with open(Img_Dir_Path + '/' + RecipeImgURL.split('/')[-1], 'wb') as f:
                            f.write(Img_conetent)

                    # ----作者及ID----
                    AuthorID = RecipeSoup.select('div[class="media my-sm"]')[0]['data-hidden-from'].replace('\n', '').strip()
                    AuthorName = RecipeSoup.select('div[class="media my-sm"] > a > span > span')[0].text.replace('\n', '').strip()

                    # ----料理時間及份數----
                    # 判斷是否有給料理時間
                    if len(RecipeSoup.select('div > span > span[class="mise-icon-text"]')) == 0:
                        CookTime = None
                    else:
                        CookTime = RecipeSoup.select('div > span > span[class="mise-icon-text"]')[0].text
                    # 判斷是否有給份數
                    if len(RecipeSoup.select('div[class="text-cookpad-gray-600 mt-sm"] > span')) == 0:
                        Servings = None
                    else:
                        Servings = RecipeSoup.select('div[class="text-cookpad-gray-600 mt-sm"] > span')[0].text

                    # ----食材名稱及數量----
                    Ingredient = [x.text.replace('\n', '').strip() for x in
                                      RecipeSoup.select('div[itemprop="ingredients"]')]  # 目前暫時找不到方法利用爬蟲將食材與數量分開

                    # ----料理方法----
                    CookingSteps = ['{}. '.format(n + 1) + x.text for n, x in enumerate(RecipeSoup.select('p[class="mb-sm inline"]'))]

                    # ----發文日期----
                    Datetime = RecipeSoup.select('div[class="py-xs"] > time')[0].text

                    # ----將食譜資訊彙整成一個dictionary----
                    RecipeInformation = {
                        'SubCategoryName': SubCategoryName,  # 子類別名稱
                        'RecipeName': RecipeName,  # 食譜名稱
                        'Description': Description,  # 食譜說明
                        'AuthorID': AuthorID,  # 作者ID
                        'Author': AuthorName,  # 作者名稱
                        'Servings': Servings,  # 份量
                        'CookingTime': CookTime,  # 烹飪時間
                        'Ingredient': Ingredient,  # 所需食材及各食材份量
                        'CookingSteps': CookingSteps,  # 烹飪方法
                        'Datetime': Datetime,  # 發文日期
                        'URL': RecipeURL,  # 食譜網址
                        'ImgURL': RecipeImgURL # 食譜照片網址
                    }

                    # ----將每頁食譜資訊暫存在list中----
                    TmpList.append(RecipeInformation)
                except IndexError:
                    print(IndexError)
                    pass
                time.sleep(3)

            print('now page: {}'.format(page))
            RecipesList.extend(TmpList)

            # ----爬取每三頁的食譜資訊後將資料丟到MongoDB及存成jsonfile----
            if page % 3 == 0:
                try:
                    result = collection.insert_many(RecipesList)
                    print('file save to MongoDB:', result)
                    with open('./cookpad_jsonfile/SubCategory_{}/page_{}To{}.txt'.format(SubCategoryName, page-2, page), 'w') as jsonfile:
                        json.dump(RecipesList, jsonfile)
                    print('file save done')
                except TypeError:  # 有時候爬到最後幾頁會出現可能都是廣告html與正常食譜網頁不同，會出現都是空字串的list，在匯入Mongodb會出現TypeError，
                    pass           # 若出現該情況則用TryException將例外排除
                RecipesList.clear()  # 檔案存檔後將 RecipesList清空，避免重複存檔
            if len(TotalRecipes) < 20:  # 每個分類每頁最多20筆食譜，少於20代表是最後一頁
                break
            page += 1
        except ConnectionRefusedError:
            time.sleep(300)

    print('final page: {}'.format(page))

    # ----在最後一頁做判斷，如果頁數不能被3整除，則資料在上述程式不會被保存，跳出While迴圈後再進行儲存----
    if page % 3 != 0:
        try:
            result = collection.insert_many(RecipesList)
            with open('./cookpad_jsonfile/SubCategory_{}/page_{}To{}.txt'.format(SubCategoryName, (page - (page % 3) + 1), page),'w') as jsonfile:
                json.dump(RecipesList, jsonfile)
            print('file save done')
        except TypeError:
            pass