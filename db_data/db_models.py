from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from db_data.db_config_reader import read_db_config
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
class Base(DeclarativeBase):
    pass


class Excursion(Base):
    __tablename__ = 'excursions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(60))
    description = Column(String(1000))
    duration = Column(Integer)
    visits = relationship('Visit', back_populates='excursions')


class Visit(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    excursions_id = Column(Integer, ForeignKey('excursions.id'))
    excursions = relationship('Excursion', back_populates='visits')
    #может ли дата/время быть ключом?
    date_time = Column(DateTime)
    link = Column(String(50))
    visitors = Column(Integer)



def enter_some_excursions_info():
    with sessionmaker(bind=engine)() as session:
        excursion = Excursion(
            title='Калужская Область в годы Великой Отечественной войны',
            description="В ходе экскурсии музейный актив рассказывает посетителям о том, что происходило на "
                        "территории Калужской области в 1941-1945гг. Экскурсоводы показывают коллекцию фронтовой посуды "
                        "и уникальные издания памяток, где увековечены имена воинов, отдавших жизни за нашу землю. В конце "
                        "рассказа посетители могут пройти тест и посоревноваться с интерактивным помощником в том, "
                        "сколько они запомнили.",
            duration = '20'
        )
        session.add(excursion)
        excursion = Excursion(
            title='Дети - герои',
            description="В ходе мероприятия экскурсоводы рассказывают о детях, совершивших подвиги ради Родины - Саше "
                        "Чекалине и Лёне Голикове. Затем знакомят посетителей с таким понятием как «пионер» и "
                        "рассказывают о подробностях посвящения. Интерактивный помощник Клио помогает показать ребятам "
                        "видео с этой самой церемонии.",
            duration='15'
        )
        session.add(excursion)
        session.commit()


def enter_some_events():
    with sessionmaker(bind=engine)() as session:
        visitor = Visit(
            excursions_id=1,
            date_time=datetime(year=2024, month=1, day=30, hour=12, minute=30),
        )
        session.add(visitor)
        session.commit()

def add_some_visitors(current_visit: Visit):
    with sessionmaker(bind=engine)() as session:
        current_visit.link = 'mysite.org'
        current_visit.visitors = 6

        session.merge(current_visit)
        session.commit()


def cross_table_query_visits():
    with sessionmaker(bind=engine)() as session:
        data = session.query(Visit, Excursion.title).join(Excursion).all()
        # возвращется список списков [[объект Visit, Excursion.title], [] ....]
        for el in data:
            print(el[0].id, el[1], el[0].date_time, el[0].link, el[0].visitors)


# пробуем без лицейских штучек и файла db_session
if __name__ == '__main__':
    configs = read_db_config()
    url = "mysql://%(user)s:%(password)s@%(host)s/%(db)s"%{
        'user': configs['user'],
        'password': configs['password'],
        'host':configs['host'],
        'db':configs['database']
    }
    engine = create_engine(url)
    if not database_exists(engine.url):
        create_database(engine.url)
    print(database_exists(engine.url))
    Base.metadata.create_all(bind=engine)
    cross_table_query_visits()

    print('ok')


