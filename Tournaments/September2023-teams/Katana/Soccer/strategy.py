"""
Модуль разработан командой Робокит Физтех-лицея и командой Starkit.
МФТИ под руководством Азера Бабаева.
Модуль предназначен для стратегии игры в футбол для нападающего и вратаря.

"""
import sys
import os
import math
import json
import time
import logging
from . import utility

from My_Tests.GetBall_XY_from_txt import GetTeammateParams
from My_Tests.create_file import create_json
from My_Tests.frwd_strategy_modify import What_I_do
from Soccer.Motion.segment_juggle import find_First_segment

class GoalKeeper:
    """
    Класс GoalKeeper предназначен для определения игры вратаря в соответствии со стилем, разработанным
     Матвей Иващенко - студент Физтех-лицея 2020 года.
     Идея стиля заключалась в разделении домашней половины футбольного поля на 8 секторов в зависимости от расстояния.
     от домашних голов. Когда мяч находится в 4 секторах, ближайших к воротам А1, А2, А3, А4, вратарь атакует мяч
     цель перевести его на сторону противника. Когда мяч находится в 4 секторах B1, B2, B3, B4, которые являются более длинными
     расстояние от ворот вратарь просто переместится в лучшую позицию от текущей без попытки
     атаковать мяч.
     В случае, если мяч после удара вратаря не прошел дальше 1 м, он предпринимает еще одну попытку.
     всего до 10 раз.
     В случае, если мяч уходит на расстояние более 1 м или мяч не виден вратарю, то вратарь
     возвращается в центр ворот.
    """
    def __init__(self, logger, motion, local, glob):
        self.logger = logger
        self.motion = motion
        self.local = local
        self.glob = glob
        self.direction_To_Guest = 0
        #self.start_segment_Viev = 2
        

    def turn_Face_To_Guest(self):
        """
        Метод предназначен для определения направления удара и загрузки его в self.direction_To_Guest.
         направление измеряется в радианах рыскания.
         После определения направления удара робот поворачивается в этом направлении.
         В случае если собственная координата робота self.glob.pf_coord показывает ссылку на свою половину поля
         т. е. self.glob.pf_coord[0] < 0, тогда направление съемки равно 0
         если координата x роботов > 0,8 и абс (координата y) > 0,6, то направление удара в центр
         голов соперников.
         если у роботов x < 1,5 и abs(y) < 0,25 направление удара будет в угол ворот соперника,
         с левым или правым углом определяется случайным образом.
         во всех остальных положениях направление удара робота определяется как направление на точку цели с
         координатами х = 0, у = 2,8
        """
        if self.glob.pf_coord[0] < 0:
            self.motion.turn_To_Course(0)
            self.direction_To_Guest = 0
            return
        elif self.glob.pf_coord[0] > 0.8 and abs(self.glob.pf_coord[1]) > 0.6:
            self.direction_To_Guest = math.atan(-self.glob.pf_coord[1]/(1.8-self.glob.pf_coord[0]))
            self.motion.turn_To_Course(self.direction_To_Guest)
        elif self.glob.pf_coord[0] < 1.5 and abs(self.glob.pf_coord[1]) < 0.25:
            if (1.8-self.glob.ball_coord[0]) == 0: self.direction_To_Guest = 0
            else: self.direction_To_Guest = math.atan((0.4* (round(utility.random(),0)*2 - 1)-
                                                       self.glob.ball_coord[1])/(1.8-self.glob.ball_coord[0]))
            self.motion.turn_To_Course(self.direction_To_Guest)
            return
        else:
            self.direction_To_Guest = math.atan(-self.glob.pf_coord[1]/(2.8-self.glob.pf_coord[0]))
            self.motion.turn_To_Course(self.direction_To_Guest)

    def goto_Center(self):                      #Function for reterning to center position
        """
        Вратарь возвращается в исходное положение на расстоянии 0,4 м от собственных ворот.
         перед возвращением робот проверяет достоверность локализации. Если локализация плохая, то берется робот
         специальные движения головой и поворотом к воротам с целью улучшения локализации.
         В случае, если расстояние до рабочего места более 0,5 м, будет использоваться far_distance_plan_approach,
         иначе будет использоваться Near_distance_omni_motion.
         после возвращения в боевое положение робот поворачивается в сторону удара, для которого рыскание=0 перед собственными воротами.

        """
        self.logger.info('Function for reterning to center position')
        if self.local.coordinate_trust_estimation() < 0.5: self.motion.localisation_Motion()
        player_X_m = self.glob.pf_coord[0]
        player_Y_m = self.glob.pf_coord[1]
        duty_position_x = - self.glob.landmarks['FIELD_LENGTH']/2 + 0.4
        distance_to_target = math.sqrt((duty_position_x -player_X_m)**2 + (0 - player_Y_m)**2 )
        if distance_to_target > 0.5 :
            target_in_front_of_duty_position = [duty_position_x + 0.15, 0]
            if distance_to_target > 1: stop_Over = True
            else: stop_Over = False
            self.motion.far_distance_plan_approach(target_in_front_of_duty_position, self.direction_To_Guest, stop_Over = stop_Over)
        else:
            if (duty_position_x -player_X_m)==0:
                alpha = math.copysign(math.pi/2, (0 - player_Y_m) )
            else:
                if (duty_position_x - player_X_m)> 0: alpha = math.atan((0 - player_Y_m)/(duty_position_x -player_X_m))
                else: alpha = math.atan((0 - player_Y_m)/(duty_position_x - player_X_m)) + math.pi
            napravl = alpha - self.motion.imu_body_yaw()
            dist_mm = distance_to_target * 1000
            self.motion.near_distance_omni_motion(dist_mm, napravl)
        self.turn_Face_To_Guest()

    def find_Ball(self):
        """
        Перед использованием метода движения seek_Ball_In_Pose вратарь определяет использование метода в быстром режиме или в точном режиме.
         В случае, если локализация является достоверной, используется быстрый режим, означающий fast_Reaction_On=True.
         Метод seek_Ball_In_Pose перемещает голову робота на 15 позиций, охватывая все видимые области спереди и по бокам робота.
         Таким образом, поиск мяча не является единственной задачей. Робот улучшает локализацию, наблюдая за маркерами локализации на
         полученные снимки.
         В случае, если fast_Reaction_On=True, то наблюдение за окружением будет прервано, как только мяч появится в поле зрения
         сектор. Также определяется скорость мяча. 
        """
        fast_Reaction_On=True
        if self.local.coordinate_trust_estimation() < 0.5: fast_Reaction_On = False
        if self.glob.ball_coord[0] <= 0: fast_Reaction_On=True
        success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On=fast_Reaction_On,start_segment_Viev=2)
        self.logger.debug( 'dist = ' + str(dist) + 'napravl =' + str(napravl))
        return success_Code, dist, napravl, speed

    def scenario_A1(self, dist, napravl):#The robot knock out the ball to the side of the opponent
        """
        Этот метод активируется, если вратарь находит мяч на расстоянии менее 0,7 м и относительном направлении.
         от 0 до math.pi/4. Предположим, что вратарь стоит на боевом посту лицом к воротам соперника перед поиском мяча.
         Применение:
             Нет: self.scenario_A1(float:dist, float: направление)
                 dist - расстояние до мяча от вратаря в метрах
                 направление - относительное направление мяча от вратаря в радианах

         метод Предпримите 10 попыток отбросить мяч на сторону соперника. В случае удачной попытки мяч уходит на 1 м от
         голкипер - вратарь возвращается в служебное положение перед собственными воротами. В противном случае попытки продолжаются до 10 раз.
        """
        self.logger.info('The robot knock out the ball to the side of the opponent')
        for i in range(10):
            if dist > 0.5 :
                if dist > 1: stop_Over = True
                else: stop_Over = False
                self.motion.far_distance_plan_approach(self.glob.ball_coord, self.direction_To_Guest, stop_Over = stop_Over)
            self.turn_Face_To_Guest()
            success_Code = self.motion.near_distance_ball_approach_and_kick(self.direction_To_Guest,start_segment_Viev=2)
            if success_Code == False and self.motion.falling_Flag != 0: return
            if success_Code == False : break
            success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = False,start_segment_Viev=2)
            if dist > 1 : break
        target_course1 = self.glob.pf_coord[2] +math.pi
        self.motion.turn_To_Course(target_course1)
        self.goto_Center()

    def scenario_A2(self, dist, napravl):#The robot knock out the ball to the side of the opponent
        """
        Этот метод активируется, если вратарь находит мяч на расстоянии менее 0,7 м и относительном направлении.
         от math.pi/4 до math.pi/2. Предположим, что вратарь стоит на боевом посту лицом к воротам соперника перед поиском мяча.
         Применение:
             Нет: self.scenario_A1(float:dist, float: направление)
                 dist - расстояние до мяча от вратаря в метрах
                 направление - относительное направление мяча от вратаря в радианах

         метод Предпримите 10 попыток отбросить мяч на сторону соперника. В случае удачной попытки мяч уходит на 1 м от
         голкипер - вратарь возвращается в служебное положение перед собственными воротами. В противном случае попытки продолжаются до 10 раз.
        """
        self.logger.info('The robot knock out the ball to the side of the opponent')
        self.scenario_A1( dist, napravl)

    def scenario_A3(self, dist, napravl):#The robot knock out the ball to the side of the opponent
        """
        This method is activated if goalkeeper finds ball at distance less than 0.7m and relative direction
        from 0 to -math.pi/4. Supposed that goalkeeper stands on duty position faced to opponents' goals before seeking ball.
        usage: 
            None: self.scenario_A1(float:dist, float: napravl)
                dist -      distance to ball from goalkeeper in meters
                napravl -   relative direction to ball from goalkeeper in radians 

        method undertake 10 attempts to kick off ball to opponents side. In case of successful attempt - ball goes 1m away from 
        goalkeeper - goalkeeper returns to duty position in front of own goals. Otherwise attempts are continued up to 10 times.
        """
        self.logger.info('The robot knock out the ball to the side of the opponent')
        self.scenario_A1( dist, napravl)

    def scenario_A4(self, dist, napravl):#The robot knock out the ball to the side of the opponent
        """
        This method is activated if goalkeeper finds ball at distance less than 0.7m and relative direction
        from -math.pi/4 to -math.pi/2. Supposed that goalkeeper stands on duty position faced to opponents' goals before seeking ball.
        usage: 
            None: self.scenario_A1(float:dist, float: napravl)
                dist -      distance to ball from goalkeeper in meters
                napravl -   relative direction to ball from goalkeeper in radians 

        method undertake 10 attempts to kick off ball to opponents side. In case of successful attempt - ball goes 1m away from 
        goalkeeper - goalkeeper returns to duty position in front of own goals. Otherwise attempts are continued up to 10 times.
        """
        self.logger.info('The robot knock out the ball to the side of the opponent')
        self.scenario_A1( dist, napravl)

    def scenario_B1(self):#the robot moves to the left and stands on the same axis as the ball and the opponents' goal
        """
        This method is activated if goalkeeper finds ball at distance more than 0.7m and less than half of length of field
        and relative direction from 0 to math.pi/4. 
        Supposed that goalkeeper stands on duty position faced to opponents' goals before seeking ball.
        method undertake to slide robot sideways to same Y coordinate as balls' Y coordinate. In case if balls' Y coordinate
        abs value is more than 0.4m robots maximum Y coordinate abs value will be 0.4m
        After sliding sideways robot undertake turning to 0 direction
        """
        self.logger.info('the robot moves to the left 4 steps')
        if self.glob.ball_coord[1] > self.glob.pf_coord[1]:
            if self.glob.ball_coord[1] > 0.4: 
                if self.glob.pf_coord[1] < 0.4:
                    self.motion.near_distance_omni_motion( 1000*(0.4 - self.glob.pf_coord[1]), math.pi/2)
            else:
                self.motion.near_distance_omni_motion( 1000*(self.glob.ball_coord[1] - self.glob.pf_coord[1]), math.pi/2)
        self.turn_Face_To_Guest()

    def scenario_B2(self):#the robot moves to the left and stands on the same axis as the ball and the opponents' goal
        """
        This method is activated if goalkeeper finds ball at distance more than 0.7m and less than half of length of field
        and relative direction from 0 to math.pi/4. 
        Supposed that goalkeeper stands on duty position faced to opponents' goals before seeking ball.
        method undertake to slide robot sideways to same Y coordinate as balls' Y coordinate. In case if balls' Y coordinate
        abs value is more than 0.4m robots maximum Y coordinate abs value will be 0.4m
        After sliding sideways robot undertake turning to 0 direction
        """
        self.logger.info('the robot moves to the left 4 steps')
        self.scenario_B1()

    def scenario_B3(self):#the robot moves to the right and stands on the same axis as the ball and the opponents' goal
        """
        This method is activated if goalkeeper finds ball at distance more than 0.7m and less than half of length of field
        and relative direction from 0 to math.pi/4. 
        Supposed that goalkeeper stands on duty position faced to opponents' goals before seeking ball.
        method undertake to slide robot sideways to same Y coordinate as balls' Y coordinate. In case if balls' Y coordinate
        abs value is more than 0.4m robots maximum Y coordinate abs value will be 0.4m
        After sliding sideways robot undertake turning to 0 direction
        """
        self.logger.info('the robot moves to the right 4 steps')
        #self.motion.first_Leg_Is_Right_Leg = True
        #self.motion.near_distance_omni_motion( 110, -math.pi/2)
        if self.glob.ball_coord[1] < self.glob.pf_coord[1]:
            if self.glob.ball_coord[1] < -0.4: 
                if self.glob.pf_coord[1] > -0.4:
                    self.motion.near_distance_omni_motion( 1000*(0.4 + self.glob.pf_coord[1]), -math.pi/2)
            else:
                self.motion.near_distance_omni_motion( 1000*(-self.glob.ball_coord[1] + self.glob.pf_coord[1]), -math.pi/2)
        self.turn_Face_To_Guest()

    def scenario_B4(self):#the robot moves to the right and stands on the same axis as the ball and the opponents' goal
        """
        This method is activated if goalkeeper finds ball at distance more than 0.7m and less than half of length of field
        and relative direction from 0 to math.pi/4. 
        Supposed that goalkeeper stands on duty position faced to opponents' goals before seeking ball.
        method undertake to slide robot sideways to same Y coordinate as balls' Y coordinate. In case if balls' Y coordinate
        abs value is more than 0.4m robots maximum Y coordinate abs value will be 0.4m
        After sliding sideways robot undertake turning to 0 direction
        """
        self.logger.info('the robot moves to the right 4 steps')
        self.scenario_B3()

