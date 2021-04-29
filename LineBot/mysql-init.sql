# 建立資料庫
CREATE SCHEMA  if not exists `linebot`;

# 建立使用者帳號資訊的資料表
CREATE TABLE if not exists `linebot`.`UserInformation` (
  `UserID` varchar(35) NOT NULL ,
  `UserName` TEXT NOT NULL,
  `Email` TEXT NOT NULL,
  `time` DATETIME NULL,
  CONSTRAINT UserInformation_UserID_PK PRIMARY KEY (UserID)
  )
COMMENT = '使用者帳號資訊表';


# 建立儲存使用者喜好食譜的資料表
CREATE TABLE if not exists `linebot`.`Userfavorite` (
  `id` INT NOT NULL AUTO_INCREMENT, 
  `UserID` varchar(35) NOT NULL,
  `Time` DATETIME NULL,
  `Favorite` TEXT NULL COMMENT '使用者喜好紀錄',
  PRIMARY KEY (`id`) 
  )
COMMENT = '使用者搜尋資料表';


