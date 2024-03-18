from db_functions import *
from csv import reader, writer
from datetime import datetime

def read_windows(session=None, filename='window_data_1803.csv'):
    new_windows = list()
    with open(filename) as file:
        data = reader(file, delimiter=';')
        next(data)
        for line in data:
            title, date, time = map(lambda x: x.strip(), line)
            excursion_id = get_excursions_id_by_title(session, title)
            if excursion_id[0] is False:
                print('There is no such an excursion in DB:', title)
                continue
            if (a := check_date(f'{date} {time}')) != 'ok':
                print(a, f'{date} {time}')
                continue
            date_split = list(map(int, date.split('.')))
            time_split = list(map(int, time.split(':')))
            try:
                window = Window(excursion_id=excursion_id[1], date_time=datetime(
                    year=date_split[2], month=date_split[1], day=date_split[0], hour=time_split[0], minute=time_split[1]))
            except Exception as e:
                print(f"{type(e).__name__}: {str(e)}")
                continue
            else:
                new_windows.append(window)
    # print(*new_windows, sep='\n')
    session.add_all(new_windows)
    session.commit()


def read_excursions(session=None, filename='excursion_data_1803.csv'):
    new_excursions = list()
    with open(filename) as file:
        data = reader(file, delimiter=';')
        next(data)
        for line in data:
            if sum(map(len, line)) < 10:
                continue
            title, duration, description = map(lambda x: x.strip(), line)
            excursion = Excursion(title=title, duration=duration, description=description)
            new_excursions.append(excursion)
    session.add_all(new_excursions)
    session.commit()


if __name__ == '__main__':
    pass