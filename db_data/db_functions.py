from db_data.db_models import *
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine
import errors
from datetime import datetime
import os
# https://www.internet-technologies.ru/articles/posobie-po-mysql-na-python.html#header-9658-6
# with sessionmaker(bind=engine)() as session:


###service functions
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

###test functions
def add_test_data_classes(session):
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


def get_all_excursions(session):
    data = session.query(Excursion).all()
    return data


def get_all_windows(session):
    data = session.query(Schedule).all()

    return data


def get_this_window(session, this_id) -> Schedule:
    data = session.query(Schedule).filter(Schedule.id == this_id)
    return data


##user functions
def get_current_windows(session):
    data = session.query(Schedule.id, Excursion.title, Excursion.description, Schedule.date_time).join(Excursion).filter(
        Schedule.contact_link == '', Schedule.date_time >= datetime.now()).all()
    for i in range(len(data)):
        data[i].insert(1, (i + 1))
    return data


def get_current_windows_names(session):
    data = (session.query(Excursion.title).join(Schedule).
            filter(Schedule.contact_link == '', Schedule.date_time >= datetime.now()).all())
    return data


def application_for_visit(session, visit_info):
    #visit_info = [id, username, name,  number]
    current_visit = get_this_window(session, visit_info[0])
    current_visit.contact_link = 'https://t.me/' + visit_info[1]
    current_visit.contact_name = visit_info[2]
    current_visit.visitors = visit_info[3]
    session.merge(current_visit)
    session.commit()


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
    print(get_all_windows(session))
    print('ok')
