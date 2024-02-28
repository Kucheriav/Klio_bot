from db_models import *
from db_config_reader import read_config
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from errors import *
from datetime import datetime



### системные функции
def database_init():
    configs = read_config(filename='config.ini', section='mysql')
    url = "mysql://%(user)s:%(password)s@%(host)s/%(db)s" % {
        'user': configs['user'],
        'password': configs['password'],
        'host': configs['host'],
        'db': configs['database']
    }
    engine = create_engine(url)
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    return session, engine


def recreate_db():
    session, engine = database_init()
    drop_database(engine.url)
    session, engine = database_init()
    return session, engine

def check_date(date):
    try:
        d = datetime.strptime(date, '%d.%m.%Y')
    except ValueError as ex:
        return 'Некорректный формат даты! Пример верного: 05.05.2055'
    if d < datetime.now():
        return 'Этот день уже прошел'
    return 'ok'



### общие функции
def get_all_excursions(session):
    data = session.query(Excursion).all()
    return data


def get_all_windows(session):
    data = session.query(Schedule).all()
    return data


def get_all_users(session):
    data = session.query(User).all()
    return data


def get_admins_ids_names_dict(session):
    data = session.query(User.tg_id, User.name).filter(User.is_admin==True).all()
    return {x[0]: x[1] for x in data}


def get_this_window(session, this_id) -> Schedule:
    data = session.query(Schedule).filter(Schedule.id == this_id).one()
    return data


### пользовательские функции
## начало ветки записи на посещение
def get_current_excursions_ids_and_names(session):
    current_excursions_ids_and_names = (session.query(Excursion.id, Excursion.title).join(Schedule).
            filter(Schedule.contact_link == '', Schedule.date_time >= datetime.now()).all())
    return set(current_excursions_ids_and_names)


#not used with next function
def get_description_by_title(session, title):
    description = session.query(Excursion.description).filter(Excursion.title == title).one()[0]
    return description


def get_excursion_info_by_id(session, id):
    excursion_info = session.query(Excursion.title, Excursion.description, Excursion.duration).filter(Excursion.id == id).one()
    return excursion_info


#not used with next function
def get_actual_dates_by_name(session, title):
    dates = session.query(Schedule.date_time).join(Excursion).filter(Excursion.title == title,
                                            Schedule.contact_link == '', Schedule.date_time >= datetime.now()).all()
    dates = [x[0] for x in dates]
    return dates


def get_windows_ids_and_dates_by_excursion_id(session, id):
    windows_ids_and_dates = session.query(Schedule.id, Schedule.date_time).join(Excursion).filter(Excursion.id == id,
                                            Schedule.contact_link == '', Schedule.date_time >= datetime.now()).all()
    return windows_ids_and_dates

def window_id_by_title_and_date(session, title, date):
    date = datetime.strptime(date, '%d.%m.%Y')
    window_id = session.query(Schedule.id).join(Excursion).filter(Excursion.title == title,
                                                                  Schedule.date_time == date).all()
    return window_id[0][0]


def add_visit_into_window(session, visit_info) -> Schedule:
    #visit_info = [window_id, contact_link, contact_name,  number]
    this_visit = get_this_window(session, visit_info[0])
    if this_visit.contact_link:
        return False
    this_visit.contact_link = 'https://t.me/' + visit_info[1]
    this_visit.contact_name = visit_info[2]
    this_visit.visitors = visit_info[3]
    try:
        session.merge(this_visit)
        session.commit()
    except Exception:
        return False
    else:
        return this_visit
##конец ветки записи на посещение


####admin functions
def get_unempty_current_windows(session):
    data = session.query(Excursion.title, Schedule.date_time, Schedule.contact_name, Schedule.contact_link,
                         Schedule.visitors).join(Excursion).filter(Schedule.contact_link != '',
                                                                   Schedule.date_time >= datetime.now()).all()
    return data


def get_all_current_windows(session):
    data = (session.query(Schedule.id, Excursion.title, Schedule.date_time, Schedule.contact_link).
            join(Excursion).filter(Schedule.date_time >= datetime.now()).all())
    return data

# злая тема, но нужна ли она?
def get_all_excursion_info_by_id(session, id):
    delimiter = '-#-'
    data = session.query(Excursion.title, Excursion.description, Excursion.duration,
                         func.group_concat(Schedule.date_time, delimiter).label('date_times'),
                         func.group_concat(Schedule.contact_name, delimiter).label('contact_names'),
                         func.group_concat(Schedule.contact_link, delimiter).label('contact_links'),
                         func.group_concat(Schedule.visitors, delimiter).label('visitors')) \
                 .join(Schedule, Excursion.id == Schedule.excursion_id) \
                 .filter(Excursion.id == id) \
                 .group_by(Excursion.title, Excursion.description, Excursion.duration) \
                 .one()
    # типовая группировка для -#- разделителя '2024-05-26 00:00:00-#-,2024-05-24 00:00:00-#-'
    # внутри добавляется запятая на автомате, разделитель доваляется еще и в конец
    # чистим:
    temp = list(data[3:])
    for i in range(len(temp)):
        temp[i] = temp[i][:-len(delimiter)].split(delimiter + ',')
    return list(data[:3]) + temp


def update_excursion_by_id(session, id, field_name, new_value):
    excursion = session.query(Excursion).filter_by(id=id).first()
    if excursion:
        setattr(excursion, field_name, new_value)
        session.commit()
        return True
    else:
        return False


def del_excursion(session, excursion_id):
    try:
        session.query(Excursion).filter_by(id=excursion_id).delete()
        session.commit()
    except Exception:
        return False
    else:
        return True


def add_window(session, excursion_id, date_time):
    try:
        date_time = datetime.strptime(date_time, '%d.%m.%Y')
        session.add(Schedule(
            excursion_id=excursion_id,
            date_time=date_time
        ))
        session.commit()
    except Exception:
        return False
    else:
        return True


def delete_window(session, window_id):
    window = session.query(Schedule).filter_by(id=window_id).one()
    session.delete(window)
    session.commit()



def add_excursion(session,title, description, duration):
    session.add(Excursion(
        title=title,
        description=description,
        duration=duration
    ))
    session.commit()


def update_excursion(session):
    pass


def delete_excursion(session, ex_id):
    excursion = session.query(Excursion).filter_by(id=ex_id).one()
    session.delete(excursion)
    session.commit()


if __name__ == '__main__':
    session, engine = database_init()
    print(*get_all_excursions(session), sep='\n')


