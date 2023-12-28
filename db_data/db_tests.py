from db_models import *
import db_session




configs = read_db_config()
url = "mysql://%(user)s:%(password)s@%(host)s/%(db)s" % {
    'user': configs['user'],
    'password': configs['password'],
    'host': configs['host'],
    'db': configs['database']
}
db_session.global_init(url)
db = db_session.create_session()
########вот тут будет код бота№№№№№№№№№№№№№№№№№





db.close()