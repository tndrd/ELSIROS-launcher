import os
import time
from random import *
import json
from datetime import datetime


'''Создаем новый файл с параметрами вратаря и нападающего, для каждого отдельный файл в 
   отдельной директории и в момент создания нового - удаляем старые(все, что старше 2 секунд)
'''
#Добавить текущее направление робота и можно булевскую переменную о наличии препятствий!
def create_json(dir_path='Gk_sync',ball_coord=[],robot_coord=[],robot_current_state='',duty_direction =0):
    filename = os.path.join(dir_path,f'params_{datetime.now().microsecond}.json')

    json_str  = f'{{"ball_coord": {{"X": {ball_coord[0]}, "Y": {ball_coord[1]}}}, "robot_coord": {{"X": {robot_coord[0]}, "Y": {robot_coord[1]}}}, "robot_current_state": "{robot_current_state}", "duty_direction": {duty_direction}}}'

    json_obj = json.loads(json_str)
    
    with open(filename, 'w') as f:
        json.dump(json_obj, f, indent=0)
     # удаляем старые файлы
    for old_file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, old_file)
        try:
            if time.time() - os.path.getctime(file_path) > 20:
                os.remove(file_path)
        except FileNotFoundError:
            print("FileNotFoundError. При попытке удаления")
        except PermissionError:
            print("PermissionError. При попытке удаления")
        except Exception:
            print(f"[{Exception}]. При попытке удаления")    

#create_json(dir_path='Gk_sync',ball_coord=[0,1],robot_coord=[1,0],robot_current_state='stay')