class Forward:
    """
    The class Forward is designed for definition of strategy of play for 'forward' role of player 
    in year 2020.
    usage:
        Forward(object: motion, object: lical, object: glob)
    """
    def __init__(self, logger, motion, local, glob):
        self.logger = logger
        self.motion = motion
        self.local = local
        self.glob = glob
        self.direction_To_Guest = 0
        #self.start_segment_Viev =2

    def dir_To_Guest(self):
        """
        The method is designed to define kick direction and load it into self.direction_To_Guest,
        direction is measured in radians of yaw. 
        In case if robots' own coordinate self.glob.pf_coord shows lication on own half of field
        i.e. self.glob.pf_coord[0] < 0 then direction of shooting is 0
        if robots' x coordinate > 0.8 and abs(y coordinate) > 0.6 then direction of kick is to center
        of opponents' goals.
        if robots' x < 1.5 and abs(y) < 0.25 kick direction will be to corner of opponents' goals, 
        with left or right corner is defined randomly.
        in all other positions of robot kick direction is defined as ditection to target point with
        coordinates x = 0, y = 2.8
        returns float: self.direction_To_Guest
        """
        if self.glob.ball_coord[0] < 0:
            self.direction_To_Guest = 0
        elif self.glob.ball_coord[0] > 0.8 and abs(self.glob.ball_coord[1]) > 0.6:
            self.direction_To_Guest = math.atan(-self.glob.ball_coord[1]/(1.8-self.glob.ball_coord[0]))
        elif self.glob.ball_coord[0] < 1.5 and abs(self.glob.ball_coord[1]) < 0.25:
            if (1.8-self.glob.ball_coord[0]) == 0: self.direction_To_Guest = 0
            else:
                if abs(self.glob.ball_coord[1]) > 0.2:
                    self.direction_To_Guest = math.atan((math.copysign(0.2, self.glob.ball_coord[1])-
                                                       self.glob.ball_coord[1])/(1.8-self.glob.ball_coord[0]))
                else:
                    self.direction_To_Guest = math.atan((0.2* (round(utility.random(),0)*2 - 1)-
                                                       self.glob.ball_coord[1])/(1.8-self.glob.ball_coord[0]))
        else:
            self.direction_To_Guest = math.atan(-self.glob.pf_coord[1]/(2.8-self.glob.pf_coord[0]))
        return self.direction_To_Guest

    def turn_Face_To_Guest(self):
        self.dir_To_Guest()
        self.motion.turn_To_Course(self.direction_To_Guest)

