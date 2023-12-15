'''
Стэйты голкипера
    'PenaltyDefenceL' - падает влево защищая ворота
    'PenaltyDefenceR' - падает вправо защищая ворота
    'PenaltyDefenceF' - садится на шпагат защищая ворота и затем падает на спину
    'Get_Up_From_Defence' - встает после защиты 
    'goalkeeper turn_To_Course(pi*2/3)' - не видит мяч 
    'goalkeeper far_distance_plan_approach' - подходит к мячу из далека
    'goalkeeper turn_To_Course(direction_To_Guest)' - поварачивается в направлении
    'goalkeeper near_distance_ball_approach_and_kick' - находясь вблизи мяча сокращает дистанцию и готовится ударить мяч
    'goalkeeper turn_To_Course(0)' - поворачивается лицом к воротам соперника
!!'goalkeeper near_distance_omni_motion' -!! УТОЧНИТЬ!! всенаправленное движение на ближнем расстоянии !! Уточнить 
    'Initial_Pose' - осматривается в поиске мяча: после падения; в начале игры...
'''
from My_Tests.GetBall_XY_from_txt import GetTeammateParams
#
def What_I_do():
    '''
       Вызываем эту функцию из strategy.py  и главного цикла нападающего 
       перед тем как нападающий соберется что-то сделать
       например : если собирается идти к мячу, а голкипер уже идет к нему,
       то лучше подождать некоторое время или переключиться на другую задачу. 
    '''
    result,Is_Old = GetTeammateParams(dir_path='Gk_sync')
    #print(result)
    doing =''
    if result["robot_current_state"] == 'goalkeeper near_distance_ball_approach_and_kick' or result["robot_current_state"] == 'goalkeeper far_distance_plan_approach': 
        doing = 'wait 8'
        print(f'GK -> {result["robot_current_state"]}')
        
    return doing,result

print(What_I_do())
