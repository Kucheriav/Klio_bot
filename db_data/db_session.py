import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from db_models import *


__factory = None


def global_init(url):
    global __factory

    if __factory:
        return

    engine = create_engine(url)
    __factory = orm.sessionmaker(bind=engine)
    Base.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
