
def get_all_db():
    with connect(host="localhost", user="root", password='123456A%') as connection:
        cursor = connection.cursor()
        show_db_query = "SHOW DATABASES"
        cursor.execute(show_db_query)
        return [db[0] for db in cursor]

def create_bot_db(db):
    with connect(host="localhost", user="root", password='123456A%') as connection:
        cursor = connection.cursor()
        query = f"CREATE DATABASE {db}"
        cursor.execute(query)
        connection.commit()


def drop_bot_db(db):
    db_config = read_db_config()
    with MySQLConnection(**db_config) as connection:
        cursor = connection.cursor()
        query = f"""
             DROP DATABASE {db}
             """
        cursor.execute(query)
        connection.commit()

def show_tables(db):
    db_config = read_db_config()
    with MySQLConnection(**db_config) as connection:
        cursor = connection.cursor()
        query = f"SHOW TABLES FROM {db}"
        cursor.execute(query)
        return [table[0] for table in cursor]

def drop_table(table):
    # if table in show_tables()
    db_config = read_db_config()
    with MySQLConnection(**db_config) as connection:
        cursor = connection.cursor()
        query = f"""
                 DROP TABLE {table}
                 """
        cursor.execute(query)
        connection.commit()


def describe_table(table):
    db_config = read_db_config()
    with MySQLConnection(**db_config) as connection:
        show_table_query = f"DESCRIBE {table}"
        cursor = connection.cursor()
        cursor.execute(show_table_query)
        result = cursor.fetchall()
        for row in result:
            print(row)



def create_excursion_table():
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = """
    CREATE TABLE excursions(
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(100),
        description VARCHAR(1000),
        duration INT
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
         link VARCHAR(30) DEFAULT 'no',
         visitors INT DEFAULT 0,
         FOREIGN KEY(excursion_id) REFERENCES excursions(id)
     )
     """
    cursor.execute(query)
    connection.commit()
    connection.close()

def get_open_visits():
    connection = connect(host="localhost", user="root", password='123456A%', database='excursion_bot_db')
    cursor = connection.cursor()
    query = f"""SELECT visits.id, excursions.title, excursions.description, visits.date, visits.time, excursions.duration
    FROM excursions
    INNER JOIN visits
    ON visits.excursion_id = excursions.id
    WHERE visits.link = 'no'
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


if __name__ == '__main__':
    pass
    # drop_bot_db('excursion_bot_db')
