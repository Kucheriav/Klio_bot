from db_functions import *


def adding_excursion_handler():
    print('Режим добавления экскурсий')
    while True:
        title = input('Введите название экскурсии: ')
        description = input('Введите описание экскурсии: ')
        duration = input('Введите продолжительность экскурсии, минут: ')
        print('Эти данные верны?')
        print(f'Название {title}\nОписание {description}\nПродолжительность {duration} минут')
        print('Д/Н ?')
        answ = input().lower()
        if answ == 'д':
            break
        else:
            print('Введем заново')
    add_new_excursion(title, description, duration)

def adding_vitis_handler():
    print('Режим добавления посещений')
    result = get_excursions()
    for res in result:
        print(*res)
    while True:
        n = input('Введите номер экскурсии: ')
        if n in map(lambda x: str(x[0]), result):
            break
        else:
            print('Неправильный ввод. Попробуйте еще раз')
    while True:
        try:
            date = input('Введите дату в формате дд.мм.гггг ')
            day, month, year = date.split('.')
            time = input('Введите время в формате чч:мм ')
            hours, minutes = time.split(':')
            title = list(map(lambda x: x[1], result))[int(n) - 1]
            print('Эти данные верны?')
            print(f'Экскурсия {title} состоится {day}.{month}.{year} в {hours}:{minutes}')
            print('Д/Н ?')
            answ = input().lower()
            if answ == 'д':
                break
            else:
                print('Введем заново')
        except:
            print('Неправильный ввод. Попробуйте еще раз')
    add_new_visits_time(n, year, month, day, hours, minutes)


def accepting_visits_handler():
    print('Режим записи на посещение')
