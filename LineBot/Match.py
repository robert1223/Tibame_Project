import pymysql
import json
import pandas as pd

def Recipe_Match(CONFIG, user_id, ingrendint):

    # 連線資料庫，將資料抓出
    conn = pymysql.connect(
        host=CONFIG['MYSQL']['HOST'],  # 連線主機名稱
        port=int(CONFIG['MYSQL']['PORT']),  # 連線主機port號
        user=CONFIG['MYSQL']['USER'],  # 登入帳號
        password=CONFIG['MYSQL']['PASSWD'])  # 登入密碼
    cursor = conn.cursor()

    # 建立相關食材的搜尋的query
    Recipe_query = '''
    select a.Recipeid, a.RecipeName, d.SubCategoryID from 
    ceb102_project.Recipes as a
    left join ceb102_project.Ingredient_CodeName as b on a.ingredient = b.Ingredient     
    left join ceb102_project.RecipeForRecommendation as c on a.Recipeid = c.Recipeid    
    left join ceb102_project.Recipe_SubCategory as d on a.RecipeID = d.RecipeID
    where b.樣品編號 = 
    (Select `樣品編號` from ceb102_project.Ingredient_icook where Ingredient = '{}') 
    group by a.Recipeid, a.RecipeName, d.SubCategoryID
    order by max(c.Total) desc;
    '''.format(ingrendint)  # 將相關"食材"的食譜在MySQL先進行query
    cursor.execute(Recipe_query)
    RecipesInformation = cursor.fetchall()

    # 建立使用者喜好的query
    user_query = '''
        SELECT UserID, style from linebot.UserInformation  
        where UserID = '{}';
        '''.format(user_id)
    cursor.execute(user_query)
    userinformation = cursor.fetchall()
    conn.close()

    # 將MySQL 抓回的食譜資料及使用者喜好資料，使用DataFrame做篩選比對
    Recipe_df = pd.DataFrame(RecipesInformation, columns=['RecipeID', 'RecipeName', 'SubCategory'])
    filterLsit = eval(userinformation[0][1])
    df_filter = Recipe_df[Recipe_df['SubCategory'].isin(filterLsit)]

    if len(df_filter) == 0:
        recommend = Recipe_df.to_records(index=False)[:5]                 # 若使用者沒有特別喜好，不使用喜好做篩選
    else:
        df_filter = Recipe_df[Recipe_df['SubCategory'].isin(filterLsit)]  # 將風格喜好加入篩選條件
        if len(df_filter) < 5:                                            # 若比數小於5比，按照風格喜好推薦後，另外加入非風格喜好的食譜(湊滿5個)
            recommend = df_filter.to_records(index=False)                 # 喜好風格食譜
            df_second = Recipe_df[~Recipe_df['RecipeID'].isin(df_filter['RecipeID'])]  # 非風格喜好食譜
            recommend_add = df_second.to_records(index=False)[:5 - len(df_filter)]     # 取的數量根據喜好風格的數量，剩餘湊滿五個
            recommend.extend(recommend_add)
        else:
            recommend = df_filter.to_records(index=False)[:5]             # 喜好風格食譜超過5個，直接選取前五個推薦
        recommend = recommend.tolist()        # to_records 會將dataframe 轉成np.array物件 要用tolist() 轉成list

    return recommend

if __name__ == "__main__":

    # 讀取mysql連線資訊
    secretFile = json.load(open('./secretFile.txt', 'r'))
    user_id = 'Ue5fb50f1e370cd5c0ff2cacc6515dada'
    ingrendint = '起司'
    result = Recipe_Match(secretFile, user_id, ingrendint)
    print(result)
