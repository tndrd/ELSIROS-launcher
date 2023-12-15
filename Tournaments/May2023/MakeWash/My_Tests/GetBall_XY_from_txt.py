import os
import json
import time
# принимаем путь к папке для голкипера и нападающего они разные  - 'Gk_sync' либо 'Frwd_sync'
def GetTeammateParams(dir_path='Gk_sync'):
        
    #dir_path = 'coordinates_folder'
    ball_coord =[]
    robot_coord = []
    robot_current_state =''

    
    # получаем список файлов в директории
    file_list = os.listdir(dir_path)

    # инициализируем переменные для хранения имени и времени создания самого нового файла
    newest_file = ''
    newest_time = 0
    data = None

    # проходим по каждому файлу в списке
    for file in file_list:
        try:
            # получаем полный путь к файлу
            file_path = os.path.join(dir_path, file)
            
            # получаем время создания файла
            file_time = os.path.getctime(file_path)
            
            # если время создания файла больше, чем время самого нового файла, то обновляем переменные
            if file_time > newest_time:
                newest_time = file_time
                newest_file = file
        except FileNotFoundError:
            print("Не могу узнать время создания. Нет файла")

    # выводим имя самого нового файла
    #print(f'The newest file is {newest_file}')
    try:
        with open(f'{dir_path}\\{newest_file}', 'r') as file:
                # читаем данные из файла
                data  = json.load(file)
                #print(data)
                ball_coord = data['ball_coord']
                robot_coord = data['robot_coord']
                robot_current_state = data['robot_current_state']
    except FileNotFoundError:
            print("FileNotFoundError. При попытке записи")
    except Exception:
            print(f"[{Exception}]. При попытке записи") 

    if time.time() - newest_time>20:
        #print(f'{time.time()} - {newest_time}={time.time()-newest_time}')
        return data, True
    else:
        return data, False
result,Is_old = GetTeammateParams() 
#print(Is_old) 
#print(f'Result = {result}')       
#print(f'{result["ball_coord"]["X"]},{result["ball_coord"]["Y"]},{result["robot_current_state"]},{Is_old},{time.time()}')