class Forward_Vector_Matrix:
    """
    The class Forward_Vector_Matrix is designed for definition of strategy of play for 'forward' role of player 
    in year 2021.
    Matrix is coded in file strategy_data.json  This file is readable and editable as well as
    normal text file. There is a dictionary with one key “strategy_data”. Value of key
    “strategy_data” is a list with default number of elements 234. Each element of list represents
    rectangular sector of soccer field with size 20cmX20cm. For each sector there assigned a vector
    representing yaw direction of shooting when ball is positioned in this sector. Power of shot is
    coded by attenuation value: 1 – standard power, 2 – power reduced 2 times, 3- power reduced 3 times.
    Each element of list is coded as follows: [column, row, power, yaw]. Soccer field is split to
    sectors in 13 rows and 18 columns.  Column 0 is near own goals, column 17 is near opposed goals.
    Row 0 is in positive Y coordinate, row 12 is in negative Y coordinate.
    Strategy data is imported from strategy_data.json file into self.glob.strategy_data list.
    usage:  
        Forward_Vector_Matrix(object: motion, object: local, object: glob)
    """
    def __init__(self, logger, motion, local, glob):
        self.logger = logger
        self.motion = motion
        self.local = local
        self.glob = glob
        self.direction_To_Guest = 0
        self.kick_Power = 1
        #self.start_segment_Viev =2

    def dir_To_Guest(self):
        """
        The method is designed to define kick direction and load it into self.direction_To_Guest.
        Direction is measured in radians of yaw.
        usage:
            int: row, int: col = self.dir_To_Guest()
            row, col  -  row and column of matrix attributing rectangular sector of field where
            ball coorinate  self.glob.ball_coord fits.
        """
        if abs(self.glob.ball_coord[0])  >  self.glob.landmarks["FIELD_LENGTH"] / 2:
            ball_x = math.copysign(self.glob.landmarks["FIELD_LENGTH"] / 2, self.glob.ball_coord[0])
        else: ball_x = self.glob.ball_coord[0]
        if abs(self.glob.ball_coord[1])  >  self.glob.landmarks["FIELD_WIDTH"] / 2:
            ball_y = math.copysign(self.glob.landmarks["FIELD_WIDTH"] / 2, self.glob.ball_coord[1])
        else: ball_y = self.glob.ball_coord[1]
        col = math.floor((ball_x + self.glob.landmarks["FIELD_LENGTH"] / 2) / (self.glob.landmarks["FIELD_LENGTH"] / self.glob.COLUMNS))
        row = math.floor((- ball_y + self.glob.landmarks["FIELD_WIDTH"] / 2) / (self.glob.landmarks["FIELD_WIDTH"] / self.glob.ROWS))
        if col >= self.glob.COLUMNS : col = self.glob.COLUMNS - 1
        if row >= self.glob.ROWS : row = self.glob.ROWS -1
        self.direction_To_Guest = self.glob.strategy_data[(col * self.glob.ROWS + row) * 2 + 1] / 40
        self.kick_Power = self.glob.strategy_data[(col * self.glob.ROWS + row) * 2]
        self.logger.debug('direction_To_Guest = ' + str(math.degrees(self.direction_To_Guest)))
        return row, col

    def turn_Face_To_Guest(self):
        self.dir_To_Guest()
        self.motion.turn_To_Course(self.direction_To_Guest)

