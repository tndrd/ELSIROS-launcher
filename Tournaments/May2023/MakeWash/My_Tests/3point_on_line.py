
# x1= -20
# y1= 20
# x2= 45
# y2= -25
# x3= 20
# y3= -15
# distance = 10

'''
Проверяем находятся ли координаты (х3,y3) между точек с (x1-y1) (x2-y2)
и находится ли третья точка на расстоянии не более distance от прямой соединяющей две другие
'''

def is_within_distance(x1, y1, x2, y2, x3, y3, distance):
    three_beetwin_1_2 =False
    three_touch_line_1_2 = False
    if abs(x1-x2)> abs(x1-x3) and  abs(y1-y2)>abs(y1-y3) and ((x1<x3<x2  and  y1<y3<y2) or (x1<x3<x2  and  y1>y3>y2) or (x1>x3>x2 and y1<y3<y2) or (x1>x3>x2 and y1>y3>y2) ):
        print('Точка 3 между 1 и 2') 
        three_beetwin_1_2 = True
    else:
        print('Точка 3 НЕ между 1 и 2')
        three_beetwin_1_2 = False
 
    d = abs((y2 - y1) * x3 - (x2 - x1) * y3 + x2 * y1 - y2 * x1) / ((y2 - y1)**2 + (x2 - x1)**2)**0.5
    if d <= distance:
        three_touch_line_1_2 = True
    else:
        three_touch_line_1_2 = False
    return three_touch_line_1_2 and three_beetwin_1_2

#print(is_within_distance(x1, y1, x2, y2, x3, y3, distance))