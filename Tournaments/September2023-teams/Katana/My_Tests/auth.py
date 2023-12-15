# import shutil
# for i in range(2):

#     shutil.copy2("E:\\Elsiros\\controllers\\School_8 main 2607\\output7001.txt", f"E:\\Elsiros\\Logs\\red_team_2607\\{i}_output7001.txt")
#     shutil.copy2("E:\\Elsiros\\controllers\\School_8 main 2607\\output7002.txt", f"E:\\Elsiros\\Logs\\red_team_2607\\{i}_output7002.txt")
#     shutil.copy2("E:\\Elsiros\\controllers\\School_8 main 2607 clone\\output7021.txt", f"E:\\Elsiros\\Logs\\blue_team_2607_clone\\{i}_output7021.txt")
#     shutil.copy2("E:\\Elsiros\\controllers\\School_8 main 2607 clone\\output7022.txt", f"E:\\Elsiros\\Logs\\blue_team_2607_clone\\{i}_output7022.txt")

#print(2*2**2*2)

# s1 = "Картофель"
# s2 = "Морковь"
# s3 = "ВСЕГО:"
# s4 = "кг"    
# a = 12
# b = 3
# s = s1+"      "+str(a)+" "+s4+'\n' +s2+"         "+str(b)+" "+s4 +'\n'+"--------------------"+ '\n' +s3 +"         "+str(a+b)+" "+s4

# print(s)


# num_a = int(input())
# num_b = int(input())

# print(num_a*num_b,round((num_a*num_b)/num_b))



# number = 473054
# index = int(input())

# str_num =str(number)

# digit = int(str_num[index - 1])
# print(digit)


# while True:
#     number = int(input())
#     if number % 2 == 0:
#         print("Вы ввели правильное число")
#         break
#     else:
#         print("Ошибка. Повторите ввод.")


# number = int(input())

# if number % 13 == 0:
#     print("Делится на 13")
# else:
#     print("Не делится на 13")


# original_string = 'ABCDEFGHIJ'
# result_string = ''

# inverted_string = original_string[::-1]  

# for char in inverted_string:
#     if char in 'JHFDB':
#         result_string += char

# print(result_string)


# sequence = [1, 10, 6, 4, 2, 7, 10, 2, 7, 10]

# for i, num in enumerate(sequence):
#     if num % 2 == 0:
#         print("Чётное", end="")
#     else:
#         print("Нечётное", end="")

#     if i < len(sequence) - 1:
#         if (num % 2 == 0 and sequence[i + 1] % 2 != 0) or (num % 2 != 0 and sequence[i + 1] % 2 == 0):
#             print(", ")
#         else:
#             print(", ", end="")


# s = "ABBBAAAAABBBBABBAAABBBBABAA"
# w = s.split("AA")
# print(len(w))
# print(w)



# s = 'ABCDEFGHIJKL'
# result = s[-1:-8:-3]
# print(result)


# char1 = input()
# char2 = input()

# num1 = ord(char1)
# num2 = ord(char2)

# for num in range(num1, num2 + 1):
#     print(chr(num), end="")

# import string
# alphabet = string.ascii_uppercase

# char = input().upper()

# if char in alphabet:
#     index = alphabet.index(char)
#     print(index)



# input_string = input()
# unique_characters = set(input_string)
# sorted_characters = sorted(unique_characters)
# print(sorted_characters)

# d1 = {1: 10, 2: 20} 
# d2 = {3: 30, 4: 40}
# d1.update(d2)
# print(d1)

# a = {1: None, 2: "A", 3: 'B', 4: None, 5: 'C'}
# a[1] = D
# print(a)



def odd_even(number):
    if number % 2 == 0:
        return 'Чётное'
    else:
        return 'Нечётное'

input_number = int(input())
result = odd_even(input_number)
print(result)


