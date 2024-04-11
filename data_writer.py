from db_functions import *
from csv import writer
from datetime import datetime


@database_session
def write_excursions_to_file(session):
    filename = f"server_excursion_data_{datetime.strftime(datetime.now(), '%d%m')}.csv"
    excursions = get_all_excursions()
    with open(filename, 'w') as file:
        my_writer = writer(file, delimiter=';', lineterminator='\n')
        my_writer.writerow(['Название', 'Описание', 'Продолжительность'])
        for excursion in excursions:
            my_writer.writerow([excursion.title, excursion.description, excursion.duration])


@database_session
def write_windows_to_file(session):
    filename = f"server_windows_data_{datetime.strftime(datetime.now(), '%d%m')}.csv"
    windows = list(map(lambda x: [x[0]] + [datetime.strftime(x[1], '%d.%m.%Y %H:%M')] + [*x[2:]], get_all_windows()))
    with open(filename, 'w') as file:
        my_writer = writer(file, delimiter=';', lineterminator='\n')
        my_writer.writerow(['Название', 'Дата время', 'Ссылка', 'Имя', 'Кол-во участников'])
        for window in windows:
            my_writer.writerow(window)