#import pandas as pd
import subprocess

def PictureDetection():

    # 執行圖像辨認
    commandString = './darknet detector test data/obj.data yolov4-tiny-custom.cfg backup/yolov4-tiny-custom_best.weights Datasets/image/image.jpg -dont_show'
    commandList = commandString.split(" ")  
    #['./darknet','detector','test', 'data/obj.data', 'yolov4-tiny-custom.cfg', 'backup/yolov4-tiny-custom_best.weights', 'Datasets/image/image.jpg', '-dont_show'] 
    
    result = subprocess.check_output(commandList, shell=False)  # 透過子程序去執行
    
    output = result.decode('utf-8') # 輸出為2進制，將其編碼
    
    # 找出辨認後結果在字串的位置，並處理特殊符號
    output = output[(output.find('milli-seconds.') + 14):]  # 字串'milli-seconds.'後為辨識的結果
    final_output = sorted(
                    [(x.split(':')[0], x.split(':')[1]) for x in output.split('\n') if x],
                    key = lambda s: int(s[1].strip('%')), 
                    reverse = True)
    # final_output 所輸出的程序
    # 先將output結果用換行符號"\n"轉成List，並去除list內為空字串的元素 => ex.['Tomato: 92%', 'Carrot: 28%']
    # 將List內每個元素分割成touple => ex. [('Tomato', ' 92%'), ('Carrot', ' 28%')]
    # 將List內個每個touple，按照百分比由高至低排序(要注意原本百分比是字串，所以用strip('%')先將百分比符號去除，再轉成int後進行排序)
    
    
    
    # 根據排序過後的結果，找出LIST內第一個touple內的第一個值(蔬果名稱)
    food_name = final_output[0][0]
    
    # 原本的做法是先轉成DataFrame再做比較
    #df = pd.DataFrame([[elem.split(':')[0], elem.split(':')[1]] for elem in output if elem])
    #df.columns = ['objectName', 'confidence']
    #food_name = df.stack().max()
    
    if food_name == 'Carrot':
        re_food = food_name.replace('Carrot', '紅蘿蔔')
    if food_name == 'Tomato':
        re_food = food_name.replace('Tomato', '番茄')
    if food_name == 'Cucumber':
        re_food = food_name.replace('Cucumber', '黃瓜')
    if food_name == 'Cheese':
        re_food = food_name.replace('Cheese', '起司')
    if food_name == 'Cabbage':
        re_food = food_name.replace('Cabbage', '甘藍')

    return re_food

if __name__ == "__main__":
    
    Result = PictureDetection()
    print(Result)