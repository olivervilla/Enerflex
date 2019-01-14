import paho.mqtt.subscribe as subscribe
from threading import Thread
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import time as tm
import time
import sqlite3
import os

path = os.path.realpath(__file__)
path = path[:path.find('decoder.py')]

def decoder(num):
    flags = list()
    code = num
    code = bin(code)
    code = code.split('b')[1]

    for bit in code:
        bit = True if bit == '1' else False
        flags.append(bit)

    flags.reverse()

    l = len(flags)
    if l != 15:
        f = 15 - l
        for bit in range(1, f-1):
            flags.append(False)

    return flags

def encoder(flags):
    # print(flags)
    tmp = list()
    for bit in flags:
        bit = '1' if bit == True else '0'
        tmp.append(bit)
    tmp.reverse()
    tmp = ''.join(tmp)
    tmp = int(tmp, 2)
    return hex(tmp)

def encoder_hex(flags):
    tmp = list()
    acum = 0
    for bit in flags:
        bit = 1 if bit == True else 0
        tmp.append(bit)
    for bit in tmp:
        acum += bit
    return hex(acum)

# print(decoder(512 + 4))
# c = [True]*15
# c[0] = True
# c[10] = True
# p = encoder(c)
# f = encoder_hex(c)
# print(p, type(p))
# print(f, type(f))


def on_action(client, userdata, message):
    print('Action recived from {} - {}'.format(client, userdata))
    print(message.payload)

def sub():
    subscribe.callback(on_action, topic, hostname="187.217.207.73", keepalive=5)

def dicts(param):
    print(param['s'])

topic = '/1234/test/attrs'

# dicts({'s':15})

# c = subscribe.simple(topic, hostname="187.217.207.73", keepalive=5)

# h = Thread(target=sub)
# h.start()

# self
# count = 0

rpm = 1000
etm = None
name = "prueba_1"

while True:
    # fecha, tiempo = dt.today().isoformat().split('T')
    db = sqlite3.connect(path + 'enerflex.db', )
    c = db.cursor()
    sql = """SELECT startTime, onlineTime, actualTime, isOnline FROM time_operation WHERE name = '{}'""".format(name)
    c.execute(sql)

    start, accum, actual, isOnline = c.fetchone()
    etm = dt.strptime(str(td(seconds=accum)), "%H:%M:%S").strftime("%H:%M")
    print(etm)

    # try:
    #     now = compare = dt.strptime("{0} {1}".format(fecha, tiempo), "%Y-%m-%d %H:%M:%S.%f")
    # except ValueError:
    #     now = compare = dt.strptime("{0} {1}".format(fecha, tiempo), "%Y-%m-%d %H:%M:%S")
 
    # now = time.mktime(now.timetuple())
    # now = now - 6*3600

    # today = dt.today() - td(hours=6)
    # limit = dt(today.year, today.month, today.day+1)

    # print('Empezo a trabajar', dt.fromtimestamp(start).strftime("%H:%M"))
    # print('Hora actual', dt.fromtimestamp(now).strftime("%H:%M"))

    # if compare > limit or (start - now) > 24*3600 :
    #     # Si queremos horas total (sin reiniciar el conteo, no reiniciar online time)
    #     sql = """UPDATE time_operation SET startTime={hours}, actualTime={hours}, 
    #             onlineTime=0 isOnline=0 WHERE name='{name}';""".format(hours=now, name=name)
    #     c.execute(sql)
    #     db.commit()

    # if rpm != None or count > 3:
    #     if rpm != None:
    #         count = 0
            
    #     if not 100 >= rpm >= 0 and count < 3:
    #         sql = "UPDATE time_operation SET actualTime={hours} WHERE name='{name}';".format(name=name, hours=now)
    #         c.execute(sql)
    #         if isOnline == 0:
    #             if not accum > 0:
    #                 etm = now - start
    #             else:
    #                 etm = accum + (now - actual)
    #             sql = "UPDATE time_operation SET isOnline=1 WHERE name='{name}';".format(name=name)
    #             c.execute(sql)
    #         else:
    #             etm = accum + (now - actual)
    #         sql = "UPDATE time_operation SET onlineTime={hours} WHERE name='{name}';".format(name=name, hours=etm)
    #         c.execute(sql)
    #     elif 100 >= rpm >= 0 or count > 3:
    #         sql = "UPDATE time_operation SET startTime={hours}, actualTime={hours}, isOnline=0 WHERE name='{name}';".format(name=name, hours=now)
    #         etm = accum
    #         c.execute(sql)
    # else:
    #     count += 1
    
    # try:
    #     etm = dt.strptime(str(td(seconds=etm)), "%H:%M:%S").strftime("%H:%M")
    # except ValueError:
    #     etm = dt.strptime(str(td(seconds=etm)), "%H:%M:%S.%f").strftime("%H:%M")
    
    # print(etm)
    # print('-'*20)

    db.commit()
    db.close()
    time.sleep(5)


# -------------- Compare dates
# fecha, tiempo = dt.today().isoformat().split('T')

# now = now_compare = dt.strptime("{0} {1}".format(fecha, tiempo), "%Y-%m-%d %H:%M:%S.%f")
# now = time.mktime(now.timetuple())
# now = now - 6*3600

# today = dt.today() - td(hours=6)
# limit = dt(today.year, today.month, today.day+1)


# print(limit, now_compare)
# print(now_compare > limit)
# print('-'*10)
# now_compare += td(hours=1, minutes=44)
# print(limit, now_compare)
# print(now_compare > limit)

# status = [1]*15

# sql = """UPDATE connection_status SET isConnected={}, isOnPLC1={}, isOnPLC2={}, isOnBR20={}, isOkCoil1={}, 
#         isOkHold1={}, isOkInputs1_1={}, isOkInputs1_2={}, isOkInputs1_3={}, isOkCoil2={}, isOkHold2={}, 
#         isOkInputs2_1={}, isOkInputs2_2={}, isOkInputs2_3={}, isOkSensors={}""".format(*status)
# sql = sql + " WHERE name='{}'".format(name)
# print(sql)
