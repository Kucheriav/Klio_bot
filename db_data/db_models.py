from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from db_data.db_config_reader import read_db_config
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy_utils import database_exists, create_database


class Base(DeclarativeBase):
    pass


class Excursion(Base):
    __tablename__ = 'excursions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(50))
    description = Column(String(300))
    duration = Column(Integer)
    visits = relationship('Visit', back_populates='excursions')


class Visit(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    excursions_id = Column(Integer, ForeignKey('excursions.id'))
    excursions = relationship('Excursion', back_populates='visits')
    date_time = Column(DateTime)
    link = Column(String(50))
    visitors = Column(Integer)

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


