from db_models import *
from db_config_reader import read_config
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from log_writer import setup_logger
import inspect
from typing import List

engine = None
logger = None
if not logger:
    logger = setup_logger(__name__)


def db_error_handler(func):
    MAX_RECONNECT_ATTEMPTS = 3
    def wrapper(*args, **kwargs):
        reconnect_attempts = 0
        try:
            # assert isinstance(args[0], Session)
            return func(*args, **kwargs)
        # except AssertionError as e:
        #     logger.error(f"Function {inspect.currentframe().f_back.f_code.co_name} dont have session argument "
        #                  f"that is demanded by error decorator", exc_info=True)
        # except OperationalError as e:
        #     logger.error(f"OperationalError in function '{inspect.currentframe().f_back.f_code.co_name}: "
        #                  f"{e}. Attempting to reconnect...")
        #     session, engine = database_init()
        #     return func(session, *args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Database error of type {error_type} in function "
                         f"'{inspect.currentframe().f_back.f_code.co_name}': {str(e)}", exc_info=True)
    return wrapper


### системные функции
def database_init():
    configs = read_config(filename='config.ini', section='mysql')
    url = "mysql://%(user)s:%(password)s@%(host)s/%(db)s" % {
        'user': configs['user'],
        'password': configs['password'],
        'host': configs['host'],
        'db': configs['database']
    }
    global engine
    if engine is None:
        engine = create_engine(url, pool_size=10, max_overflow=5)
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    return session, engine


def database_session(func):
    def wrapper(*args, **kwargs):
        session, _ = database_init()
        return func(session, *args, **kwargs)
    return wrapper

def recreate_db():
    global engine
    session, engine = database_init()
    drop_database(engine.url)
    engine = None
    session, engine = database_init()


def check_date(date):
    try:
        d = datetime.strptime(date, '%d.%m.%Y %H:%M')
    except ValueError as ex:
        return 'Некорректный формат даты! Пример верного: 05.05.2055 12:23'
    if d < datetime.now():
        return 'Этот день уже прошел'
    return 'ok'


### общие функции

@db_error_handler
@database_session
def get_all_excursions(session):
    data = session.query(Excursion).all()
    return data


@db_error_handler
@database_session
def get_all_windows(session):
    data = session.query(Excursion.title, Window.date_time, Window.contact_link, Window.contact_name,
                         Window.visitors).join(Excursion).all()
    return data


@db_error_handler
@database_session
def get_all_users(session): # used in tests only
    data = session.query(User).all()
    return data


@db_error_handler
@database_session
def get_admins(session):
    admins = session.query(User).filter(User.is_admin == True).all()
    return {x.tg_user_id: x for x in admins}


@db_error_handler
@database_session
def get_this_window(session, this_id) -> Window:
    data = session.query(Window).filter(Window.id == this_id).one()
    return data


@db_error_handler
@database_session
def get_excursions_id_by_title(session, title):
    ex_id = session.query(Excursion.id).filter(Excursion.title == title).one()
    if ex_id:
        return True, ex_id[0]
    else:
        return False, title


@db_error_handler
@database_session
def update_user_chat_id(session, user_id, chat_id):
    user = session.query(User).filter(User.tg_user_id == user_id).one()
    user.tg_chat_id = chat_id
    session.merge(user)
    session.commit()


@db_error_handler
@database_session
def invert_event_listener_status(session, user: User):
    user.is_tracking_events = bool((int(user.is_tracking_events) + 1) % 2)
    session.merge(user)
    session.commit()


### пользовательские функции
## начало ветки записи на посещение
@db_error_handler
@database_session
def get_current_excursions_ids_and_names(session):
    current_excursions_ids_and_names = (session.query(Excursion.id, Excursion.title).join(Window).
                                        filter(Window.contact_link == '', Window.date_time >= datetime.now()).all())
    logger.debug('Found current_excursions_ids_and_names in DB')
    return set(current_excursions_ids_and_names)


@db_error_handler
@database_session
def get_excursion_info_by_id(session, id):
    excursion_info = session.query(Excursion.title, Excursion.description, Excursion.duration).filter(Excursion.id == id).one()
    logger.debug('Found excursion_info in DB')
    return excursion_info


@db_error_handler
@database_session
def get_actual_dates_by_name(session, title): # used in tests only
    dates = session.query(Window.date_time).join(Excursion).filter(Excursion.title == title,
                                                                   Window.contact_link == '', Window.date_time >= datetime.now()).all()
    dates = [x[0] for x in dates]
    logger.debug('Found actual_dates_by_name in DB')
    return dates


