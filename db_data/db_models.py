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
    duration = Column(String)
    visits = relationship('Schedule', back_populates='excursions')

    def __str__(self):
        return f'''{self.title}\n{self.description}\n{self.duration}'''


class Schedule(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    excursion_id = Column(Integer, ForeignKey('excursions.id'))
    excursions = relationship('Excursion', back_populates='visits')
    #может ли дата/время быть ключом?
    date_time = Column(DateTime)
    link = Column(String(100))
    name = Column(String(300))
    visitors = Column(Integer)

    def __str__(self):
        return f'''{self.excursion_id}  {self.date_time}  {self.link}  {self.name}  {self.visitors}'''



def add_window(excursion_id=1, date_time=datetime(year=2024, month=1, day=30, hour=12, minute=30)):
    with sessionmaker(bind=engine)() as session:
        window = Schedule(
            excursion_id=excursion_id,
            date_time=date_time,
        )
        session.add(window)
        session.commit()




def cross_table_query_visits():
    with sessionmaker(bind=engine)() as session:
        data = session.query(Schedule, Excursion.title).join(Excursion).all()
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
    Base.metadata.create_all(bind=engine)
    cross_table_query_visits()

    print('ok')