class Player():
    """
    class Player is designed for implementation of main cycle of player.
    Real robot have 3 programmable buttons. Combination of button pressing can transmit to programm pressed button
    code from 1 to 9. At initial button pressing role of player is selected. With second pressed button optional
    playing mode is selected depending on role. 
    For 'forward' and 'forward_old_style' role  second_pressed_button can take value 1 or value 4. With value 1
    player starts game as kick-off player,
    with value 4 player stars as non-kick-off player, which means player starts moving 10 seconds later.
    For 'run_test' role second_pressed_button can take values from 1 or value 9 with following optional modes:
    1 - 10 cycle steps walk forward
    2 - 20 cycle side step walk to right
    3 - 20 cycle side step walk to left
    4 - 20 cycle steps walk forward
    5 - 20 cycle steps with rotation to right side
    6 - 20 cycle steps with rotation to left side
    9 - 20 cycle steps of spot walk 
    All modes of run test are used with purpose to calibrate walking. After calibration is completed results of
    calibration must be input to file  Sim_params.json. Motion module is used calibration data for planning
    motions and odometry correction into localization.
    usage:
        Player(str: role, int: second_pressed_button, object: glob, object: motion, object: local)
    """
    def __init__(self, logger, role, second_pressed_button, glob, motion, local):
        self.logger = logger
        self.role = role   #'goalkeeper', 'penalty_Goalkeeper', 'forward', 'penalty_Shooter'
        self.second_pressed_button = second_pressed_button
        self.glob = glob
        self.motion = motion
        self.local = local
        self.g = None
        self.f = None
        self.current_state =''
        self.start_segment_Viev =2
        self.neck_play_pose = -788


    def play_game(self):
        #success_Code, napravl, dist, speed = self.motion.seek_Ball_In_Pose(fast_Reaction_On = True)
        #self.motion.pause_in_ms(200)    # this is needed for camera renewal in simulation with streaming of camera data. pause have to be same langth as camera update time
        if self.role == 'goalkeeper': self.goalkeeper_main_cycle()
        if self.role == 'goalkeeper_old_style': self.goalkeeper_old_style_main_cycle()
        if self.role == 'penalty_Goalkeeper': self.penalty_Goalkeeper_main_cycle()
        if self.role == 'forward': self.forward_main_cycle(self.second_pressed_button)
        if self.role == 'forward_old_style': self.forward_old_style_main_cycle(self.second_pressed_button)
        if self.role == 'penalty_Shooter': self.penalty_Shooter_main_cycle()
        if self.role == 'run_test': self.run_test_main_cycle(self.second_pressed_button)
        if self.role == 'rotation_test': self.rotation_test_main_cycle()
        if self.role == 'sidestep_test': self.sidestep_test_main_cycle()
        if self.role == 'dance': self.dance_main_cycle()


    def run_test_main_cycle(self, pressed_button):
        """
        For 'run_test' role second_pressed_button can take values from 1 or value 9 with following optional modes:
        1 - 10 cycle steps walk forward
        2 - 20 cycle side step walk to right
        3 - 20 cycle side step walk to left
        4 - 20 cycle steps walk forward
        5 - 20 cycle steps with rotation to right side
        6 - 20 cycle steps with rotation to left side
        9 - 20 cycle steps of spot walk 
        All modes of run test are used with purpose to calibrate walking. After calibration is completed results of
        calibration must be input to file  Sim_params.json. Motion module is used calibration data for planning
        motions and odometry correction into localization.
        usage:
            self.run_test_main_cycle(int: pressed_button)
        """
        if pressed_button == 2 or pressed_button ==3 :
            self.sidestep_test_main_cycle(pressed_button)
            return
        if pressed_button == 5 or pressed_button ==6 :
            self.rotation_test_main_cycle(pressed_button)
            return
        stepLength = 64
        if pressed_button == 9: stepLength = 0
        number_Of_Cycles = 20
        if pressed_button == 1: number_Of_Cycles = 10
        sideLength = 0
        #self.motion.first_Leg_Is_Right_Leg = False
        if self.motion.first_Leg_Is_Right_Leg: invert = -1
        else: invert = 1
        self.motion.walk_Initial_Pose()
        number_Of_Cycles += 1
        for cycle in range(number_Of_Cycles):
            stepLength1 = stepLength
            if cycle ==0 : stepLength1 = stepLength/3
            if cycle ==1 : stepLength1 = stepLength/3 * 2
            self.motion.refresh_Orientation()
            rotation = 0 + invert * self.motion.imu_body_yaw() * 1.2
            if rotation > 0: rotation *= 1.5
            rotation = self.motion.normalize_rotation(rotation)
            #rotation = 0
            self.motion.walk_Cycle(stepLength1,sideLength, rotation,cycle, number_Of_Cycles)
        self.motion.walk_Final_Pose()

    def sidestep_test_main_cycle(self, pressed_button):
        number_Of_Cycles = 10
        stepLength = -20
        sideLength = 58
        if pressed_button == 3:
            self.motion.first_Leg_Is_Right_Leg = False
        if self.motion.first_Leg_Is_Right_Leg: invert = -1
        else: invert = 1
        self.motion.walk_Initial_Pose()
        for cycle in range(number_Of_Cycles):
            stepLength1 = stepLength
            #if cycle ==0 : stepLength1 = stepLength/3
            #if cycle ==1 : stepLength1 = stepLength/3 * 2
            self.motion.refresh_Orientation()
            rotation = 0 + invert * self.motion.imu_body_yaw() * 1.0
            rotation = self.motion.normalize_rotation(rotation)
            #rotation = 0
            self.motion.walk_Cycle(stepLength1,sideLength, rotation,cycle, number_Of_Cycles)
        self.motion.walk_Final_Pose()
        #без строчки ниже сходит с ума при использовании метода self.motion.turn_To_Course
        #так как она заточена под поворот с правой ноги
        self.motion.first_Leg_Is_Right_Leg = True

    def norm_yaw(self, yaw):
        """
        This module normalizes yaw according to internal rule: -pi <= yaw <= pi
        usage:
            float: yaw = self.norm_yaw(float: yaw)
            yaw - orientation on horizontal surface in radians, 
                  zero value orientation is directed along X axis
        """
        yaw %= 2 * math.pi
        if yaw > math.pi:  yaw -= 2* math.pi
        if yaw < -math.pi: yaw += 2* math.pi
        return yaw
    
    def rotation_test_main_cycle(self, pressed_button,number_Of_Cycles_,rotation_,stepLength_ =0,sideLength_ = 20):
        number_Of_Cycles = number_Of_Cycles_+1
        stepLength = stepLength_
        sideLength = sideLength_
        if pressed_button == 6:
            rotation = rotation_# 0.483

        else: 
            rotation = rotation_
            #без строчки ниже крутится не в ту сторону
            self.motion.first_Leg_Is_Right_Leg = False
        self.logger.info(f'rotation = {rotation}')
        
        if self.motion.first_Leg_Is_Right_Leg: invert = -1
        else: invert = 1
        self.motion.walk_Initial_Pose()
        for cycle in range(number_Of_Cycles):
            self.motion.walk_Cycle(stepLength,sideLength, rotation, cycle, number_Of_Cycles)
        self.motion.walk_Final_Pose()
        self.motion.refresh_Orientation()
        self.logger.debug('self.motion.imu_body_yaw() =' + str(self.motion.imu_body_yaw()))
        #без строчки ниже сходит с ума при использовании метода self.motion.turn_To_Course
        #так как она заточена под поворот с правой ноги
        self.motion.first_Leg_Is_Right_Leg = True

    def move_on_radius(self,radius, side_length,target_angle, current_angle):
            # Рассчет длины окружности
            circumference = 2 * math.pi * radius

            # Рассчет количества циклов
            number_of_cycles = circumference / (side_length/1000)

            # Рассчет угла поворота на каждом цикле
            rotation_angle = 2 * math.pi / number_of_cycles
            self.logger.info(f'rotation_angle = {rotation_angle}')

            number_of_cycles = abs(target_angle - current_angle) / rotation_angle
            self.logger.info(f'number_of_cycles = {number_of_cycles}')

            return round(number_of_cycles), rotation_angle
    def gate_escape(self,x,y):
        #Находимся за воротами соперника
        if x>2 and y>-0.5 and y<0.5:
            out_dist = (x-1.6)*1000+200
            self.motion.turn_To_Course(3.14)
            self.motion.near_distance_omni_motion(150,3)
            if y>=0:
                near_dist = abs(y-0.58)*1000+200
                self.motion.turn_To_Course(1.57)
                self.motion.near_distance_omni_motion(near_dist,0)
                self.motion.turn_To_Course(3.14)
                self.motion.near_distance_omni_motion(out_dist,0)
            else:
                near_dist = abs(y+0.58)*1000+200
                self.motion.turn_To_Course(-1.57)
                self.motion.near_distance_omni_motion(near_dist,0)
                self.motion.turn_To_Course(3.14)
                self.motion.near_distance_omni_motion(out_dist,0)

        #Находимся за своими воротами
        if x<-2 and y>-0.5 and y<0.5:
            out_dist = abs(x+1.6)*1000+200
            self.motion.turn_To_Course(0)
            self.motion.near_distance_omni_motion(150,3)
            if y>=0:
                near_dist = abs(y-0.58)*1000+200
                self.motion.turn_To_Course(1.57)
                self.motion.near_distance_omni_motion(near_dist,0)
                self.motion.turn_To_Course(0)
                self.motion.near_distance_omni_motion(out_dist,0)
            else:
                near_dist = abs(y+0.58)*1000+200
                self.motion.turn_To_Course(-1.57)
                self.motion.near_distance_omni_motion(near_dist,0)
                self.motion.turn_To_Course(0)
                self.motion.near_distance_omni_motion(out_dist,0)

    def forward_main_cycle(self, pressed_button):
        """
        Main cycle method for 'forward' role of player.
        usage:
            self.forward_main_cycle(int: pressed_button)
        """
        
        
        def Save_FWRD_params(duty_direction = 0):
            create_json(dir_path='Fwrd_sync',ball_coord=[self.glob.ball_coord[0],self.glob.ball_coord[1]],
                            robot_coord=[self.glob.pf_coord[0],self.glob.pf_coord[1]],
                            robot_current_state=f'{self.current_state}',duty_direction = duty_direction)
            

        def Get_ball_from_GK(result,Is_old):
            if not Is_old:
                if result!= None:
                    ballX = result['ball_coord']["X"]
                    ballY = result['ball_coord']["Y"]
                    Gk_state = result['robot_current_state']
                    ball_coord =[ballX,ballY]
                    return  (ball_coord,Gk_state)
            return None,''
        
        ''' 02.08'''
        def Get_gk_coord_and_duty_dist(result,Is_old):
            if not Is_old:
                if result!= None:
                    GK_X = result['robot_coord']["X"]
                    GK_Y = result['robot_coord']["Y"]
                    Gk_duty_dir = result['duty_direction']
                    Gk_state = result['robot_current_state']
                    self.logger.info(f'X_F<X_GK {self.glob.pf_coord[0]<GK_X}')
                    self.logger.info(f'Y_F -Y_GK = {abs(self.glob.pf_coord[1]-GK_Y)}')
                    self.logger.info(f'Gk_dd {Gk_duty_dir}')

                    if self.glob.pf_coord[0]<GK_X and abs(self.glob.pf_coord[1]-GK_Y)<0.25 and Gk_state=="goalkeeper turn_To_Course(0)": #and abs(Gk_duty_dir) >1:
                        return True
            return False  
        ''' 02.08'''

        second_player_timer = self.motion.game_time()                       # ignition of timer for non-kick-off forward player
        what_I_do_timer = self.motion.game_time()
        Go_back_or_Fwrd = True
        #start_segment_Viev =2 
        self.f = Forward_Vector_Matrix(self.logger, self.motion, self.local, self.glob)
        Is_first_ball  = True
        while (True):
            #self.logger.info(f'Цикл в начале {self.motion.game_time()}')
            
            if pressed_button == 4 and Go_back_or_Fwrd: 
                Go_back_or_Fwrd = False
                self.motion.turn_To_Course(-0.2)
           
            #if self.motion.falling_Flag == 0:
            if pressed_button != 4  and self.f.direction_To_Guest==0 and Is_first_ball:#self.current_state !='near_distance_ball_approach_and_kick':
                Is_first_ball = False
                self.current_state = 'near_distance_omni_motion(400,0)'
                self.logger.info(f'1Go ---------------FF')
                Save_FWRD_params()
                self.motion.near_distance_omni_motion(338,0)

                self.motion.kick(first_Leg_Is_Right_Leg = False, small = True)
                self.motion.kick(first_Leg_Is_Right_Leg = False, small = True)

            if self.motion.falling_Flag != 0:                               # falling_Flag variable is used to with purpose to deliver
                                                                            # to strategy falling event or request to stop cycle. 
                                                                            # falling_Flag = 0 if nothing happened, = 1 если было падение на живот
                                                                            # =-1 падение на спину,= 2 падение на левый бок, 
                                                                            # = -2 падение на правый бок, = 3 запрос на остановку цикла.  
                if self.motion.falling_Flag == 3:
                    self.current_state = 'Initial_Pose'
                    self.motion.play_Soft_Motion_Slot(name = 'Initial_Pose')
                    break
                self.motion.falling_Flag = 0
                self.local.coordinate_fall_reset()                          # after falling localization must be blurered
            self.current_state = 'Initial_Pose'
            #обновляем координаты робота
            self.local.coordinate_record()
            #Если попали за ворота - выбираемся
            self.gate_escape(self.glob.pf_coord[0],self.glob.pf_coord[1])

            Save_FWRD_params()

            #Получение координат мяча от вратаря
            result,Is_old = GetTeammateParams(dir_path='Gk_sync')#Frwd_sync
            ball_coord,Gk_state = Get_ball_from_GK(result,Is_old)

            '''02.08'''
            move_side = Get_gk_coord_and_duty_dist(result,Is_old)
            if move_side:
                if self.glob.pf_coord[2]!=0:
                    self.motion.turn_To_Course(0) 
                    
                if self.glob.pf_coord[1] <=0:
                    #self.motion.near_distance_omni_motion(400,-1.57)
                    self.sidestep_test_main_cycle(2)
                    self.logger.info(f'Gk_Move_Back -отходим вправо')
                else:
                    self.sidestep_test_main_cycle(3)
                    #self.motion.near_distance_omni_motion(400,1.57)
                    self.logger.info(f'Gk_Move_Back -отходим влево')
            '''02.08'''
            

            Gk_cord = False
            Is_opponent_half = self.glob.pf_coord[0]>-0.6 or Gk_state == 'watch_Ball_In_Pose'
            if ball_coord!=None and self.current_state !='near_distance_ball_approach_and_kick' and Is_opponent_half:
               if ball_coord[0]<=-1.7 or ball_coord[0]>=1.7 or ball_coord[1]<=-1.4 or ball_coord[1]>=1.4 or (self.glob.pf_coord[0]<-0.6 and ball_coord[0]<self.glob.pf_coord[0]):
                   pass
               else:
                    Gk_cord = True
                    self.glob.ball_coord = ball_coord
                    self.logger.info(f'Gk_ball {round(ball_coord[0],2)},{round(ball_coord[1],2)}')
                    self.logger.info(f'Gk_State {Gk_state}')

            distance_to_ball = math.sqrt((self.glob.ball_coord[0]-self.glob.pf_coord[0])**2 + (self.glob.ball_coord[1]-self.glob.pf_coord[1])**2)
            dir_to_ball = self.motion.p.coord2yaw(self.glob.pf_coord[0] - self.glob.ball_coord[0],
                                                          self.glob.pf_coord[1] - self.glob.ball_coord[1]) - math.pi
            dir_to_ball = self.norm_yaw(dir_to_ball)
            #self.logger.info(f'2 Robot X {self.glob.pf_coord[0]}  Y {self.glob.pf_coord[1]}')
            #self.logger.info(f'2 Ball X {self.glob.ball_coord[0]}  Y {self.glob.ball_coord[1]}')
            # Получаем индекс сектора в котором по идее должен быть мяч
            self.start_segment_Viev = find_First_segment(self.glob.pf_coord[2],dir_to_ball, distance_to_ball)
            #self.logger.info(f'Robot dir {self.glob.pf_coord[2]}')
            #self.logger.info(f'ball dir {dir_to_ball}')
            #self.logger.info(f'to ball distance {distance_to_ball}')
            self.logger.info(f'Calc sector {self.start_segment_Viev}')
            
            if ball_coord!=None and self.current_state !='near_distance_ball_approach_and_kick' and Gk_cord:
                dist = distance_to_ball
                napravl = dir_to_ball
                start_segment_Viev = 2
                self.logger.info(f'Gk_ball  {round(ball_coord[0],2)},{round(ball_coord[1],2)} dist {round(dist,2)} ')
            else:
                success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = True,start_segment_Viev=self.start_segment_Viev)
                self.logger.info(f'Fwrd get dist {round(dist,2)}')

                
            
            #self.logger.info(f'distance = {dist} y- {self.glob.ball_coord[1]}  napravl ={napravl} x - {self.glob.ball_coord[0]} Code- {success_Code}')
            self.logger.debug( 'napravl =' + str(napravl) + ' dist = ' + str(dist) )
            #if self.glob.SIMULATION == 2 and self.glob.wifi_params['WIFI_IS_ON']: self.local.report_to_WIFI()  # telemetry for real robot 
                                                               # motion is ignored diring 10 seconds for non-kick-off player 
            self.f.dir_To_Guest()                                           # loading kick direction from strategy_data.json into self.f.direction_To_Guest
           
            self.logger.debug('direction_To_Guest = ' + str(math.degrees(self.f.direction_To_Guest)) + 'degrees')
            self.logger.debug('coord =' + str(self.glob.pf_coord) + ' ball =' + str(self.glob.ball_coord))
            if dist == 0 and success_Code == False: 
                self.logger.info(f'NOBALL')                        # condition when robot doesn't find ball 
                #self.motion.turn_To_Course(self.glob.pf_coord[2]+ 2 * math.pi / 3)  # robot turns to 1/3 of round from current orientation
