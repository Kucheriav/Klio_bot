import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file='log.txt'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_file, maxBytes=3000000, backupCount=5)  # Максимальный размер файла 1 МБ, хранится до 5 файлов
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
