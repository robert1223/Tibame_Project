from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.ml import PipelineModel



def Recipe_Recommend(userid):

	# 將Pipline model load進來
	model = PipelineModel.load("hdfs://devenv/user/spark/ceb102_project/icook_ALS_Model_AutoTraining/")
	
	#從HDFS 將使用者id及轉換成的index對應表抓出來
	UserID_toIndex = spark.read.csv("hdfs://devenv/user/spark/ceb102_project/UserID_toIndex/",
									header=True,
                           			schema="UserID string, UserID_Index float")


	# 將ALS模型抓出並根據各使用者喜好找出食譜分數作為推薦
	ALS_Model = model.stages[-1]
	user_SubCategory = ALS_Model.recommendForAllUsers(5)

	# 將表合併(因為推薦的表user_SubCategory只有代號沒有ID,要將有id及代號的表一起合併)
	Recommend_Information = UserID_toIndex.join(user_SubCategory, "UserID_Index","left")\
	.select("UserID","UserID_Index","recommendations")

	# 判斷要該使用者行為是否有參與模行訓練
	result = Recommend_Information.where(Recommend_Information.UserID == userid).toPandas()
	if len(result) == 0:
		final_result = []

		return finals_result
	else: 
		final_result = [x['RecipeID'] for x in result['recommendations'].tolist()[0]]

		return final_result

if __name__ == '__main__':

	spark = SparkSession.builder.getOrCreate()
	userid = 'Ue5fb50f1e370cd5c0ff2cacc6515dada'
	recommendation = Recipe_Recommend(userid)
	print(recommendation)