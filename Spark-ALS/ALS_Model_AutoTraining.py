from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.ml import Pipeline	


# 建立SparkSession
spark = SparkSession.builder.getOrCreate()

# 讀取使用者喜好資訊
icook = spark.read.csv('hdfs://devenv/user/spark/ceb102_project/uer_preferences',
                header=True,
                schema="UserID string, RecipeID int, rating int, DateTime timestamp")


# 先根據DateTime依 新>舊 排序，再找出UserID與RecipeID同時重複的值並刪除（只保留最新的資料）
icook_final = icook.orderBy(f.col('DateTime').desc()).dropDuplicates(subset=['UserID', 'RecipeID'])

# 僅選取要訓練的欄位
data = icook_final.select("UserID","RecipeID","rating")

# 建立Pipline model
pipeline = Pipeline(stages = [
    StringIndexer(inputCol="UserID", outputCol="UserID_Index"),
    ALS(maxIter=20,userCol="UserID_Index",itemCol="RecipeID",ratingCol="rating" , coldStartStrategy="drop")
])

# 將要訓練的資料放進Pipline model
model = pipeline.fit(data)

# 將使用者資料使用StringIndex轉換的相關資訊存到hadoop-HDFS
UserID_toIndex = model.stages[0].transform(data).dropDuplicates(subset=['UserID'])\
					.select("UserID","UserID_Index")

UserID_toIndex.write.format('csv').option('header',True).mode('overwrite')\
					.option('sep',',').save("hdfs://devenv/user/spark/ceb102_project/UserID_toIndex/")

# 儲存並複寫pipline model
model.write().overwrite().save("hdfs://devenv/user/spark/ceb102_project/icook_ALS_Model_AutoTraining/")




	





