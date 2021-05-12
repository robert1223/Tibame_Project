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
