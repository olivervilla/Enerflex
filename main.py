# coding=utf-8
from threading import Thread
import sqlite3
import tcp
import time
import json
import sys
import os


path = os.path.realpath(__file__)
path = path[:path.find('main.py')]

man = """
Uso:
    python main.py <comando> [opciones]

Comandos:
    -n          Ejecutar el programa con hilos por cada pozo.
    -e          Ejecutar el programa para secuenciar cada pozo.
    -g          Ejecutar el programa para dividir en dos grupos de preguntas.

Opciones:
    --- En implementacion
"""

def initialize():
    db = sqlite3.connect(path + 'enerflex.db', )
    c = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS time_operation('id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'name' TEXT UNIQUE NOT NULL, 
            'limitTime' INTEGER, 'onlineTime' INTEGER, 'actualTime' INTEGER, 'startTime' INTEGER, 'isOnline' INTEGER)"""
    c.execute(sql)
    sql = """CREATE TABLE IF NOT EXISTS connection_status ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'name' TEXT, 'ip' TEXT, 'isConnected' INTEGER, 
            'isOnPLC1' INTEGER, 'isOnPLC2' INTEGER, 'isOnBR20' INTEGER, 'isOkCoil1' INTEGER, 'isOkHold1' INTEGER, 'isOkInputs1_1' INTEGER, 'isOkInputs1_2' INTEGER,
            'isOkInputs1_3' INTEGER, 'isOkCoil2' INTEGER, 'isOkHold2' INTEGER, 'isOkInputs2_1' INTEGER, 'isOkInputs2_2' INTEGER, 'isOkInputs2_3' INTEGER, 
            'isOkSensors' INTEGER);"""
    c.execute(sql)
    db.commit()
    db.close()

def update_times_well():
    db = sqlite3.connect(path + 'enerflex.db', )
    c = db.cursor()

def read_info():
    list_pozos = list()
    try:
        with open(path + "init.json", "r") as f:
            repo = json.load(f)
            host = str(repo["host"])
            for pozo in repo["pozos"]:
                ip = str(pozo["ip"])
                nombre = str(pozo["nombre"])
                compresoras = pozo["compresoras"]
                topic = str(pozo["topic"])
                # actions = str(pozo["actions"])
                tm_out = int(pozo["tout"])
                plc1 = pozo["id_dispositivos"]["PLC1"]
                br20 = pozo["id_dispositivos"]["BR20"]
                plc2 = pozo["id_dispositivos"]["PLC2"]
                br20_normal = pozo["br20_normal"]
                ip_br20 = str(pozo["ip_br20"]) if pozo["ip_br20"] != None else None
                ptp = pozo["id_sensores"]["ptp"]
                ptr = pozo["id_sensores"]["ptr"]
                pld = pozo["id_sensores"]["pld"]
                ttp = pozo["id_sensores"]["ttp"]
                if "get_etm" in pozo:
                    etm = pozo["get_etm"]
                else:
                    etm = False
                print(ip, nombre)
                p = tcp.ModbusTCP(ip,
                                  nombre,
                                  compresoras,
                                  host,
                                  topic,
                                  # actions,
                                  id_plc1=plc1,
                                  id_br20=br20,
                                  id_plc2=plc2,
                                  id_ptp=ptp,
                                  id_ptr=ptr,
                                  id_pld=pld,
                                  id_ttp=ttp,
                                  br20_unique=br20_normal,
                                  ip_br20=ip_br20,
                                  tout=tm_out,
                                  get_etm=etm)
                list_pozos.append(p)
                
                if nombre == 'Cardenas 439' or nombre == 'Cardenas 539':
                    time.sleep(1)
        print('')
        return list_pozos

    except Exception as e:
        print('main', e)

def routine_each(list_pozos, minutes):
    while True:
		for p in list_pozos:
			print('Asking to ' + p._name)
			p.run_once()
			print('Wait for it')
			time.sleep(minutes*60)
		print('One full turn')

def routine_thread(list_pozos):
    for p in list_pozos:
        h = Thread(name="Pozo {}".format(p._name), target=p.run_loop)
        h.start()

def routine_groups(list_pozos, seconds):
    middle = int(round(len(list_pozos)/2))
    g1 = list_pozos[0:middle]
    g2 = list_pozos[middle:]
    while True:
        th1 = list()
        th2 = list()

        for p in g1:
            print('Asking to ' + p._name)
            h = Thread(target=p.run_once)
            # h.start()
            th1.append(h)
        for h in th1:
            h.start()
        for h in th1:
            h.join()
        # th1[:] = []
        print('Wait for g2\n')
        time.sleep(seconds)

        for p in g2:
            print('Asking to ' + p._name)
            h = Thread(target=p.run_once)
            # h.start()
            th2.append(h)
        for h in th2:
            h.start()
        for h in th2:
            h.join()
        # th2[:] = []
        print('Wait for g1\n')
        time.sleep(seconds)

if __name__ == '__main__':
    # init
    initialize()

    howmany = len(sys.argv)
    if howmany == 1:
        print('Error de arranque: no se especifico un parametro')
        print(man)
        exit()
    param = sys.argv[1]
    list_pozos = read_info()

    if  param == '-n':
        routine_thread(list_pozos)
    elif param == '-e':
        minutes = sys.argv[2] if howmany == 3 and sys.argv[2] == int else 10
        routine_each(list_pozos, minutes)
    elif param == '-g':
        seconds = sys.argv[2] if howmany == 3 and sys.argv[2] == int else 10
        routine_groups(list_pozos, seconds)
    else:
        print('Error de arranque: parametro no valido')
        print(man)

    print('-- THREADS STARTS! --')
