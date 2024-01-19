from db_data.db_models import *
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine
import datetime
# https://www.internet-technologies.ru/articles/posobie-po-mysql-na-python.html#header-9658-6

SESSION = None
ENGINE = None

def database_init():
    global SESSION, ENGINE
    configs = read_db_config()
    url = "mysql://%(user)s:%(password)s@%(host)s/%(db)s" % {
        'user': configs['user'],
        'password': configs['password'],
        'host': configs['host'],
        'db': configs['database']
    }
    ENGINE = create_engine(url)
    if not database_exists(ENGINE.url):
        create_database(ENGINE.url)
    Base.metadata.create_all(bind=ENGINE)
    SESSION = sessionmaker(bind=ENGINE)()
    return SESSION



def recreate_db():
    drop_database(ENGINE.url)


def get_current_windows(session):
    data = session.query(Schedule.id, Excursion.title, Excursion.description, Schedule.date_time).join(Excursion).filter(
        Schedule.link == '', Schedule.date_time >= datetime.now()).all()
    for i in range(len(data)):
        data[i].insert(1, (i + 1))
    return data

def get_this_window(session, this_id) -> Schedule:
    data = session.query(Schedule).filter(Schedule.id==this_id)
    return data

def application_for_visit(session, visit_info):
    #visit_info = [id, username, name,  number]
    current_visit = get_this_window(session, visit_info[0])
    current_visit.link = 'https://t.me/' + visit_info[1]
    current_visit.name = visit_info[2]
    current_visit.visitors = visit_info[3]
    session.merge(current_visit)
    session.commit()