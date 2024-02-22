from db_models import *
from db_config_reader import read_db_config
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import errors
from datetime import datetime



### системные функции
def database_init():
    configs = read_db_config()
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


### общие функции
def get_all_excursions(session):
    data = session.query(Excursion).all()
    return [(x.title, x.description, x.duration)  for x in data]


def get_all_windows(session):
    data = session.query(Schedule).all()
    return data

def get_all_users(session):
    data = session.query(User).all()
    return data

def get_admins_ids(session):
    data = session.query(User.tg_id).filter(User.is_admin == True).all()
    return [x[0] for x in data]

def get_this_window(session, this_id) -> Schedule:
    data = session.query(Schedule).filter(Schedule.id == this_id).one()
    return data


### пользовательские функции
## начало ветки записи на посещение
def get_current_windows_names(session):
    data = (session.query(Excursion.title).join(Schedule).
            filter(Schedule.contact_link == '', Schedule.date_time >= datetime.now()).all())
    data = set([x[0] for x in data])
    return data

def get_description_by_title(session, title):
    data = session.query(Excursion.description).filter(Excursion.title == title).one()[0]
    return data

def get_actual_dates_by_name(session, title):
    dates = session.query(Schedule.date_time).join(Excursion).filter(Excursion.title == title,
                                                                     Schedule.date_time >= datetime.now()).all()
    dates = [x[0] for x in dates]
    return dates

def window_id_by_title_and_date(session, title, date):
    window_id = session.query(Schedule.id).join(Excursion).filter(Excursion.title == title,
                                                                  Schedule.date_time == date).all()
    return window_id[0][0]


def add_visit(session, visit_info):
    #visit_info = [window_id, contact_link, contact_name,  number]
    this_visit = get_this_window(session, visit_info[0])
    this_visit.contact_link = 'https://t.me/' + visit_info[1]
    this_visit.contact_name = visit_info[2]
    this_visit.visitors = visit_info[3]
    session.merge(this_visit)
    session.commit()
    return 'ok'
##конец ветки записи на посещение


####admin functions
def get_current_visits(session):
    data = session.query(Excursion.title, Schedule.date_time, Schedule.contact_name, Schedule.contact_link,
                         Schedule.visitors).join(Excursion).filter(Schedule.contact_link != '',
                                                                   Schedule.date_time >= datetime.now()).all()
    return data


def add_window(session, title, date_time):
    excursion_id = session.query(Excursion.id).filter(Excursion.title == title).one()
    try:
        date_time = datetime.strptime(date_time, '%d.%m.%Y')
    except Exception:
        raise errors.DateInputError
    else:
        session.add(Schedule(
            excursion_id=excursion_id,
            date_time=date_time
        ))
        session.commit()


def update_window(session):
    pass


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


