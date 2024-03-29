from configparser import ConfigParser
import os


THIS_FOLDER = 'db_data'


def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()

    where_are_we = os.getcwd()
    if THIS_FOLDER not in where_are_we:
        path = os.path.join(os.getcwd(), THIS_FOLDER, filename)
    else:
        path = os.path.join(os.getcwd(), filename)

    parser.read(path)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


if __name__ == '__main__':
    print(read_db_config())