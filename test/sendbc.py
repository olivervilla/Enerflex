import json
import paho.mqtt.publish as publish
import time
import os

topic = "/1234/142.183.3.10(2)/attrs"
# topic = "/1234/prueba/attrs"
host = "187.217.207.73"
archivo = "bc20190109_cardenas_439.txt"

data = None
with open(archivo, 'r') as f:
    data = str(f.read())
    data = data.split('\n')

    # a = int(round(float(len(data)/12)))
    i = 0
    for x in data:
        x = json.dumps(x)
        x = json.loads(x)
        
        publish.single(topic, payload=str(x), keepalive=5, hostname=host)
        time.sleep(0.5)
        i += 1
        os.system('cls')
        print('Topic: {}\nArchivo: {}'.format(topic, archivo))
        print('Llevo {} registros completados de {}'.format(i, len(data)))


    # ------------------ Automatico
    # print(len(data))
    # data = data[0:a]
    # print(len(data))

    # tmp = list()
    # for reg in data:
    #     one_json = json.dumps(reg)
    #     one_json = json.loads(one_json)
    #     print(one_json, type(one_json))
        # if "compressor_1" in one_json:
            # print(reg["compressor_1"]["time"])