@db_error_handler
@database_session
def get_windows_ids_and_dates_by_excursion_id(session, id):
    windows_ids_and_dates = session.query(Window.id, Window.date_time).join(Excursion).filter(Excursion.id == id,
                                                                                              Window.contact_link == '', Window.date_time >= datetime.now()).all()

    logger.debug('Found windows_ids_and_dates_by_excursion_id in DB')
    return windows_ids_and_dates


@db_error_handler
@database_session
def window_id_by_title_and_date(session, title, date): # used in tests only
    date = datetime.strptime(date, '%d.%m.%Y %H:%M')
    window_id = session.query(Window.id).join(Excursion).filter(Excursion.title == title,
                                                                Window.date_time == date).all()
    logger.debug('Found windows_ids_and_dates_by_excursion_id in DB')
    return window_id[0][0]


@db_error_handler
@database_session
def add_visit_into_window(session, visit_info) -> Window:
    #visit_info = [window_id, contact_link, contact_name,  number]
    this_visit = get_this_window(visit_info[0])
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
        logger.debug('Added_visit_into_window in DB')
        return this_visit
##конец ветки записи на посещение


####admin functions
@db_error_handler
@database_session
def get_all_current_windows(session):
    data = (session.query(Window.id, Excursion.title, Window.date_time, Window.contact_link).
            join(Excursion).filter(Window.date_time >= datetime.now()).all())

    logger.debug('Found all_current_windows in DB')

    return data

# злая тема, но нужна ли она?
def get_all_excursion_info_by_id(session, id):
    delimiter = '-#-'
    data = session.query(Excursion.title, Excursion.description, Excursion.duration,
                         func.group_concat(Window.date_time, delimiter).label('date_times'),
                         func.group_concat(Window.contact_name, delimiter).label('contact_names'),
                         func.group_concat(Window.contact_link, delimiter).label('contact_links'),
                         func.group_concat(Window.visitors, delimiter).label('visitors')) \
                 .join(Window, Excursion.id == Window.excursion_id) \
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


@db_error_handler
@database_session
def add_excursion(session, data):
    try:
        session.add(Excursion(title=data[0], description=data[2], duration=data[1]))
        session.commit()
    except Exception:
        return False
    else:

        logger.debug('Add excursion in DB')

        return True


@db_error_handler
@database_session
def update_excursion_by_id(session, id, field_name, new_value):
    excursion = session.query(Excursion).filter_by(id=id).first()
    if excursion:
        setattr(excursion, field_name, new_value)
        session.commit()

        logger.debug('Updated excursion in DB')

        return True
    else:
        return False


@db_error_handler
@database_session
def del_excursion(session, excursion_id):
    try:
        session.query(Excursion).filter_by(id=excursion_id).delete()
        session.commit()
    except Exception as ex:
        print(ex.args[0])
        return False
    else:
        logger.debug('Deleted excursion in DB')
        return True


@db_error_handler
@database_session
def get_window_info_by_id(session, window_id):
    window_info = (session.query(Excursion.title, Excursion.description, Excursion.duration,
                                 Window.date_time, Window.contact_link, Window.contact_name, Window.visitors).
                   join(Window, Excursion.id == Window.excursion_id).
                   filter(Window.id == window_id).one())
    logger.debug('Found window_info_by_id in DB')
    return window_info


@db_error_handler
@database_session
def add_window(session, excursion_id, date_time):
    try:
        date_time = datetime.strptime(date_time, '%d.%m.%Y %H:%M')
        session.add(Window(
            excursion_id=excursion_id,
            date_time=date_time
        ))
        session.commit()
    except Exception:
        return False
    else:
        logger.debug('Add window in DB')
        return True


@db_error_handler
@database_session
def update_window_by_id(session, id, field_name, new_value):
    window = session.query(Window).filter_by(id=id).first()
    if window:
        setattr(window, field_name, new_value)
        session.commit()
        logger.debug('Updated window in DB')
        return True
    else:
        return False


@db_error_handler
@database_session
def delete_window(session, window_id):
    window = session.query(Window).filter_by(id=window_id).one()
    session.delete(window)
    session.commit()
    logger.debug('Deleted window in DB')


if __name__ == '__main__':
    database_init()
    print(*get_all_excursions(), sep='\n')


