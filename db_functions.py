from mysql.connector import connect


def show_all_db():
    connection = connect(host="localhost", user="root", password='123456A%')
    cursor = connection.cursor()
    show_db_query = "SHOW DATABASES"
    cursor.execute(show_db_query)
    for db in cursor:
        print(db)
    connection.close()

def create_bot_db():
    connection = connect(host="localhost", user="root", password='123456A%')
    cursor = connection.cursor()
    query = "CREATE DATABASE excursion_bot_db"
    cursor.execute(query)
    connection.commit()
    connection.close()

def drop_bot_db():
    connection = connect(host="localhost", user="root", password='123456A%')
    cursor = connection.cursor()
    query = """
         DROP DATABASE excursion_bot_db
         """
    cursor.execute(query)
    connection.commit()
    connection.close()


def create_excursion_table():
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = """
    CREATE TABLE excursions(
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(100),
        description VARCHAR(1000),
        duration TIME
    )
    """
    cursor.execute(query)
    connection.commit()
    connection.close()


def get_excursions():
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = f"""SELECT id, title FROM excursions"""
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result

def add_new_excursion(title, description, duration):
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = """
        INSERT INTO excursions
        (title, description, duration)
        VALUES ( %s, %s, %s )
    """
    cursor.execute(query, (title, description, duration))
    connection.commit()
    connection.close()

def create_visit_table():
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = """
     CREATE TABLE visits(
         id INT AUTO_INCREMENT PRIMARY KEY,
         excursion_id INT,
         date DATE,
         time TIME,
         FOREIGN KEY(excursion_id) REFERENCES excursions(id)
     )
     """
    cursor.execute(query)
    connection.commit()
    connection.close()

def get_open_visits():
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = f"""SELECT visits.id, excursions.description, visits.date, visits.time, excursions.duration
    FROM excursions
    INNER JOIN visits
    ON visits.excursion_id = excursion.id
    """
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result


def add_new_visits_time(n, year, month, day, hours, minutes):
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = """
           INSERT INTO visits
           (excursion_id, date, time)
           VALUES ( %s, %s, %s )
       """

    cursor.execute(query, (n, f'{year}-{month}-{day}', f'{hours}:{minutes}'))
    connection.commit()
    connection.close()


def accept_visit():
    pass


# def get_field_from_db(table, field='*'):
#     connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
#     cursor = connection.cursor()
#     query = f"""
#     SELECT {field}
#     FROM {table}
#
#     """
#     cursor.execute(query, )
#     connection.commit()
#     connection.close()
#


#show_all_db()

