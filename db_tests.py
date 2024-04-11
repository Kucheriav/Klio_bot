from db_functions import *
from data_reader import *
from data_writer import *

@database_session
def add_test_data(session):
    with open('test_data.txt', encoding='utf8') as file:
        new_excursions, open_visits = file.read().split('-#-')
        new_excursions = [list(filter(lambda x: len(x), exc.split('\n'))) for exc in new_excursions.split('@')]
        new_excursions = [list(map(lambda x: x.split(': ')[1], exc)) for exc in new_excursions]
        open_visits = list(map(lambda x: x.strip().split('\n'), open_visits.split('-')))
    for excursion in new_excursions:
        session.add(Excursion(title=excursion[0], description=excursion[2], duration=excursion[1].split()[0]))
    for visit in open_visits:
        session.add(Window(excursion_id=int(visit[0]), date_time=datetime.strptime(visit[1], '%d.%m.%Y %H:%M')))

    session.commit()


@database_session
def add_test_admin_users(session):
    with open('test_users.txt', encoding='utf8') as file:
        users = [dict(map(lambda x: x.split('='), x)) for x in map(lambda x: x.strip().split('\n'), file.read().split('\n-#-\n'))]
    for user in users:
        session.add(User(name=user['name'], link=user['link'], tg_user_id=int(user['tg_id']),
                         is_admin=bool(int(user['is_admin'])), is_tracking_events=False))
    session.commit()


def drop_db_scenario():
    recreate_db()
    add_test_data()
    add_test_admin_users()
    print(*get_all_users(), sep='\n\n')


def normal_init():
    database_init()
    print(*get_all_users(), sep='\n\n')


def reading_from_csv():
    recreate_db()
    read_excursions()
    print(*get_all_excursions(), sep='\n\n')
    read_windows()
    print(*get_all_windows(), sep='\n\n')
    add_test_admin_users()


def write_to_csv():
    # write_excursions_to_file()
    write_windows_to_file()


if __name__ == '__main__':
    write_to_csv()





