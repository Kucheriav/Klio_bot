from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, DefaultClause
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Excursion(Base):
    __tablename__ = 'excursions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(60))
    description = Column(Text())
    duration = Column(String(60))
    UniqueConstraint('title')

    schedules = relationship('Schedule', cascade='all, delete')

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






