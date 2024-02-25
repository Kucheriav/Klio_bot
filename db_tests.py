from db_functions import *


def add_test_data(session):
    with open('test_data.txt', encoding='utf8') as file:
        new_excursions, open_visits = file.read().split('-#-')
        new_excursions = [list(filter(lambda x: len(x), exc.split('\n'))) for exc in new_excursions.split('@')]
        new_excursions = [list(map(lambda x: x.split(': ')[1], exc)) for exc in new_excursions]
        open_visits = list(map(lambda x: x.split(), open_visits.split('-')))
    for excursion in new_excursions:
        session.add(Excursion(title=excursion[0], description=excursion[2], duration=excursion[1].split()[0]))
    for visit in open_visits:
        session.add(Schedule(excursion_id=int(visit[0]), date_time=datetime.strptime(visit[1], '%d.%m.%Y')))

    session.commit()

def add_test_admin_users(session):
    with open('test_users.txt', encoding='utf8') as file:
        users = [dict(map(lambda x: x.split('='), x)) for x in map(lambda x: x.strip().split('\n'), file.read().split('\n-#-\n'))]
    for user in users:
        session.add(User(name=user['name'], link=user['link'], tg_id=int(user['tg_id']), is_admin=bool(int(user['is_admin']))))
    session.commit()


def singing_to_visit():
    id = '1'
    contact_link = 'my_user1'
    contact_name = 'Посетитель1'
    number = '6'
    visit_info = [id, contact_link, contact_name, number]
    return visit_info

def straight_choosing_scenario():
    session, engine = database_init()
    r = get_current_excursions_ids_and_names(session)
    print(*r, sep='\n')
    title = 'Фронтовая посуда'
    print(f'Выбрано: {title}')
    s = get_actual_dates_by_name(session, title)
    print(*map(lambda x: x.strftime("%d.%m.%Y"), s), sep='\n')
    date_time = datetime.strptime('22.05.2024', '%d.%m.%Y')
    print(f'Выбрано: {date_time}')
    this_id = window_id_by_title_and_date(session, title, date_time)
    print('this_id', this_id)
    res = add_visit_into_window(session, singing_to_visit())
    print(res)
    bb = get_all_windows(session)
    print(*bb, sep='\n')

def drop_db_scenario():
    session, engine = recreate_db()
    add_test_data(session)
    add_test_admin_users(session)
    print(*get_all_users(session))


def normal_init():
    session, engine = database_init()
    print(get_windows_ids_and_dates_by_excursion_id(session, 1))


if __name__ == '__main__':
    normal_init()




