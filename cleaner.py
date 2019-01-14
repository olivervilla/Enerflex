from datetime import timedelta as td
from datetime import datetime as dt
import time
import os
from enviroment import Address


one_week = 604800
one_day = 86400
one_hour = 3600


def clean_backup():
    path = Address.BACKUP_FOLDER
    current_time = time.time()
    for f in os.listdir(path):
        creation_time = os.path.getctime(os.path.join(path, f))
        days = (current_time - creation_time) // one_day
        if days >= 1:
            print('{} removed'.format(f))
            os.unlink(path + f)
      

def clean_logs():
    path = Address.LOGS_FOLDER
    current_time = time.time()
    for f in os.listdir(path):
        creation_time = os.path.getctime(path + f)
        week = (current_time - creation_time) // one_week
        if week >= 1:
            print('{} removed'.format(f))
            os.unlink(path + f)


def clean_data():
    path = Address.DATA_FOLDER
    current_time = time.time()
    for f in os.listdir(path):
        creation_time = os.path.getctime(path + f)
        week = (current_time - creation_time) // one_week
        if week >= 1:
            print('{} removed'.format(f))
            os.unlink(path + f)