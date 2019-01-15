from datetime import timedelta as td
from datetime import datetime as dt
from enviroment import Address
import time
import os


one_week = 604800
one_day = 86400
one_hour = 3600


def clean_backup():
    path = Address.BACKUP_DAILY_FOLDER
    current_time = time.time()
    for f in os.listdir(path):
        creation_time = os.path.getctime(os.path.join(path, f))
        days = (current_time - creation_time) // one_day
        if days >= 2:
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


def clean_database(list_pozos):
    import sqlite3
    import csv
    from zipfile import ZipFile, ZIP_DEFLATED
    from datetime import datetime as dt

    fecha_reg = dt.today()

    db = sqlite3.connect(Address.DATABASE_FOLDER, )
    c = db.cursor()

    sql = "SELECT date('now', 'start of month', '-1 month');"
    c.execute(sql)

    fecha = str(c.fetchone()[0])
    fecha = dt.strptime(fecha, '%Y-%m-%d').strftime('%B%Y').lower()

    db.row_factory = sqlite3.Row
    c = db.cursor()

    for p in list_pozos:
        name_table = p._name.lower().replace("-", " ").replace(" ", "_")

        archivo_csv = "{1}_{0}.csv".format(name_table, fecha)
        archivo_zip = "{1}_{0}.zip".format(name_table, fecha)

        if not os.path.exists(Address.BACKUP_MONTHLY_FOLDER + archivo_zip):
            sql = """SELECT * FROM {0} WHERE 
                    date>=date('now', 'start of month', '-1 month')
                    and date<date('now', 'start of month')""".format(name_table)
            # date>=date('now', 'start of month', '-1 month') and date<date('now', 'start of month')
            c.execute(sql)
            data_month = c.fetchall()

            try:
                with open(archivo_csv, "wb") as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(data_month[0].keys())
                    for line in data_month:
                        csv_writer.writerow(line)

                with ZipFile(Address.BACKUP_MONTHLY_FOLDER + archivo_zip, 'w') as zipman:
                    zipman.write(archivo_csv, compress_type=ZIP_DEFLATED)
            except IndexError:
                print('Data already saved')
            except Exception as e:
                print(e, e.args)
            finally:
                if os.path.exists(archivo_csv):
                    os.unlink(archivo_csv)

            if os.path.exists(Address.BACKUP_MONTHLY_FOLDER + archivo_zip):
                # sql = """DELETE FROM {0}
                #          WHERE date>=date('now', 'start of month', '-1 month')
                #          AND date<date('now', 'start of month')""".format(name_table)
                # c.execute(sql)
                db.commit()
                pass
            
            time.sleep(2)
            print('{}   Cleaning completed for {}'.format(fecha_reg, p._name))
        else:
            print('{}   Cleaning already completed for {}'.format(fecha_reg, p._name))
    
    db.close()   
       
