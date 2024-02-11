from db_functions import *


def singing_to_visit():
    id = '1'
    contact_link = 'my_user1'
    contact_name = 'Посетитель1'
    number = '6'
    visit_info = [id, contact_link, contact_name, number]
    return visit_info

def straight_choosing_scenario():
    session, engine = database_init()
    r = get_current_windows_names(session)
    print(*r, sep='\n')
    title = 'Фронтовая посуда'
    print(f'Выбрано: {title}')
    s = get_actual_dates_by_name(session, title)
    print(*map(lambda x: x.strftime("%d.%m.%Y"), s), sep='\n')
    date_time = datetime.strptime('22.05.2024', '%d.%m.%Y')
    print(f'Выбрано: {date_time}')
    this_id = window_id_by_title_and_date(session, title, date_time)
    print('this_id', this_id)
    res = add_visit(session, singing_to_visit())
    print(res)
    bb = get_all_windows(session)
    print(*bb, sep='\n')

def drop_db_scenario():
    session, engine = recreate_db()
    add_test_data_classes(session)

if __name__ == '__main__':
    drop_db_scenario()
    straight_choosing_scenario()

