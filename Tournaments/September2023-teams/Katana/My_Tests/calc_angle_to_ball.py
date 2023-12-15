import math
# θ = atan2(Yb - Ya, Xb - Xa) - direction_A

# где:

# atan2 - это функция арктангенса с двумя аргументами, которая может определить угол между двумя точками;
# Ya и Xa - координаты объекта A;
# Yb и Xb - координаты объекта B;
# direction_A - текущее направление объекта A.

ballX = 0
ballY = 0
robotX= 0.6
robotY = 0.6
angle = -1.12
#1.5 рад +
dir_target = -0.325
dir_robot = 0.24198891555017

result = abs(dir_target-dir_robot)
print(result)
result = abs(dir_robot-dir_target)
print(result)

# dir_to_ball = abs(math.atan2(ballY-robotY,ballX-robotX))+angle 
# if angle<0:
#     dir_to_ball = -dir_to_ball
# if (robotY>ballY and robotX>ballX) or robotX<ballX :
#     dir_to_ball = -dir_to_ball
#2.56374
#если Y робота меньше Y мяча поворачиваем на положительный угол. Если больше то на отрицательный
# если и х и у меньше чем у мяча поворачиваем на отриц угол
# При плюсовом значении угла робот крутится против часовой стрелки, а при "-" по часовой.
#print(f'Робот X- {self.glob.pf_coord[0]} Робот Y- {self.glob.pf_coord[1]} catetA -{catetA} catetB -{catetB}')
#print(f'угол поворота {dir_to_ball}')

#if (self.motion.game_time() - second_player_timer) > 15 and (self.current_state =='near_distance_ball_approach_and_kick'or self.current_state =='forward far_distance_plan_approach') and abs(self.glob.pf_coord[2]-self.f.direction_To_Guest)<0.55: