import pandas as pd
import subprocess

def PictureDetection():
    # 執行圖像辨認
    commands = 'darknet.exe detector test data/obj.data yolov4-tiny-custom.cfg backup/yolov4-tiny-custom_best.weights Datasets/image/image.jpg -dont_show'

    result = subprocess.check_output(commands, shell=False)
    output = result.decode('big5')
    output = output[(output.find('milli-seconds') + 13):]
    output = output.replace('\r\n', '').replace('.', '')
    output = output.split('%')

    df = pd.DataFrame([[elem.split(':')[0], elem.split(':')[1]] for elem in output if elem])
    df.columns = ['objectName', 'confidence']
    food_name = df.stack().max()
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