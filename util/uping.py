# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
from datetime import datetime
from threading import Thread
import json
import os

path = os.path.realpath(__file__)
path = path[:path.find('uping.py')]
path_json = path[:path.find('util')]


def example():
    arg = "if netcat -z google.com 80; then echo \"Ok\"; else echo \"Noup\"; fi"
    p = Popen(arg, shell=True, stdout=PIPE)
    data = p.communicate()[0].split('\n')[0]
    if data == "Ok":
        return True
    else:
        return False

def make_ping(ip, name):
    fecha, tiempo = datetime.today().isoformat().split('T')

    arg = "ping {} -n 10".format(ip)
    p = Popen(arg, shell=True, stdout=PIPE)
    info = p.communicate()[0]
    info = info.replace('\r', ' ')

    with open(path + 'ping_{}.txt'.format(name), 'a+') as f:
        f.write('{0} {1}'.format(fecha, tiempo))
        f.write(info)
        f.write('-'*50)
        f.write('\n')
        f.close()
    return info

def make_tracert(ip, name):
    fecha, tiempo = datetime.today().isoformat().split('T')
    arg = "tracert {}".format(ip)
    p = Popen(arg, shell=True, stdout=PIPE)
    info = p.communicate()[0]
    info = info.replace('\r', ' ')
    with open(path + 'trace_{}.txt'.format(name), 'a+') as f:
        f.write('{0} {1}'.format(fecha, tiempo))
        f.write(info)
        f.write('-'*50)
        f.write('\n')
        f.close()
    return info

def make_csv(data, ip, name, fecha, hora):
    header = "fecha,hora,nombrePozo,ip,enviados,recibidos,perdidos,%perdidos,tiempoMin,tiempoMax,tiempoProm"
    file = path + 'trace_{}.csv'.format(name)
    data = "{},{},{},{}".format(fecha, hora, name, ip)

    with open(file, 'a+') as f:
        if os.stat(file).st_size == 0:
            f.write(header)

        f.write(data)
        # f.write('-'*50)
        # f.write('\n')


if __name__ == '__main__':
    # with open(path_json + 'init.json', 'r') as f:
    #     repo = json.load(f)
    #     for pozo in repo["pozos"]:
    #         ip = str(pozo["ip"])
    #         nombre = str(pozo["nombre"]).lower().replace("-", " ").replace(" ", "_")
            
    #         h1 = Thread(name="ping {}".format(nombre), target=make_ping, args=(ip, nombre,))
    #         h1.start()

    #         h2 = Thread(name="trace {}".format(nombre), target=make_tracert, args=(ip, nombre,))
    #         h2.start()

    #         print('Making ping to {}...'.format(nombre))
    #         print('Making trace to {}...'.format(nombre))
    #         print('-'*20)
    
    arg = "ping 192.168.2.102"
    p = Popen(arg, shell=True, stdout=PIPE)
    info = p.communicate()[0]
    # info = unicode(info, "utf-8", errors='replace')
    print('info', unicode(info, 'utf-8', errors='replace'))
    print('string', unicode('Máximo', 'utf-8', errors='replace'))
    # i1 = info.find()
    # print(i1)
    # i1 = info.find(u"Máximo")
    # print(i1)
