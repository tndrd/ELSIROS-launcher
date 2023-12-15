def sort_list(list,start_value):
    # Находим индекс стартового элемента
    start_idx = list.index(start_value)
    print(f'Смотрим на сегмент № {start_value}')
    if start_value!=2:
        del list [-1]
    # Переносим элементы перед стартовым индексом в конец списка
    list = list[start_idx:] + list[:start_idx]

    # Проходим по списку, начиная со следующего за стартовым элемента
    for i in range(start_idx+1, len(list)):
        if list[i] == 0:
            break  # Заканчиваем цикл, если достигли элемента со значением 0
    #     print(list[i])
    # print(list)
    return list

#print(sort_list([2,7,12,11,6,8,13,14,9,4,3,10,5,0,1,2],3))