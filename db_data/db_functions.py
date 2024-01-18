from mysql.connector import connect
from mysql.connector import MySQLConnection
from db_data.db_config_reader import read_db_config
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
    data = session.query(Excursion.title, Schedule.date_time).join(Excursion).filter(
        Schedule.link == '', Schedule.date_time >= datetime.now())
    return data


def application_for_visit(current_visit: Schedule, link='mysite.org', visitors=6):
    with sessionmaker(bind=engine)() as session:
        current_visit.link = link
        current_visit.visitors = visitors
        session.merge(current_visit)
        session.commit()