# !/bin/sh
deldate=`date -d '1 day ago' +%Y-%m-%d`
hadoop fs -put /home/spark/Desktop/ceb102_project/user_preferences_logs_$deldate.csv \
	/user/spark/ceb102_project/uer_preferences/
rm /home/spark/Desktop/ceb102_project/user_preferences_logs_$deldate.csv
spark-submit --master spark://devenv:7077 /home/spark/Desktop/ceb102_project/ALS_Model_AutoTraining.py

