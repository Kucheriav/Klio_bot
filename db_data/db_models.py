from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, DefaultClause
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Excursion(Base):
    __tablename__ = 'excursions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(60))
    description = Column(Text())
    duration = Column(String(60))
    UniqueConstraint('title')

    def __str__(self):
        return f'''{self.title}\n{self.description}\n{self.duration}'''

#timetable
class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    excursion_id = Column(Integer, ForeignKey('excursions.id'))
    date_time = Column(DateTime)
    contact_link = Column(String(100), DefaultClause(''))
    contact_name = Column(String(300), DefaultClause(''))
    visitors = Column(String(100), DefaultClause('0'))
    UniqueConstraint('excursion_id', 'date_time')

    def __str__(self):
        return f'''{self.excursion_id}  {self.date_time}  {self.contact_link}  {self.contact_name}  {self.visitors}'''


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(300))
    link = Column(String(100))
    tg_id = Column(Integer())
    is_admin = Column(Boolean())

    def __str__(self):
        return f'''{self.name}  {self.link}  {self.tg_id}  {self.is_admin}'''


# def add_window(excursion_id=1, date_time=datetime(year=2024, month=1, day=30, hour=12, minute=30)):
#     with sessionmaker(bind=engine)() as session:
#         window = Schedule(
#             excursion_id=excursion_id,
#             date_time=date_time,
#         )
#         session.add(window)
#         session.commit()
#
#
#
#
# def cross_table_query_visits():
#     with sessionmaker(bind=engine)() as session:
#         data = session.query(Schedule, Excursion.title).join(Excursion).all()
#         # возвращется список списков [[объект Visit, Excursion.title], [] ....]
#         for el in data:
#             print(el[0].id, el[1], el[0].date_time, el[0].link, el[0].visitors)






