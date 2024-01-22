from db_models import *
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine
from ..errors import *
import datetime
# https://www.internet-technologies.ru/articles/posobie-po-mysql-na-python.html#header-9658-6
# with sessionmaker(bind=engine)() as session:
SESSION = None
ENGINE = None

###service fucntions
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
    database_init()
    drop_database(ENGINE.url)
    database_init()

###test functions
def add_test_excursions(session):
    with open('test_excursions.txt', encoding='utf8') as file:
        excursions, windows = file.read().split('-#-')
        excursions = [list(filter(lambda x: len(x), exc.split('\n'))) for exc in excursions.split('@')]
        excursions = [list(map(lambda x: x.split(': ')[1], exc)) for exc in excursions]
    for excursion in excursions:
        session.add(Excursion(
            title=excursion[0],
            description=excursion[2],
            duration=excursion[1].split()[0]
        ))
    session.commit()

def get_all_excursions(session):
    data = session.query(Excursion).all()
    return data


def add_test_windows(session):
    with open('test_visits.txt', encoding='utf8') as file:
        visits = list(map(lambda x: x.split(), file.read().split('-')))
    for visit in visits:
        session.add(Schedule(
            excursion_id=int(visit[0]),
            date_time=datetime.datetime.strptime(visit[1], '%d.%m.%Y')
        ))
    session.commit()


def get_all_windows(session):
    data = session.query(Schedule).all()
    return data


def get_this_window(session, this_id) -> Schedule:
    data = session.query(Schedule).filter(Schedule.id==this_id)
    return data


##user functions
def get_current_windows(session):
    data = session.query(Schedule.id, Excursion.title, Excursion.description, Schedule.date_time).join(Excursion).filter(
        Schedule.link == '', Schedule.date_time >= datetime.now()).all()
    for i in range(len(data)):
        data[i].insert(1, (i + 1))
    return data


def application_for_visit(session, visit_info):
    #visit_info = [id, username, name,  number]
    current_visit = get_this_window(session, visit_info[0])
    current_visit.link = 'https://t.me/' + visit_info[1]
    current_visit.name = visit_info[2]
    current_visit.visitors = visit_info[3]
    session.merge(current_visit)
    session.commit()


####admin functions
def get_current_visits(session):
    data = session.query(Excursion.title, Schedule.date_time, Schedule.name, Schedule.link, Schedule.visitors).join(
        Excursion).filter(
        Schedule.link != '', Schedule.date_time >= datetime.now()).all()
    return data


def add_window(session, title, date_time):
    excursion_id = session.query(Excursion.id).filter(Excursion.title == title).one()
    try:
        date_time = datetime.datetime.strptime(date_time, '%d.%m.%Y')
    except Exception:
        raise DateInputError
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




database_init()
# add_test_excursions(SESSION)
add_test_windows(SESSION)
lines = get_all_windows(SESSION)
for line in lines:
    print(line)