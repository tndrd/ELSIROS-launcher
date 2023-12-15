import os
def find_goal_remaining_time_pairs(lines):
    goal_lines = [line for line in lines if 'goal' in line]
    remaining_time_lines = [line for line in lines if 'remaining time:' in line]
    pairs = {}
    
    for goal_line in goal_lines:
        goal_index = lines.index(goal_line)
        min_index_diff = float('inf')
        closest_remaining_time_line = ''
        for remaining_time_line in remaining_time_lines:
            remaining_time_index = lines.index(remaining_time_line)
            index_diff = abs(remaining_time_index - goal_index)
            if index_diff < min_index_diff:
                min_index_diff = index_diff
                closest_remaining_time_line = remaining_time_line
        pairs[goal_line] = closest_remaining_time_line
    # путь к директории с файлами
    path = "My_Tests\\logs_parse"
    # создаем список пар и время
    pairs_with_time = []
    for goal_line, time_line in zip(goal_lines, remaining_time_lines):
        pairs_with_time.append((goal_line, time_line))
    
    # сохраняем список пар и время в txt файл
    filename = "pairs_with_time.txt"
    filepath = os.path.join(path, filename)
    with open(filepath, "w") as f:
        for pair in pairs_with_time:
            f.write(f"{pair[0]} {pair[1]}\n")
        
    return pairs
dir_to_log_file = "E:\\Elsiros\\controllers\\referee\\log.txt"    
with open(f'{dir_to_log_file}', 'r') as f:
    lines = f.readlines()
    pairs = find_goal_remaining_time_pairs(lines)
    print(pairs)






