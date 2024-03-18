from db_functions import *
from csv import reader, writer


def read_excursion(session=None, filename='excursion_data_1803.csv'):
    with open(filename) as file:
        data = reader(file, delimiter=';')
        next(data)
        for line in data:
            # print(line)
            title, date, time = map(lambda x: x.strip(), line)
            excursion_id = get_excurions_id_by_title(session, title)
            print(excursion_id)
    # with open('test_data.txt', encoding='utf8') as file:
    #     new_excursions, open_visits = file.read().split('-#-')
    #     new_excursions = [list(filter(lambda x: len(x), exc.split('\n'))) for exc in new_excursions.split('@')]
    #     new_excursions = [list(map(lambda x: x.split(': ')[1], exc)) for exc in new_excursions]
    #     open_visits = list(map(lambda x: x.strip().split('\n'), open_visits.split('-')))
    # for excursion in new_excursions:
    #     session.add(Excursion(title=excursion[0], description=excursion[2], duration=excursion[1].split()[0]))
    # for visit in open_visits:
    #     session.add(Schedule(excursion_id=int(visit[0]), date_time=datetime.strptime(visit[1], '%d.%m.%Y %H:%M')))
    #
    # session.commit()

if __name__ == '__main__':
    read_excursion()