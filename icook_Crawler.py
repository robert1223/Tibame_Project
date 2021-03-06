# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import os
import json
import random
from pymongo import MongoClient

# 讀取MongoDB連線資訊
MongoDBInformation = json.load(open('./MongoDB_Information.txt', 'r'))

# 建立MongoDB數據庫連接 IP='10.1.16.67', port=27017
uri = 'mongodb://{}:{}@18.183.16.220:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false'\
    .format(MongoDBInformation['host'],MongoDBInformation['passwd'])
client = MongoClient(uri)
db = client['Recipe_OriginData']
collection = db['icook']

# ----建立爬蟲用的header----
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
headers = {
    'user-agent': UserAgent,
    'Upgrade-Insecure-Requests': '1'
}
url = 'https://icook.tw/categories'
res = requests.get(url=url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')



for EachCategoryHtml in soup.select('li[class="categories-all-parents"]')[1:-1]:  # "影音專區" 跟 "寵物美食" 不爬
    CategoryName = EachCategoryHtml.select('h3')[0].text.replace('\n', '').strip()  # 主類別名稱(沒有網址連結)
    # ---- 把子分類的代號(ID)及名稱用dict表示並放入list ---- ex. {'104': 烤肉}
    SubCategories = [{x['href'].split('/')[2]: x.text.replace('\n', '')}
                     for x in EachCategoryHtml.select('ul > li > a[class="categories-all-child-link"]')]
    for SubCategory in SubCategories:
        SubCategoryID = list(SubCategory.keys())[0]
        SubCategoryName = list(SubCategory.values())[0]
        page = 1
        # ----建立儲存圖片的資料夾----
        Img_Dir_Path = './icook_img/SubCategory_' + SubCategoryID
        if not os.path.exists(Img_Dir_Path):
            os.makedirs(Img_Dir_Path)
        # ----建立儲存JsonFile的資料夾----
        JsonFile_Dir_Path = './icook_jsonfile/SubCategory_' + SubCategoryID
        if not os.path.exists(JsonFile_Dir_Path):
            os.makedirs(JsonFile_Dir_Path)
        # ----建立存放各食譜資訊的LIST----
        RecipesList = list()
        while True:
            try:
                # ----對各分類網站進行爬蟲----
                SubCategoryUrl = 'https://icook.tw/categories/{}?page={}'.format(SubCategoryID, page)
                SubCategoryRes = requests.get(url=SubCategoryUrl, headers=headers)
                SubCategorySoup = BeautifulSoup(SubCategoryRes.text, 'html.parser')
                Total_Recipes = SubCategorySoup.select('li[class="browse-recipe-item"]')
                # print(Total_Recipes)
                TmpList = list()
                for recipe in Total_Recipes:
                    RecipeName = recipe.select('h2[class="browse-recipe-name"]')[0].text.replace(' ', '').replace('\n', '')  # 標題名稱
                    content_url = 'https://icook.tw' + recipe.select('a')[0]['href']   # 內容網址
                    RecipeID = recipe.select('a > article')[0]['data-recipe-id']  # 食譜ID

                    # ----測試之後發現"食譜內容"的網址會擋爬蟲，需要代token才能進行拜訪----
                    token = soup.select('meta[name="csrf-token"]')[0]['content']   # 在分類網站時抓出token，再利用token去擺訪每個食譜網站
                    data = {
                        'content': token
                    }

                    # ---- 對每篇食譜進行爬蟲----
                    content_res = requests.get(content_url, headers=headers, data=data)    # 食譜內容爬蟲
                    content_soup = BeautifulSoup(content_res.text, 'html.parser')


                    # ---- 依文章的讚數來決定是否進行爬蟲 ----(暫時不使用)
                    try:
                        LikeStat = content_soup.select('span[class="stat-content"]')[0].text
                    except IndexError:  # 若新發佈的食譜還沒有按讚數，則會出現空的list
                        LikeStat = 0


                    # ---- 部份爬蟲會爬到廣告資料沒有內文，使用TryException處理----(如果內容不齊全直接pass掉不爬取)
                    try:
                        # ---- 把食譜圖片抓下 ----
                        RecipeImgURL = content_soup.select('a[data-gallery="recipe-imgs"]')[0]['href']
                        Img_conetent = requests.get(RecipeImgURL, headers).content
                        if not os.path.exists(Img_Dir_Path + '/' + RecipeID + '.jpg'):
                            with open(Img_Dir_Path + '/' + RecipeID + '.jpg', 'wb') as f:
                                f.write(Img_conetent)
                        # ----食譜說明----
                        Description = content_soup.select('section[class="description"] > p')[0].text
                        # Description = content_soup.select('div[class="description"] > p')[0].text # (舊版)

                        # ----作者ID及名稱----
                        Author = content_soup.select('div[class="author-name"] > a')[0].text
                        AuthorID = content_soup.select('div[class="author-name"] > a')[0]['href'].split('/')[-1]

                        # ----食材名稱及數量----
                        IngredientName = [x.text.replace('.', '、')
                                          for x in content_soup.select('div[class="ingredients-groups"]')[0].select('a[class="ingredient-search"]')]  # 名稱
                        IngredientUnit = [y.text
                                          for y in content_soup.select('div[class="ingredients-groups"]')[0].select('div[class="ingredient-unit"]')]  # 數量
                        IngredientDict = dict(zip(IngredientName, IngredientUnit))  # 合併成字典

                        # ---料理方法---
                        CookingSteps = ['{}. '.format(n+1) + x.text
                                        for n, x in enumerate(content_soup.select('li > figure > figcaption > p'))]  # 按tag依序找出
                        # ----份量及烹飪時間----
                        Servings = content_soup.select('div[class="servings-info info-block"] > div[class="info-content"]')[0].text.replace('\n', '')
                        CookingTime = content_soup.select('div[class="time-info info-block"] > div[class="info-content"]')[0].text.replace('\n', '')

                        # ----發文日期----
                        Datetime = content_soup.select('div[class="recipe-detail-metas"] > time')[0]['datetime']

                        # ----瀏覽人數----
                        try:
                            Preview = content_soup.select('div[class="recipe-detail-meta-item"]')[0].text.replace('\n', '').strip()
                        except IndexError:
                            Preview = 0

                        # ----將食譜資訊彙整成一個dictionary----
                        RecipeInformation = {
                            'RecipeID': RecipeID,  # 食譜ID
                            'CategoryName': CategoryName,  # 主類別名稱
                            'SubCategoryID': SubCategoryID,  # 子類別ID
                            'SubCategoryName': SubCategoryName,  # 子類別名稱
                            'RecipeName': RecipeName,  # 食譜名稱
                            'Description': Description,  # 食譜說明
                            'AuthorID': AuthorID, # 作者ID
                            'Author': Author,  # 作者名稱
                            'Servings': Servings,  # 份量
                            'CookingTime': CookingTime,  # 烹飪時間
                            'Ingredient': IngredientDict,  # 所需食材及各食材份量
                            'CookingSteps': CookingSteps,  # 烹飪方法
                            'LikeStat': LikeStat,  # 按讚數
                            'Datetime': Datetime,  # 發文日期
                            'Preview': Preview,  # 瀏覽人數
                            'URL': content_url,  # 食譜網址
                            'ImgURL': RecipeImgURL # 食譜圖片網址
                        }
                        # ----將食譜資訊包在list中----
                        TmpList.append(RecipeInformation)
                    except IndexError as e:
                        print(e)
                        pass
                    time.sleep(random.randint(3, 5))
                print('now page: {}'.format(page))

                # 將每頁所爬的資料儲存於RecipesList
                RecipesList.extend(TmpList)
                # ----爬取每三頁的食譜資訊後將資料存成jsonfile----
                if page % 3 == 0:
                    try:
                        result = collection.insert_many(RecipesList)
                        print('file save to MongoDB:', result)
                        with open('./icook_jsonfile/SubCategory_{}/page_{}To{}.json'.format(SubCategoryID, page-2, page), 'w') as jsonfile:
                            json.dump(RecipesList, jsonfile)
                        print('file save done')
                    except TypeError:  # 有時候爬到最後幾頁會出現可能都是廣告html與正常食譜網頁不同，會出現都是空字串的list，在匯入Mongodb會出現TypeError，
                        pass           # 若出現該情況則用TryException將例外排除
                    RecipesList.clear()  # 檔案存檔後將 RecipesList清空，避免重複存檔
                if len(Total_Recipes) < 18:  # 每個分類每頁最多18筆食譜，少於18代表是最後一頁
                    break
                page += 1

            except ConnectionRefusedError as C:  # 若爬蟲被擋，讓爬蟲程式先休息5分鐘再試試
                print(C)
                time.sleep(300)

        print('final page: {}'.format(page))

        # ----在最後一頁做判斷，如果頁數不能被3整除，則資料在上述程式不會被保存，跳出While迴圈後再進行儲存----
        if page % 3 != 0:
            try:  # 若爬取的最後一頁完全無食譜，則RecipesList為空字串，無法再Mongodb進行存取
                result = collection.insert_many(RecipesList)
                print(result)
                with open('./icook_jsonfile/SubCategory_{}/page_{}To{}.txt'.format(SubCategoryID, (page-(page % 3)+1), page), 'w') as jsonfile:
                    json.dump(RecipesList, jsonfile)
            except TypeError:
                pass