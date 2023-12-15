import math
import json
import random

class Blurrer():
    """Simulate localization and vision noize. 
    Params is placed in the blurrer.json file.
    Args:
        object_angle_noize (float, optional): Noize for angle in radians.
            Blurrer will uniformly random value from -object_angle_noize 
            to object_angle_noize and add it to the ground truth course. 
            Defaults to 0.
        object_distance_noize (float, optional): Noize for distance in 
            percents divided by 100. Blurrer will uniformly random value 
            from -object_distance_noize to object_distance_noize and multiply 
            difference of 1 and this value with ground truth distance. 
            Defaults to 0..
        observation_bonus (float, optional): Blurrer will increase the 
            consistency for every good observation (successfuly processed 
            image). Defaults to 0..
        step_cost (float, optional): Blurrer will decrease the consistency
            for every simulation step. Defaults to 0..
        constant_loc_noize (float, optional): Constant localization noize. 
            Defaults to 0..
        loc_noize_meters (float, optional): Multiplier for consistency, in 
            meters. Defaults to 0. Defaults to 0..
    """

    def __init__(self, object_angle_noize=0., object_distance_noize=0.,
                 observation_bonus=0., step_cost=0., 
                 constant_loc_noize=0., loc_noize_meters=0.):

        self.object_angle_noize = object_angle_noize
        self.object_distance_noize = object_distance_noize
        self.observation_bonus = observation_bonus
        self.step_cost = step_cost
        self.constant_loc_noize = constant_loc_noize
        self.loc_noize_meters = loc_noize_meters

        params = self.load_json("E:\\Elsiros\\controllers\\player\\blurrer.json")

        self.consistency = 1
        self.receiver = None
        #penalty = self.receiver.player_state.penalty

    def load_json(self, filename):
        with open(filename) as f:
            params = json.load(f)

        self.object_angle_noize = params["object_angle_noize"]
        self.object_distance_noize = params["object_distance_noize"]
        self.observation_bonus = params["observation_bonus"]
        self.step_cost = params["step_cost"]
        self.constant_loc_noize = params["constant_loc_noize"]
        self.loc_noize_meters = params["loc_noize_meters"]

    def course(self, angle):
        return angle + random.uniform(-self.object_angle_noize, self.object_angle_noize)

    def distance(self, distance):
        return distance * (1 + random.uniform(-self.object_distance_noize, self.object_distance_noize))

    def objects(self, course=course, distance=distance):
        return (self.course(course), self.distance(distance))

    def loc(self, x, y):
        return (self.coord(x), self.coord(y))

    def coord(self, p):
        random_factor = 1 - self.consistency
        print(f"random_factor { random_factor} self.consistency {self.consistency}")
        print(f" coord {p} -> {p + self.loc_noize_meters * random.uniform(-random_factor, random_factor)}")
        return p + self.loc_noize_meters * random.uniform(-random_factor, random_factor)

    def step(self):
        self.update_consistency(-self.step_cost)

    def observation(self):
        self.update_consistency(self.observation_bonus)

    def update_consistency(self, value):
        tmp = self.consistency + value
        self.consistency = max(0, min(tmp, 1))
# x1= -20
# y1= 20
# x2= 45
# y2= -25
# x3= 20
# y3= -15
# distance = 10
__blurrer = Blurrer()



res = __blurrer.loc(1.3, -0.4)
print (res)

# '''
# Проверяем находятся ли координаты (х3,y3) между точек с (x1-y1) (x2-y2)
# и находится ли третья точка на расстоянии не более distance от прямой соединяющей две другие
# '''

# def is_within_distance(x1, y1, x2, y2, x3, y3, distance):
#     three_beetwin_1_2 =False
#     three_touch_line_1_2 = False
#     if abs(x1-x2)> abs(x1-x3) and  abs(y1-y2)>abs(y1-y3) and ((x1<x3<x2  and  y1<y3<y2) or (x1<x3<x2  and  y1>y3>y2) or (x1>x3>x2 and y1<y3<y2) or (x1>x3>x2 and y1>y3>y2) ):
#         print('Точка 3 между 1 и 2') 
#         three_beetwin_1_2 = True
#     else:
#         print('Точка 3 НЕ между 1 и 2')
#         three_beetwin_1_2 = False
 
#     d = abs((y2 - y1) * x3 - (x2 - x1) * y3 + x2 * y1 - y2 * x1) / ((y2 - y1)**2 + (x2 - x1)**2)**0.5
#     if d <= distance:
#         three_touch_line_1_2 = True
#     else:
#         three_touch_line_1_2 = False
#     return three_touch_line_1_2 and three_beetwin_1_2


# def coord2yaw( x, y):
#         if x == 0:
#             if y > 0 : yaw = math.pi/2
#             else: yaw = -math.pi/2
#         else: yaw = math.atan(y/x)
#         if x < 0: 
#             if yaw > 0: yaw -= math.pi
#             else: yaw += math.pi
#         return yaw
# #print(is_within_distance(x1, y1, x2, y2, x3, y3, distance))
# field_length = 3.6
# ball_x = 1.4
# ball_y = -0.8
# robot_x = 0.4
# robot_y = 1.2
# dir_r= -0.7
# dir_b = -1.95

# duty_x_position =  min((-field_length/2 + 0.4),(ball_x-field_length/2)/2)
# print(f'duty_x_position {duty_x_position}')
# duty_y_position = ball_y * (duty_x_position + field_length/2) / (ball_x + field_length/2) 
# print(f'duty_y_position {duty_y_position}')
# duty_distance = math.sqrt((duty_x_position - robot_x)**2 + (duty_y_position - robot_y )**2)
# print(f'duty_distance {duty_distance}')
# if duty_distance<0.2:
#     print('В начало цикла')
# elif duty_distance <  3:
#     duty_direction = coord2yaw(duty_x_position - robot_x, duty_y_position - robot_y) 
#     print(f'Идем {duty_distance*1000+196}мм  в направлении {duty_direction}')
# else:
#     print(f'сокращаем дистанцию двигаясь к координатам X {duty_x_position + 0.25}, Y {duty_y_position}')
# print(f'{abs(dir_r-dir_b )}')
# x = -2
# y = 0.4
# yaw = math.atan(y/x)
# print(yaw )
