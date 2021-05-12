# Tibame_Project
![黑桃組專題海報](https://user-images.githubusercontent.com/78791996/117966160-30aaee80-b356-11eb-8fb3-155aab0977fd.png)

## 專案說明
執行本專案的目的主要是希望透過拍照食材及關鍵字搜尋的方式，推薦給使用者適合的食譜
- 使用者透過LineBot使用食譜推薦系統，功能包含
  - 使用者填入相關喜好
  - 拍照辨認食材，推薦該食材相關食譜
  - 透過食材關鍵字搜尋，推薦食譜
  - 推薦主題食譜

## 環境架設
- 使用Linux及Docker架設環境
- 建立MongoDB與MySQL用於儲存食譜資料
- 使用Kafka做為即時收集使用者數據的第一街口
- 使用Hadoop儲存使用者資訊

## 食譜網站爬蟲
- icook 網站爬蟲
- cookpad 網站爬蟲

可參考`icook_crawler.py`及`cookpad_crawler.py`

分別將兩個網站所爬下來的食譜資訊存在MongoDB及在本地端備份Jsonfile

## 資料清洗
僅將icook資料作完整清洗
- 針對食材(名稱、數量、單位)做清洗，目的是計算各食譜營養素，進行分群
  - 全形自轉半形字
  - 特殊符號處理
  - 漢字數字轉阿拉伯數字(使用ca2an套件)
  - 數字統一(ex 四分之一 => 1/4)
  
- 針對食譜敘述做清洗，目的是為了找出每篇食譜敘述內TFIDF前三高的詞
  -  刪除空值
  -  Jieba斷詞
  -  設定停用字



## 模型建立
- K-means
  - 透過食譜敘述TFIDF前三高的詞，將其向量化，再進行K-means分群
結論: 因為矩陣過於稀疏，分群並無顯著效果(誤差平方和SSE無法收斂)
 
- Spark-ALS
  - 模擬使用者對食譜的評分，做成推薦模型
  (註)實際上使用者對食譜的評分我們無法取得，所以使用Numpy模擬出50位使用者隨機對100個食譜進行0~5評分 

## LineBot
使用`linebot-sdk-python`API，並架設flask及啟用ngrok做為webhook
- app.py: 主要用來架設flask用來與linebot server進行驗證、處理使用者訊息
- Carousel_template.py: 回覆旋轉木馬訊息設定
- Match.py: 根據使用者喜好及食材從資料庫比對資料並回傳食譜