#--------------------------------------------------------------------- 
                result,Is_old = GetTeammateParams(dir_path='Gk_sync')
                ball_coord,Gk_state = Get_ball_from_GK(result,Is_old)
                if ball_coord!=None:
                    self.current_state = 'forward far_distance_plan_approach'
                    self.logger.info('far_d_p_approach')
                    self.motion.far_distance_plan_approach(ball_coord, self.f.direction_To_Guest, stop_Over = True)        
                else: 
                    self.logger.info(f'Turn default')  
                    self.motion.turn_To_Course(self.glob.pf_coord[2]+ 2 * math.pi / 3) 

                continue 
#-------------------------------------------
            # following 4 operators detect is the player in fast kick position or is the player in front of ball
            # if player is in fast kick position then it proceed to near_distance_ball_approach_and_kick mandatory.
            # if player is in front of ball then it proceed to far_distance_plan_approach mandatory
            # if player isn't in fast kick position or isn't in front of ball then selection between near_distance_ball_approach_and_kick
            # or far_distance_plan_approach depends on distance to ball

            
            player_from_ball_yaw = self.motion.p.coord2yaw(self.glob.pf_coord[0] - self.glob.ball_coord[0],
                                                          self.glob.pf_coord[1] - self.glob.ball_coord[1]) - self.f.direction_To_Guest
            player_from_ball_yaw = self.norm_yaw(player_from_ball_yaw)
            player_in_front_of_ball = -math.pi/2 < player_from_ball_yaw < math.pi/2
            player_in_fast_kick_position = (player_from_ball_yaw > 2 or player_from_ball_yaw < -2) and dist < 0.6 

            
            if (dist > 0.35  or player_in_front_of_ball) and not player_in_fast_kick_position:
                if dist > 1: stop_Over = True
                else: stop_Over = False


                if False:#dist<=0.3 and success_Code : 
                    self.local.coordinate_record()
                    yaw =self.motion.p.coord2yaw(self.glob.pf_coord[0] - self.glob.ball_coord[0],
                                                                self.glob.pf_coord[1] - self.glob.ball_coord[1])- math.pi
                    yaw = self.norm_yaw(yaw)
                    self.logger.info(f'Dist = {dist*1000} Napravl = {yaw }')
                    if abs(self.glob.pf_coord[2]-yaw)>0.3:    
                        self.motion.turn_To_Course(yaw )
                    self.motion.near_distance_omni_motion(dist*1000-200,0 )
                    success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = True)
                    
                    if dist<=0.3 and success_Code :
                        num_Cycles,rotation = move_on_radius(dist,20,self.f.direction_To_Guest, self.glob.pf_coord[2])
                        if self.f.direction_To_Guest>self.glob.pf_coord[2]:
                                self.rotation_test_main_cycle(6,num_Cycles,rotation,5,20)
                                self.logger.info(f'Идем по дуге вправо')
                                if abs(self.glob.pf_coord[2]-self.f.direction_To_Guest)>0.1:
                                    self.motion.turn_To_Course(self.f.direction_To_Guest)
                                
                        elif self.f.direction_To_Guest<self.glob.pf_coord[2]:
                            self.rotation_test_main_cycle(5,num_Cycles,rotation,5,20)
                            self.logger.info(f'Идем по дуге влево')
                            if abs(self.glob.pf_coord[2]-self.f.direction_To_Guest)>0.1:
                                self.motion.turn_To_Course(self.f.direction_To_Guest)
                else:
                    self.current_state = 'forward far_distance_plan_approach'
                    Save_FWRD_params()
                    self.logger.info('forward far_distance_plan_approach')
                    '''
                    #попытка добавить условие на подход к мячу так чтобы перекрыть собой траекторию атаки мяча противником
                    if self.glob.ball_coord[0]<-0.1 and (self.glob.ball_coord[1]<-0.9 or self.glob.ball_coord[1]>0.9):
                        self.motion.far_distance_plan_approach(self.glob.ball_coord, 0, stop_Over = stop_Over)
                    '''
                    self.motion.far_distance_plan_approach(self.glob.ball_coord, self.f.direction_To_Guest, stop_Over = stop_Over)

                    
                continue
            self.motion.turn_To_Course(self.f.direction_To_Guest)
            small_kick = False
            if self.f.kick_Power > 1: small_kick = True
            self.current_state = 'near_distance_ball_approach_and_kick'
            Save_FWRD_params()
            self.logger.info('near_distance_ball_approach_and_kick')


            success_Code = self.motion.near_distance_ball_approach_and_kick(self.f.direction_To_Guest, strong_kick = False, small_kick = small_kick,start_segment_Viev = start_segment_Viev)
            
            

        

    def forward_old_style_main_cycle(self, pressed_button):
        """
        Main cycle method for 'forward_old_style' role of player.
        usage:
            self.forward_main_cycle(int: pressed_button)
        """
        
        second_player_timer = self.motion.game_time()                       # ignition of timer for non-kick-off forward player
        self.f = Forward(self.logger, self.motion, self.local, self.glob)
        
        while (True):
            if self.motion.falling_Flag != 0:                               # falling_Flag variable is used to with purpose to deliver
                                                                            # to strategy falling event or request to stop cycle. 
                                                                            # falling_Flag = 0 if nothing happened, = 1 if there was falling to stomach
                                                                            # =-1 if there was falling to back, = 2 if there was falling to left, 
                                                                            # = -2 if there was falling to right, = 3 if there was request to stop cycle.
                if self.motion.falling_Flag == 3: break
                self.motion.falling_Flag = 0
                self.local.coordinate_fall_reset()                          # after falling localization must be blurered
            success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = True,start_segment_Viev =2)
            self.logger.debug( 'napravl =' + str(napravl) + 'dist = ' + str(dist) )
            if pressed_button == 4 and (self.motion.game_time() - second_player_timer) < 10 : 
                continue                                                    # motion is ignored diring 10 seconds for non-kick-off player
            if dist == 0 and success_Code == False:                         # condition when robot doesn't find ball
                self.motion.turn_To_Course(self.glob.pf_coord[2]+ 2 * math.pi / 3)  # robot turns to 1/3 of round from current orientation
                continue
            if dist > 0.5  or self.glob.pf_coord[0] > self.glob.ball_coord[0] :
                self.motion.far_distance_ball_approach(self.glob.ball_coord)
                self.f.turn_Face_To_Guest()
                continue
            success_Code = self.motion.near_distance_ball_approach_and_kick(self.f.direction_To_Guest, strong_kick = False,start_segment_Viev=self.start_segment_Viev)


    def goalkeeper_main_cycle(self):        
        """
        Метод основного цикла вратаря основан на стратегии векторной матрицы. Вратарь не уходит от ворот слишком далеко.
        Предположим, что вратарь начинает игру в точке на середине линии ворот.
        Через 10 секунд после начала игры вратарь занимает дежурную позицию в зависимости от обнаруженного положения мяча.
        В случае, если мяч оказывается в опасной позиции, вратарь атакует мяч. 
        """
        def Save_GK_params(duty_direction = 0):
            create_json(dir_path='Gk_sync',ball_coord=[self.glob.ball_coord[0],self.glob.ball_coord[1]],
                            robot_coord=[self.glob.pf_coord[0],self.glob.pf_coord[1]],
                            robot_current_state=f'{self.current_state}',duty_direction = duty_direction)
            self.logger.info(f'Save_Gk at TIME {self.motion.game_time()}')
            self.logger.info(f'Ball {round(self.glob.ball_coord[0],2)} {round(self.glob.ball_coord[1],2)}')
            self.logger.info(f'Gk {round(self.glob.pf_coord[0],2)} {round(self.glob.pf_coord[1],2)}')
            self.logger.info(f'State {self.current_state}')

        def ball_position_is_dangerous(row, col):
            """
            Метод определяет, опасно ли положение мяча.
            Рискованная позиция квалифицируется, если мяч находится в ближайшей к автоголам трети поля по координате X.
            Из рискованных положений мяча исключаются угловые положения.
            Применение:
            bool: опасность = ball_position_is_dangerous (int: row, int: col)
            row - строка сектора поля по матрице
            col - столбец сектора поля по матрице
            """
            danger = False
            
            danger = (col <= (round(self.glob.COLUMNS / 3) - 1))#18 columns 13 rows
            if ((row <= (round(self.glob.ROWS / 3) - 1) or row >= round(self.glob.ROWS * 2 / 3)) and col == 0) or (col == 1 and (row == 0 or row == (self.glob.ROWS -1))):
               danger = False
            return danger
            
            '''
            #пытаемся ограничить выход вратаря за пределы вратарской вперед на 5 секторов влево право в пределах 7 центральных
            danger = (col <= (round(self.glob.COLUMNS/ 4) - 1))#18 columns 13 rows
            if ((row >= 3 or row <= 10) and col >=5) :
                danger = False
            return danger
            '''
        def Get_frwd_coord(result,Is_old):
            if not Is_old:
                if result!= None:
                    frwd_X = result['robot_coord']["X"]
                    frwd_Y = result['robot_coord']["Y"]
                    frwd_coord =[frwd_X,frwd_Y]
                    return  frwd_coord
            return None
        
        second_player_timer = self.motion.game_time()
        self.f = Forward_Vector_Matrix(self.logger, self.motion, self.local, self.glob)
        self.g = GoalKeeper(self.logger, self.motion, self.local, self.glob)
        #self.motion.near_distance_omni_motion(400, 0)                    # get out from goal
        fast_Reaction_On = True
        while (True):
