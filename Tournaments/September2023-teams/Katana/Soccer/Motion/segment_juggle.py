
import math
# def find_First_segment(robot_dir,dir_to_ball,distance_to_ball):
#     #head_pose_seq = [0,5,10,1,6,11,2,7,12,3,8,13,4,9,14]
#     #если направление робота примерно равно направлению на мяч в районе 0,31 рад ищем мяч в центральных секторах
#     if robot_dir<dir_to_ball or robot_dir>dir_to_ball:
#         #Центральные сектора 2, 7, 12 от дальнего к ближнему
#         if abs(dir_to_ball-robot_dir)<=0.31 :
#             if distance_to_ball>0.4:
#                 return 2
#             if distance_to_ball>0.2 and distance_to_ball<0.4:
#                 return 7
#             if distance_to_ball<0.2:
#                 return 12
#     # Левые сектора 1, 6, 11, 0, 5, 10   
#     elif robot_dir>dir_to_ball and dir_to_ball>0:
#         # Левые сектора 1, 6, 11
#         if (robot_dir-dir_to_ball)>0.31 and (robot_dir-dir_to_ball)<=0.94:
#             if distance_to_ball>0.4:
#                 return 1
#             if distance_to_ball>0.2 and distance_to_ball<0.4:
#                 return 6
#             if distance_to_ball<0.2:
#                 return 11
#         # Левые сектора 0, 5, 10
#         if (robot_dir-dir_to_ball)>0.94 and (robot_dir-dir_to_ball)<=1.57 :
#             if distance_to_ball>0.4:
#                 return 0
#             if distance_to_ball>0.2 and distance_to_ball<0.4:
#                 return 5
#             if distance_to_ball<0.2:
#                 return 10
#     # Правые сектора 3, 8, 13, 4, 9, 14
#     elif robot_dir>dir_to_ball and dir_to_ball<0:
#         # Правые сектора 3, 8, 13
#         if (dir_to_ball-robot_dir)<-0.31 and (dir_to_ball-robot_dir)>=-0.94  :
#             if distance_to_ball>0.4:
#                 return 3
#             if distance_to_ball>0.2 and distance_to_ball<0.4:
#                 return 8
#             if distance_to_ball<0.2:
#                 return 13
#         # Правые сектора 4, 9, 14
#         if (dir_to_ball-robot_dir)> -0.94 and (dir_to_ball-robot_dir)>=-1.57  :
#             if distance_to_ball>0.4:
#                 return 4
#             if distance_to_ball>0.2 and distance_to_ball<0.4:
#                 return 9
#             if distance_to_ball<0.2:
#                 return 14
#     else:
#         return 2

# print(find_First_segment(1.5,0.6,0.49))

#------------------------------------------------------------------------------------

def find_First_segment(robot_dir, dir_to_ball, distance_to_ball):
    #head_pose_seq = [0,5,10,1,6,11,2,7,12,3,8,13,4,9,14]
    # если направление робота примерно равно направлению на мяч в районе 0,31 рад ищем мяч в центральных секторах
    if abs(robot_dir - dir_to_ball) <= 0.4:
        if distance_to_ball > 1.2:
            return 2
        elif 0.2 <= distance_to_ball <= 1.2:
            return 7
        else:
            return 12
    # Левые сектора 1, 6, 11, 0, 5, 10   
    elif robot_dir < dir_to_ball:
        # Левые сектора 1, 6, 11
        if dir_to_ball-robot_dir  <= 1.2:
            if distance_to_ball > 1.2:
                return 1
            elif 0.2 <= distance_to_ball <= 1.2:
                return 6
            else:
                return 11
        # Левые сектора 0, 5, 10
        else:
            if distance_to_ball > 1.2:
                return 0
            elif 0.2 <= distance_to_ball <= 1.2:
                return 5
            else:
                return 10
    # Правые сектора 3, 8, 13, 4, 9, 14
    elif robot_dir > dir_to_ball:
        # Правые сектора 3, 8, 13
        if  abs(robot_dir-dir_to_ball)  <= 1.2:
            if distance_to_ball > 1.2:
                return 3
            elif 0.2 <= distance_to_ball <= 1.2:
                return 8
            else:
                return 13
        # Правые сектора 4, 9, 14
        else:
            if distance_to_ball > 1.2:
                return 4
            elif 0.2 <= distance_to_ball <= 1.2:
                return 9
            else:
                return 14
    # Если ни одно из условий не выполняется, возвращаем значение по умолчанию
    else:
        return 2
# print(find_First_segment(-0.07,2.57, 0.33))  # Output: 1

#------------------------------------------------------------------------------------

# import math

# # Известные координаты мяча
# ball_coord = [0.5, 0.7, 0.1]

# # Угол поворота головы робота
# head_angle = 30 # в градусах

# # Расстояние от робота до мяча
# distance_to_ball = math.sqrt(ball_coord[0]**2 + ball_coord[1]**2)

# # Вычисляем угол alpha между направлением на мяч и направлением, куда смотрит робот
# alpha = math.degrees(math.atan2(ball_coord[1], ball_coord[0])) - head_angle

# # Если угол alpha выходит за пределы от -180 до 180 градусов, то корректируем его
# if alpha < -180:
#     alpha += 360
# elif alpha > 180:
#     alpha -= 360

# # Вычисляем сектор, в который нужно посмотреть в первую очередь
# sector_index = int((alpha + 22.5) / 45)
# if sector_index < 0:
#     sector_index += 8
# elif sector_index >= 8:
#     sector_index -= 8

# # Последовательность осмотра секторов
# head_pose_seq = [2,7,12,11,6,8,13,14,9,4,3,10,5,0,1,2]

# # Выбираем первый сектор в последовательности осмотра, исходя из найденного сектора
# first_sector = head_pose_seq[sector_index]

# print("Робот должен в первую очередь посмотреть в сектор", first_sector)

#------------------------------------------------------------------------------------
# def coord2yaw( x, y):
#         if x == 0:
#             if y > 0 : yaw = math.pi/2
#             else: yaw = -math.pi/2
#         else: yaw = math.atan(y/x)
#         if x < 0: 
#             if yaw > 0: yaw -= math.pi
#             else: yaw += math.pi
#         return yaw

# def find_First_segment(x1,y1,x2,y2,robot_dir,distance_to_ball):
#     x,y = x2-x1,y2-y1
#     dir_to_ball = math.atan(y/x)
#     print(coord2yaw(x,y))
#     return dir_to_ball
# print(find_First_segment(0.2,0.1,-0.15,1,0,0.3))