#----------------------------------------------------------------------------------------------------------------!!!  
            start_segment_Viev = None          
            if self.motion.falling_Flag == 0:
                Save_GK_params()
                
                #self.logger.info(f'coordinate ball 0 = {self.glob.ball_coord[0]} coordinate ball 1 = {self.glob.ball_coord[1]}')
#----------------------------------------------------------------------------------------------------------------!!! 

            if self.motion.falling_Flag != 0:                               # falling_Flag variable is used to with purpose to deliver
                                                                            # to strategy falling event or request to stop cycle. 
                                                                            # falling_Flag = 0 if nothing happened, = 1 if there was falling to stomach
                                                                            # =-1 if there was falling to back, = 2 if there was falling to left, 
                                                                            # = -2 if there was falling to right, = 3 if there was request to stop cycle.                                                           
                if self.motion.falling_Flag == 3: break
                self.motion.falling_Flag = 0
                self.local.coordinate_fall_reset()
            if self.glob.ball_coord[0] <=1.2:# 0.15:
                success_Code, napravl, dist, speed =  self.motion.watch_Ball_In_Pose()                  # looks with increased attention
                self.current_state = 'watch_Ball_In_Pose'
                Save_GK_params()
            else:
                #-------------------------03.05.23 
                distance_to_ball = math.sqrt((self.glob.ball_coord[0]-self.glob.pf_coord[0])**2 + (self.glob.ball_coord[1]-self.glob.pf_coord[1])**2)
                #dir_to_ball = math.atan2((self.glob.ball_coord[1]-self.glob.pf_coord[1]), (self.glob.ball_coord[0]-self.glob.pf_coord[0]))
                dir_to_ball = self.motion.p.coord2yaw(self.glob.pf_coord[0] - self.glob.ball_coord[0],
                                                            self.glob.pf_coord[1] - self.glob.ball_coord[1])
                # Получаем индекс сектора в котором по идее должен быть мяч
                self.start_segment_Viev = find_First_segment(self.glob.pf_coord[2],dir_to_ball, distance_to_ball)
                self.logger.info(f'Robot dir {self.glob.pf_coord[2]}')
                self.logger.info(f'ball dir {dir_to_ball}')
                self.logger.info(f'to ball distance {distance_to_ball}')
                self.logger.info(f'Calc sector {self.start_segment_Viev}')
                #-----------------------------------------------------------------------03.05.23
                success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = fast_Reaction_On,start_segment_Viev=self.start_segment_Viev)#start_segment_Viev=2
                self.current_state = 'seek_Ball_In_Pose'
                Save_GK_params()
            if abs(speed[0]) > 0.02 and dist < 1.5 :                         # if dangerous tangential speed
                fast_Reaction_On = True
                print(f'Tang_Speed ={speed[0]}')
                #self.motion.play_Soft_Motion_Slot(name = 'PanaltyDefenceReady_Fast')
                self.motion.play_Soft_Motion_Slot(name ='PenaltyDefenceF')
                self.motion.pause_in_ms(2000)
                self.motion.play_Soft_Motion_Slot(name = 'Get_Up_From_Defence')
                continue
            #print(f'Speed ={speed[1]}')

            if speed[1] < - 0.015 and dist <1.1: #< 1.5 :                          # if dangerous front speed
                fast_Reaction_On = True
                print(f'Front_Speed ={speed[1]}')
                self.current_state = 'PenaltyDefenceF'
                #self.motion.play_Soft_Motion_Slot(name = 'PanaltyDefenceReady_Fast')    # preparing for splits
                self.current_state = 'PenaltyDefenceF'
                Save_GK_params()
                self.motion.play_Soft_Motion_Slot(name = 'PenaltyDefenceF')             # sit to splits
                self.motion.pause_in_ms(3000)#3000
                self.current_state = 'Get_Up_From_Defence'
                self.motion.play_Soft_Motion_Slot(name = 'Get_Up_From_Defence')
                continue
            if (self.motion.game_time() - second_player_timer) < 10 : continue
            row, col = self.f.dir_To_Guest()
            if dist == 0 and success_Code == False:                             # if ball was not detected at in viewable sectors
                #Брать координаты мяча из файла созданного роботом?
                self.current_state = 'goalkeeper turn_To_Course(pi*2/3)'
                self.logger.info('goalkeeper turn_To_Course(pi*2/3)')
                Save_GK_params()
                self.motion.turn_To_Course(self.glob.pf_coord[2]+ 2 * math.pi / 3)
                continue

            #Обновляем координаты робота
            self.local.coordinate_record()
            #Если попали за ворота - выбираемся
            self.gate_escape(self.glob.pf_coord[0],self.glob.pf_coord[1])

            if ball_position_is_dangerous(row, col):
                # attacking of ball
                fast_Reaction_On = True
                player_from_ball_yaw = self.motion.p.coord2yaw(self.glob.pf_coord[0] - self.glob.ball_coord[0], self.glob.pf_coord[1] - self.glob.ball_coord[1]) - self.f.direction_To_Guest
                player_from_ball_yaw = self.norm_yaw(player_from_ball_yaw)
                player_in_front_of_ball = -math.pi/2 < player_from_ball_yaw < math.pi/2
                player_in_fast_kick_position = (player_from_ball_yaw > 2 or player_from_ball_yaw < -2) and dist < 0.6 
                if (dist > 0.35  or player_in_front_of_ball) and not player_in_fast_kick_position:
                    if dist > 1: stop_Over = True
                    else: stop_Over = False
                    self.current_state = 'goalkeeper far_distance_plan_approach'
                    self.logger.info('goalkeeper far_distance_plan_approach')
                    Save_GK_params()

                    '''
                    Получаем координаты форварда.Если они актуальны b если форвард далее по х чем -0.2 м то идем прямо на мяч вратарем
                    
                    result,Is_old = GetTeammateParams(dir_path='Fwrd_sync')
                    frwd_coord = Get_frwd_coord(result,Is_old)
                    '''
                    if dist>0.3:#frwd_coord!=None and frwd_coord[0]>=-0.2: 
                        self.local.coordinate_record()
                        yaw =self.motion.p.coord2yaw(self.glob.pf_coord[0] - self.glob.ball_coord[0],
                                                                    self.glob.pf_coord[1] - self.glob.ball_coord[1])- math.pi
                        yaw = self.norm_yaw(yaw)
                        self.logger.info(f'Dist = {dist*1000} Napravl = {yaw }')
                        if abs(self.glob.pf_coord[2]-yaw)>0.1:    
                            self.motion.turn_To_Course(yaw)
                            
                        success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = True)

                        yaw =self.motion.p.coord2yaw(self.glob.pf_coord[0] - self.glob.ball_coord[0],
                                                                    self.glob.pf_coord[1] - self.glob.ball_coord[1])- math.pi
                        yaw = self.norm_yaw(yaw)
                        self.logger.info(f'Dist = {dist*1000} Napravl = {yaw }')
                            
                        if abs(self.glob.pf_coord[2]-yaw)>0.05:    
                            self.motion.turn_To_Course(yaw)
                        ball_in_our_half =False
                        ball_in_our_half = self.glob.ball_coord[0]<-0.5#  было -0.5

                        if success_Code and ball_in_our_half:
                            self.motion.near_distance_omni_motion(dist*1000-150,0 )
                        #success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = True)
                        
                        if success_Code and ball_in_our_half :
                            num_Cycles,rotation = self.move_on_radius(0.17,20,self.f.direction_To_Guest, self.glob.pf_coord[2])
                            if self.f.direction_To_Guest>self.glob.pf_coord[2]:
                                    self.rotation_test_main_cycle(6,num_Cycles-2,rotation,5,20)
                                    self.logger.info(f'Идем по дуге вправо')
                                    if abs(self.glob.pf_coord[2]-self.f.direction_To_Guest)>0.1:
                                        self.motion.turn_To_Course(self.f.direction_To_Guest)
                                    self.motion.near_distance_omni_motion(180,0 )
                                    
                            elif self.f.direction_To_Guest<self.glob.pf_coord[2]:
                                self.rotation_test_main_cycle(5,num_Cycles-2,rotation,5,20)
                                self.logger.info(f'Идем по дуге влево')
                                if abs(self.glob.pf_coord[2]-self.f.direction_To_Guest)>0.1:
                                    self.motion.turn_To_Course(self.f.direction_To_Guest)
                                self.motion.near_distance_omni_motion(180,0 )
                    else:
                        pass
                        #self.motion.far_distance_plan_approach(self.glob.ball_coord, self.f.direction_To_Guest, stop_Over = stop_Over) 
                    #self.f.turn_Face_To_Guest()

                    '''Закомментировано 02.08 в следствие чего вратарь после подхода к мячу по прямой и доворота на угол атаки
                    переходит в состояние - "approach_and_kick"
                    '''
                    #continue

                self.current_state = 'goalkeeper turn_To_Course(direction_To_Guest)'
                self.logger.info('goalkeeper turn_To_Course(direction_To_Guest)')

                '''Закомментировано 02.08 - отмена поворота в направлении угла атаки - поворот сделан ранее после подхода по дуге'''
                #self.motion.turn_To_Course(self.f.direction_To_Guest)

                small_kick = False
                if self.f.kick_Power > 1: small_kick = True
                self.current_state = 'goalkeeper near_distance_ball_approach_and_kick'
                self.logger.info('goalkeeper near_distance_ball_approach_and_kick')
                Save_GK_params()
               
                '''
                   Перед ударом вратарь вновь проверяет дистанцию и направление до/на мяч/а
                   и если они не удовлетворяют условиям ничего не делает!!
                '''
                if start_segment_Viev != None:
                    success_Code = self.motion.near_distance_ball_approach_and_kick(self.f.direction_To_Guest, strong_kick = False, small_kick = small_kick,start_segment_Viev=start_segment_Viev)
                else:
                    success_Code = self.motion.near_distance_ball_approach_and_kick(self.f.direction_To_Guest, strong_kick = False, small_kick = small_kick,start_segment_Viev=2)
            else:
                # returning to duty position
                fast_Reaction_On = False
                # bx = -0.5  dxp= -1.5
                duty_x_position =  min((-self.glob.landmarks['FIELD_LENGTH']/2 + 0.4),(self.glob.ball_coord[0]-self.glob.landmarks['FIELD_LENGTH']/2)/2)
                #dyp = 0.5*(-1.5+ 1.8)/(-0.5 +1.8) = 0.12

                duty_y_position = self.glob.ball_coord[1] * (duty_x_position + self.glob.landmarks['FIELD_LENGTH']/2) / (self.glob.ball_coord[0] + self.glob.landmarks['FIELD_LENGTH']/2) 
                if self.glob.ball_coord[1]>0.9:
                    duty_y_position+=0.08
                elif self.glob.ball_coord[1]<-0.9:
                    duty_y_position-=0.08

                duty_distance = math.sqrt((duty_x_position - self.glob.pf_coord[0])**2 + (duty_y_position - self.glob.pf_coord[1])**2)
                self.logger.debug('duty_x_position =' + str(duty_x_position) + ' duty_y_position =' + str(duty_y_position))
                if duty_distance < 0.05 : continue
                elif duty_distance <  3:# and abs(self.glob.pf_coord[1]-self.glob.ball_coord[1])>0.4: #   0.6 :
                    self.current_state = 'goalkeeper turn_To_Course(0)'
                    Save_GK_params(duty_direction=0)
                    self.logger.info('goalkeeper turn_To_Course(0)')
                    self.motion.turn_To_Course(0)
                    duty_direction = self.motion.p.coord2yaw(duty_x_position - self.glob.pf_coord[0], duty_y_position - self.glob.pf_coord[1]) 
                    self.current_state = 'goalkeeper near_distance_omni_motion'
                    self.logger.info(f'omni_motion Direction - {duty_direction}')

                    #Save_GK_params(duty_direction=duty_direction)

                    self.motion.near_distance_omni_motion(duty_distance * 1000, duty_direction)
                    self.current_state = 'goalkeeper turn_To_Course(0)'
                    self.logger.info('goalkeeper turn_To_Course(0)')
                    self.motion.turn_To_Course(0)
                else:
                    self.motion.far_distance_plan_approach([duty_x_position + 0.25, duty_y_position], 0, stop_Over = False)
                    

        self.current_state = 'Initial_Pose'
        Save_GK_params()
        self.motion.play_Soft_Motion_Slot(name = 'Initial_Pose')
        

    def goalkeeper_old_style_main_cycle(self):
        """
        main cycle for old style goalkeeper strategy
        """
        start_segment_Viev =2
        self.motion.near_distance_omni_motion(200, 0)                    # get out from goal line
        self.g = GoalKeeper(self.logger, self.motion, self.local, self.glob)
        while (True):
            dist = -1.0
            if self.motion.falling_Flag != 0:                               # falling_Flag variable is used to with purpose to deliver
                                                                            # to strategy falling event or request to stop cycle. 
                                                                            # falling_Flag = 0 if nothing happened, = 1 if there was falling to stomach
                                                                            # =-1 if there was falling to back, = 2 if there was falling to left, 
                                                                            # = -2 if there was falling to right, = 3 if there was request to stop cycle.
                if self.motion.falling_Flag == 3: break
                self.motion.falling_Flag = 0
                self.local.coordinate_fall_reset()
                self.g.turn_Face_To_Guest()
            while(dist < 0):
                a, dist,napravl, speed = self.g.find_Ball()
                self.logger.debug('speed = ' + str(speed) + ' dist  =' + str(dist) + ' napravl =' + str(napravl))
                if abs(speed[0]) > 0.02 and dist < 1 :                         # if dangerous tangential speed
                    if speed[0] > 0:
                        if self.glob.pf_coord[1] < 0.35:
                            self.motion.play_Soft_Motion_Slot(name ='PenaltyDefenceL')
                    else:
                        if self.glob.pf_coord[1] > -0.35:
                            self.motion.play_Soft_Motion_Slot(name ='PenaltyDefenceR')
                    if self.glob.SIMULATION == 2: pyb.delay(3000)
                    else: self.motion.sim_Progress(3)
                    continue
                if speed[1] < - 0.01 and dist < 1.5 :                          # if dangerous front speed
                    self.motion.play_Soft_Motion_Slot(name = 'PanaltyDefenceReady_Fast')
                    self.motion.play_Soft_Motion_Slot(name = 'PenaltyDefenceF')
                    if self.glob.SIMULATION == 2: pyb.delay(8000)
                    else: self.motion.sim_Progress(3)
                    self.motion.play_Soft_Motion_Slot(name = 'Get_Up_From_Defence')

                if (dist == 0 and napravl == 0) or dist > 2.5:
                    position_limit_x1 = -self.glob.landmarks['FIELD_LENGTH']/2 - 0.05
                    position_limit_x2 = position_limit_x1 + 0.25
                    if position_limit_x1 < self.glob.pf_coord[0] < position_limit_x2 and -0.05 < self.glob.pf_coord[1] < 0.05: break
                    self.g.goto_Center()
                    break
                old_neck_pan, old_neck_tilt = self.motion.head_Up()
                if (dist <= 0.7         and 0 <= napravl <= math.pi/4):         self.g.scenario_A1( dist, napravl)
                if (dist <= 0.7         and math.pi/4 < napravl <= math.pi/2):  self.g.scenario_A2( dist, napravl)
                if (dist <= 0.7         and 0 >= napravl >= -math.pi/4):        self.g.scenario_A3( dist, napravl)
                if (dist <= 0.7         and -math.pi/4 > napravl >= -math.pi/2): self.g.scenario_A4( dist, napravl)
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (math.pi/18 <= napravl <= math.pi/4)): self.g.scenario_B1()
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (math.pi/4 < napravl <= math.pi/2)): self.g.scenario_B2()
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (-math.pi/18 >= napravl >= -math.pi/4)): self.g.scenario_B3()
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (-math.pi/4 > napravl >= -math.pi/2)): self.g.scenario_B4()

    def penalty_Shooter_main_cycle(self):
        """
        main cycle for penalty striker 
        """
        start_segment_Viev =2
        self.f = Forward(self.logger, self.motion, self.local, self.glob)
        while (True):
            if self.motion.falling_Flag != 0:
                if self.motion.falling_Flag == 3: break
                self.motion.falling_Flag = 0
                self.local.coordinate_fall_reset()
            success_Code, napravl, dist, speed,start_segment_Viev = self.motion.seek_Ball_In_Pose(fast_Reaction_On = True,start_segment_Viev=2)
            self.f.dir_To_Guest()
            self.logger.debug('ball_coord = ' + str(self.glob.ball_coord))
            self.logger.debug('direction_To_Guest = ' + str(math.degrees(self.f.direction_To_Guest)) + 'degrees')
            if dist == 0 and success_Code == False:
                self.motion.turn_To_Course(self.glob.pf_coord[2]+ 2 * math.pi / 3)
                continue
            if dist > 0.35 or self.glob.pf_coord[0] - 0.2 > self.glob.ball_coord[0]:
                if dist > 1: stop_Over = True
                else: stop_Over = False
                self.motion.far_distance_plan_approach(self.glob.ball_coord, self.f.direction_To_Guest, stop_Over = stop_Over)
            kick_direction = self.f.direction_To_Guest
            self.motion.turn_To_Course(kick_direction)
            success_Code = self.motion.near_distance_ball_approach_and_kick(self.f.direction_To_Guest, strong_kick = False,start_segment_Viev=self.start_segment_Viev,dist_correct=30)
            self.motion.near_distance_omni_motion(400,0)

    def penalty_Goalkeeper_main_cycle(self):
        self.g = GoalKeeper(self.logger, self.motion, self.local, self.glob)
        self.glob.obstacleAvoidanceIsOn = False
        first_Get_Up = True
        while (True):
            dist = -1.0
            if self.motion.falling_Flag != 0:
                if self.motion.falling_Flag == 3: break
                self.motion.falling_Flag = 0
                self.local.coordinate_fall_reset()
                self.g.turn_Face_To_Guest()
                if first_Get_Up:
                    first_Get_Up = False
                    self.g.goto_Center()
            while(dist < 0):
                a, napravl, dist, speed = self.motion.watch_Ball_In_Pose(penalty_Goalkeeper = True)
                self.logger.debug('speed = ' + str(speed) + 'dist  =' + str(dist) + 'napravl =' + str(napravl))
                if abs(speed[0]) > 0.004 and dist < 1 :                         # if dangerous tangential speed

                    #self.motion.play_Soft_Motion_Slot(name = 'PanaltyDefenceReady_Fast')
                    self.motion.play_Soft_Motion_Slot(name ='PenaltyDefenceF')
                    self.motion.pause_in_ms(2000)
                    self.motion.play_Soft_Motion_Slot(name = 'Get_Up_From_Defence')

                    
                    continue
                if speed[1] < - 0.03 and dist < 1.5 :                          # if dangerous front speed
                    #self.motion.play_Soft_Motion_Slot(name = 'PanaltyDefenceReady_Fast')
                    self.motion.play_Soft_Motion_Slot(name = 'PenaltyDefenceF')
                    self.motion.pause_in_ms(2000)
                    self.motion.play_Soft_Motion_Slot(name = 'Get_Up_From_Defence')

                if (dist == 0 and napravl == 0) or dist > 2.5:
                    continue
                old_neck_pan, old_neck_tilt = self.motion.head_Up()
                if (dist <= 0.7         and 0 <= napravl <= math.pi/4):         self.g.scenario_A1( dist, napravl)
                if (dist <= 0.7         and math.pi/4 < napravl <= math.pi/2):  self.g.scenario_A2( dist, napravl)
                if (dist <= 0.7         and 0 >= napravl >= -math.pi/4):        self.g.scenario_A3( dist, napravl)
                if (dist <= 0.7         and -math.pi/4 > napravl >= -math.pi/2): self.g.scenario_A4( dist, napravl)
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (math.pi/18 <= napravl <= math.pi/4)): self.g.scenario_B1()
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (math.pi/4 < napravl <= math.pi/2)): self.g.scenario_B2()
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (-math.pi/18 >= napravl >= -math.pi/4)): self.g.scenario_B3()
                if ((0.7 < dist < self.glob.landmarks['FIELD_LENGTH']/2) and (-math.pi/4 > napravl >= -math.pi/2)): self.g.scenario_B4()
                self.motion.head_Return(old_neck_pan, old_neck_tilt)

    def dance_main_cycle(self):
        if self.glob.SIMULATION == 2:
            while True:
                successCode, u10 = self.motion.kondo.getUserParameter(10)
                #time.sleep(2)
                if successCode and u10 == 1:
                    self.motion.kondo.motionPlay(26)
                    for i in range(10):
                        self.motion.play_Soft_Motion_Slot( name = 'Dance_6_1')
                    self.motion.play_Soft_Motion_Slot( name = 'Dance_7-1')
                    self.motion.play_Soft_Motion_Slot( name = 'Dance_7-2')
                    for i in range(9):
                        self.motion.play_Soft_Motion_Slot( name = 'Dance_6_1')
                    self.motion.play_Soft_Motion_Slot( name = 'Dance_2')
                    for i in range(2):
                        self.motion.play_Soft_Motion_Slot( name = 'Dance_6_1')
                    self.motion.play_Soft_Motion_Slot( name = 'Dance_4')
                    self.motion.kondo.setUserParameter(10,0)
        else:
            #for i in range(10):
            #    self.motion.play_Soft_Motion_Slot( name = 'Dance_6_1')
            self.motion.play_Soft_Motion_Slot( name = 'Dance_7')
            self.motion.play_Soft_Motion_Slot( name = 'Dance_2')
            self.motion.play_Soft_Motion_Slot( name = 'Dance_4')


if __name__=="__main__":
    pass