from pyModbusTCP.client import ModbusClient
from datetime import timedelta as td
from datetime import datetime as dt
from subprocess import Popen, PIPE
from enviroment import Address
from threading import Thread
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import pyModbusTCP.utils as decoder
import win_inet_pton
import sqlite3
import socket
import time
import json
import os


class EncodeToJson():
    def __init__(self, name_well, plc1, br20, plc2, ptp, ptr, pld, ttp, onETM):
        self.__name = name_well
        self._flg_plc1 = plc1
        self._flg_br20 = br20
        self._flg_plc2 = plc2
        self.__realtime = 0
        self.__well = dict()
        self.__compressor_1 = dict()
        self.__compressor_2 = dict()
        self.__linealdata = dict()
        # Encontrar que numeros faltan
        self.ids = [ptp, ptr, pld, ttp]
        self.count = 0
        self.etm = onETM

    def set_well(self, devices, fecha, tiempo):
        if devices == None:
            devices = [None]*20
        elif len(devices) < 20:
            devices += [None]*(20-len(devices))

        self.fecha = fecha
        self.tiempo = tiempo
        # ptp - 2   ptr - 7
        # pld - 12  ttp - 17
        i = list()
        for pos in self.ids:
            if pos == 1 or pos == 5:
                i.append(2)
            elif pos == 2 or pos == 6:
                i.append(7)
            elif pos == 3 or pos == 7:
                i.append(12)
            elif pos == 4 or pos == 8:
                i.append(17)
            elif pos == None:
                i.append(None)
        
        self.__well = {
            "name": self.__name,
            "date": fecha,
            "time": tiempo,
            "ptp": devices[i[0]] if i[0] != None else None,
            "ptr": devices[i[1]] if i[1] != None else None,
            "pld": devices[i[2]] if i[2] != None else None,
            "ttp": devices[i[3]] if i[3] != None else None
        }

    def __model_compressor(self, name_compressor, inputs_1_1, inputs_1_2, inputs_2, holding, coils):

        # time = "{}:{}:{}".format(holding[1], holding[2], holding[3]) if holding != None else None
        
        pr = holding[0] if holding != None else None

        # Rutina etm
        rpm = inputs_2[7]
        if self.etm:
            time = self.get_etm(rpm, name_compressor)
        else:
            time = "{}:{}".format(holding[1], holding[2]) if holding != None else None
        
        model = {
            "namecompresor": name_compressor,
            "pr": pr,
            "etm": time,
            # ----------------
            "tts": inputs_1_1[0],
            "pts": inputs_1_1[1],
            "pld2": inputs_1_1[6],
            "tpv": inputs_1_1[9],
            "pdd": inputs_1_2[0],
            "ped": inputs_1_2[1],
            "td": inputs_1_2[2],
            "pdgc": inputs_1_2[3],
            "pegc": inputs_1_2[4],
            "tgc": inputs_1_2[5],
            "fcd": inputs_1_2[6],
            "vgi": inputs_1_2[7],
            "fcgc": inputs_1_2[8],
            "fegc": inputs_1_2[9],
            "tad": inputs_1_2[10],
            "tagc": inputs_1_2[14],
            # ----------------
            "pttpp": inputs_2[0],
            "pttrp": inputs_2[1],
            "ptsp": inputs_2[3],
            "prdp": inputs_2[4],
            "ttdp": inputs_2[5],
            "fep": inputs_2[6],
            "rpmp": inputs_2[7],
            # ----------------
            "df": coils[0],
            "pc": coils[1],
            "di": coils[2]
        }
        return model

    def set_compressor_1(self, name, inputs_1_1, inputs_1_2, inputs_2, holding, coils):
        self.__compressor_1 = self.__model_compressor(
            name, inputs_1_1, inputs_1_2, inputs_2, holding, coils)

    def set_compressor_2(self, name, inputs_1_1, inputs_1_2, inputs_2, holding, coils):
        self.__compressor_2 = self.__model_compressor(
            name, inputs_1_1, inputs_1_2, inputs_2, holding, coils)

    def set_realtime(self, isRealTime):
        self.__realtime = 1 if isRealTime else 0

    def get_dict(self):
        model = dict()
        # No se actualiza (status) por que well ya esta definido
        model["well_1"] = self.__well
        if self._flg_plc1:
            model["compressor_1"] = self.__compressor_1
        if self._flg_plc2:
            model["compressor_2"] = self.__compressor_2
        model["realtime"] = self.__realtime
        model["status"] = self.status
        # print(self.status)
        return model, json.dumps(model)

    def get_lineal_dict(self):
        self.__linealdata.update(self.__well)

        if self._flg_plc1:
            keys = self.__compressor_1.keys()
            values = self.__compressor_1.values()
            for i in range(0, len(keys)):
                keys[i] = str(keys[i] + '_1')
            self.__linealdata.update(dict(zip(keys, values)))

        if self._flg_plc2:
            keys = self.__compressor_2.keys()
            values = self.__compressor_2.values()
            for i in range(0, len(keys)):
                keys[i] = str(keys[i] + '_2')
            self.__linealdata.update(dict(zip(keys, values)))
        return self.__linealdata


    # FIXME: Checar porque falla el br20 y no manda el error (modbusprotocol)
    code_errors = {
        0: "Unknown Error",
        1: "Illegal Function",
        2: "Illegal Data Address",
        3: "Illegal Data Value",
        4: "Failure In Associated Device ",
        5: "Acknowledge",
        6: "Busy, Rejected Message",
        7: "Negative Acknowledgement ",
        8: "Memory Parity Error",
        10: "Gateway Path Unavailable",
        11: "Gateway Target Device Failed to respond"
    }

    def get_system_errors(self, errors, fecha, tiempo):
        data = ''
        for error in errors:
            # if error[1] != 0:
            data = data + '{} {} | {}: {}\n'.format(
                    fecha, tiempo, error[0], self.code_errors[error[1]])
        return data

    def set_code_errors(self, errors):
        tmp = list()
        for bit in errors:
            bit = '1' if bit == True else '0'
            tmp.append(bit)
        tmp.reverse()
        tmp = ''.join(tmp)
        tmp = int(tmp, 2)
        self.status = tmp

    def get_etm(self, rpm, name_compressor):
        # fecha, tiempo = dt.today().isoformat().split('T')
        try:
            name_compressor = self.__name+'_{}'.format(name_compressor)
            day = 24*3600

            db = sqlite3.connect(Address.DATABASE_FOLDER, )
            c = db.cursor()
            sql = """SELECT startTime, limitTime, onlineTime, actualTime, isOnline FROM time_operation WHERE name = '{}'""".format(
                name_compressor)
            c.execute(sql)

            # start = Registra la hora que se registro el ultimo funcionamiento de la compresora
            # limit = Registra un dia mas al actual con hora 6 am como limit
            # online = Registra el tiempo acumulado de operacion
            # actual = Registra el tiempo actual anterior para sumar al acumulado
            # isOnline = Registra el estado anterior de la compresora
            start, limit, online, actual, isOnline = c.fetchone()

            # print(start, limit, online, actual, isOnline)

            try:
                now = dt.strptime("{0} {1}".format(self.fecha, self.tiempo), "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                now = dt.strptime("{0} {1}".format(self.fecha, self.tiempo), "%Y-%m-%d %H:%M:%S")
            
            # timetest = 20*3600+15*60

            now = time.mktime(now.timetuple())
            now = now - 6*3600 #+ timetest
            
            # Si el tiempo guardado o el tiempo de operacion es mayor a un dia
            if online >= day or now > limit:
                today = dt.today() - td(hours=6)
                limit_now = dt(today.year, today.month, today.day+1, 5, 59)
                limit_now = time.mktime(limit_now.timetuple())
                
                sql = """UPDATE time_operation 
                         SET startTime={hours}, limitTime={limit}, onlineTime=0, actualTime={hours}
                         WHERE name='{name}';""".format(name=name_compressor, hours=now, limit=limit_now)
                c.execute(sql)
                db.commit()
                online = 0
                start = now - 1
                actual = start
            
            if rpm != None:
                if rpm > 100:
                    if isOnline == 0:
                        sql = """UPDATE time_operation SET isOnline=1
                                WHERE name='{name}';""".format(name=name_compressor)
                        c.execute(sql)
                    if not online > 0: # Si no hay acumulado ponemos el etm actual
                        etm = now - start # Tiempo de operacion
                    else: # Si hay acumulado debemos sumar
                        etm = online + (now - actual)
                    sql = """UPDATE time_operation SET actualTime={hours}, onlineTime={accum} 
                            WHERE name='{name}';""".format(name=name_compressor, hours=now, accum=etm)
                    c.execute(sql)
                    db.commit()
                else:
                    # Debemos dejar de contar por lo tanto etm el tiempo guardado
                    # Actualiza tanto actual como start hasta que vuelva funcionar
                    sql = """UPDATE time_operation 
                            SET actualTime={hours}, startTime={hours}, isOnline=0 
                            WHERE name='{name}';""".format(name=name_compressor, hours=now)
                    c.execute(sql)
                    db.commit()
                    etm = online
            else:
                # Debemos esperar 5 min si estaba online, si no dejar de contar
                if isOnline == 0 or (now - actual) >= 5*60:
                    # Al no estar operativa etm debe ser el acumulado
                    sql = """UPDATE time_operation 
                            SET actualTime={hours}, startTime={hours}, isOnline=0
                            WHERE name='{name}';""".format(name=name_compressor, hours=now)
                    c.execute(sql)
                    db.commit()
                    etm = online
                elif isOnline == 1:
                    etm = online

            if not etm > day: # Verificamos que el calculo etm no de mas de un dia
                try:
                    etm = dt.strptime(str(td(seconds=etm)),"%H:%M:%S").strftime("%H:%M")
                except ValueError:
                    etm = dt.strptime(str(td(seconds=etm)),"%H:%M:%S.%f").strftime("%H:%M")
            else:
                etm = None

            # os.system('cls')
            # print('Estado: {:<15}'.format("On" if isOnline == 1 else "Off"))
            # print('Empezo a trabajar: {:<25}'.format(dt.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")))
            # print('Hora actual: {:<25}'.format(dt.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")))
            # print('Fecha limite: {:<25}'.format(dt.fromtimestamp(limit).strftime("%Y-%m-%d %H:%M:%S")))
            # print('ETM {}: {:<25}'.format(name_compressor, etm))

            db.commit()
            db.close()

            return etm
        except sqlite3.Error as e:
            print(self.__name, 'DB - etm process', e)
            return None


# TODO: Tarda 7.9 s en saber que no esta conectado el radio

class ModbusTCP():
    def __init__(self, ip, name_well, name_compressors, host_mqtt, topic_data, topic_actions=None, ip_br20=None, puerto=502, scanrate=0.1,
                 id_plc1=None, id_br20=None, id_plc2=None, id_ptp=1, id_ptr=2, id_pld=3, id_ttp=4, br20_unique=True, tout=5, get_etm=False):

        self.cliente = ModbusClient(host=ip, port=puerto, timeout=tout)

        # if id_plc1 != id_br20 and id_br20 != id_plc2 and id_plc2 != id_plc1:
        if len(name_compressors) == 1:
            self._flg_plc1 = True if id_plc1 != None and name_compressors[0] != None else False
            self._flg_plc2 = True if self._flg_plc1 == False else False
        elif len(name_compressors) == 2:
            self._flg_plc1 = True if id_plc1 != None and name_compressors[0] != None else False
            self._flg_plc2 = True if id_plc2 != None and name_compressors[1] != None else False
        self._flg_br20 = True if id_br20 != None else False

        if self._flg_plc1:
            # self._tcp_plc1 = ModbusClient(host=ip, port=puerto, unit_id=id_plc1, timeout=tout)
            self.id_plc1 = id_plc1

            self.tries_plc1 = 0
            self._name_compressor1 = str(name_compressors[0])

        if self._flg_br20:
            if ip_br20 == None:
                self._tcp_br2 = ModbusClient(
                    host=ip, port=puerto, unit_id=id_br20, timeout=tout)
            else:
                self._tcp_br2 = ModbusClient(
                    host=ip_br20, port=puerto, unit_id=id_br20, timeout=tout)
            
            # self.ip_br20 = ip_br20 if ip_br20 != None else None
            # if ip_br20 != None:
            #     self._tcp_br2 = ModbusClient(host=ip_br20, port=puerto, unit_id=id_br20, timeout=tout)
            # else:
            #     self.id_br20 = id_br20
            
            self._flg_unique = br20_unique
            self.tries_br20 = 0

        if self._flg_plc2:
            # self._tcp_plc2 = ModbusClient( host=ip, port=puerto, unit_id=id_plc2, timeout=tout)
            self.id_plc2 = id_plc2

            self.tries_plc2 = 0
            if self._flg_plc1:
                self._name_compressor2 = str(name_compressors[1])
            else:
                self._name_compressor2 = str(name_compressors[0])

        self._ip = ip
        self._scanrate = scanrate
        self._hostmqtt = host_mqtt
        self._topic = topic_data
        self._actions = topic_actions
        self.tries_radio = 0
        self.how_many_null = 100
        self.json_ok = None
        self.status = [False]*15

        self.sensors = 0
        self.sensors += 1 if id_ptp != None else 0
        self.sensors += 1 if id_ptr != None else 0
        self.sensors += 1 if id_pld != None else 0
        self.sensors += 1 if id_ttp != None else 0
        
        self._name = name_well.lower().replace("-", " ").replace(" ", "_")
        self._errors = list()
        self.__create_table()
        self._ecd = EncodeToJson(self._name, plc1=self._flg_plc1, br20=self._flg_br20, plc2=self._flg_plc2,
            ptp=id_ptp, ptr=id_ptr, pld=id_pld, ttp=id_ttp, onETM=get_etm)

        # Thread(name='Actions {}'.format(self._name), target=self.__subscribe_mqtt).start()
        Thread(name='Backup {}'.format(self._name), target=self.__save_data_daily).start()
        

    def __create_table(self):
        db = sqlite3.connect(Address.DATABASE_FOLDER, )
        c = db.cursor()
        sql = """CREATE TABLE IF NOT EXISTS {}('id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'name' TEXT NOT NULL,'time' NUMERIC,'date' NUMERIC,
            'ptp' NUMERIC, 'ptr' NUMERIC,'pld' NUMERIC,'ttp' NUMERIC, 'namecompresor_1' TEXT, 'etm_1' NUMERIC,'pr_1' NUMERIC, 'rpmp_1' NUMERIC,
            'fep_1'NUMERIC,'ttdp_1' NUMERIC,'prdp_1' NUMERIC, 'ptsp_1' NUMERIC,'pttrp_1' NUMERIC,'pttpp_1' NUMERIC,'tagc_1' NUMERIC, 'tad_1' NUMERIC,
            'fegc_1' NUMERIC,'fcgc_1' NUMERIC,'vgi_1' NUMERIC, 'fcd_1' NUMERIC,'tgc_1' NUMERIC,'pegc_1' NUMERIC,'pdgc_1' NUMERIC, 'td_1' NUMERIC,
            'ped_1' NUMERIC,'pdd_1' NUMERIC,'tpv_1' NUMERIC,'pld2_1' NUMERIC, 'pts_1' NUMERIC,'tts_1' NUMERIC,'di_1' NUMERIC, 'pc_1' NUMERIC,'df_1' NUMERIC,
            'namecompresor_2' TEXT, 'etm_2' NUMERIC, 'pr_2' NUMERIC,'rpmp_2' NUMERIC,'fep_2' NUMERIC,'ttdp_2' NUMERIC, 'prdp_2' NUMERIC,'ptsp_2' NUMERIC,
            'pttrp_2' NUMERIC,'pttpp_2' NUMERIC,'tagc_2' NUMERIC,'tad_2' NUMERIC,'fegc_2' NUMERIC,'fcgc_2' NUMERIC, 'vgi_2' NUMERIC,'fcd_2' NUMERIC,
            'tgc_2' NUMERIC, 'pegc_2' NUMERIC,'pdgc_2' NUMERIC, 'td_2' NUMERIC,'ped_2' NUMERIC,'pdd_2' NUMERIC,'tpv_2' NUMERIC, 'pld2_2' NUMERIC,
            'pts_2' NUMERIC, 'tts_2' NUMERIC,'di_2' NUMERIC, 'pc_2' NUMERIC,'df_2' NUMERIC)""".format(self._name)
        c.execute(sql)
        if self._flg_plc1:
            sql = """INSERT INTO time_operation(name, limitTime, onlineTime, startTime, actualTime, isOnline) 
                    SELECT * FROM (SELECT '{0}', 0, 0, {1}, 0, 0) AS tmp 
                    WHERE NOT EXISTS ( SELECT name FROM time_operation WHERE name = '{0}') LIMIT 1;""".format(
                        self._name+'_{}'.format(self._name_compressor1), int(time.time()-6*3600))
            c.execute(sql)
        if self._flg_plc2:
            sql = """INSERT INTO time_operation(name, limitTime, onlineTime, startTime, actualTime, isOnline) 
                    SELECT * FROM (SELECT '{0}', 0, 0, {1}, 0, 0) AS tmp 
                    WHERE NOT EXISTS ( SELECT name FROM time_operation WHERE name = '{0}') LIMIT 1;""".format(
                        self._name+'_{}'.format(self._name_compressor2), int(time.time()-6*3600))
            c.execute(sql)
        sql = """INSERT INTO connection_status(name, ip) SELECT * FROM (SELECT '{0}', '{1}') AS tmp 
                WHERE NOT EXISTS ( SELECT name FROM connection_status WHERE name = '{0}') LIMIT 1;""".format(self._name, self._ip)
        c.execute(sql)
        db.commit()
        db.close()


    def __routine_plc(self, plc, id):
        # if id == 1:
        #     plc.unit_id(self.id_plc1)
        # elif id == 2:
        #     plc.unit_id(self.id_plc2)

        if not plc.is_open():
            if not plc.open():
                 # Title: error
                self._errors.append(
                    ("PLC{} Connection".format(id), plc.last_except()))
                plc.close()
                self.tries_radio += 1
                return [None]*13, [None]*15, [None]*8, None, [None]*3
        if plc.is_open():
            self.tries_radio = 0
            
            plc4 = plc.read_discrete_inputs(0, 3)
            if plc4 != None:
                fl_bp = False
                for i in range(0, len(plc4)):
                    plc4[i] = 1 if plc4[i] else 0
            else:
                fl_bp = True
                # Title: error
                self._errors.append(
                    ("PLC{} Booleans Package".format(id), plc.last_except()))
                plc4 = [None]*3
            # plc4 = [None]*3
            fl_bp = True
            time.sleep(0.1)

            # plc3 = plc.read_holding_registers(0, 4)
            # if plc3 != None:
            #     fl_hp = False
            # else:
            #     fl_hp = True
            #     # Title: error
            #     self._errors.append(
            #         ("PLC{} Holding Package".format(id), plc.last_except()))
            #     plc3 = None
            plc3 = None
            fl_hp = True
            # time.sleep(0.1)

            tmp = plc.read_input_registers(148, 2)
            if tmp != None:
                tmp = decimal_list_to_float_litEndian(tmp)
            else:
                tmp = [None]
            time.sleep(0.1)

            # plc2 = plc.read_input_registers(134, 16)
            plc2 = plc.read_input_registers(134, 14)
            if plc2 != None:
                fl_ip1 = False
                plc2 = decimal_list_to_float_litEndian(plc2)
            else:
                fl_ip1 = True
                # Title: error
                self._errors.append(
                    ("PLC{} Inputs Package 1".format(id), plc.last_except()))
                # plc2 = [None]*8
                plc2 = [None]*7

            plc2.extend(tmp)

            time.sleep(0.1)

            plc1_1 = plc.read_input_registers(0, 26)
            if plc1_1 != None:
                fl_ip2 = False
                plc1_1 = decimal_list_to_float_litEndian(plc1_1)
            else:
                fl_ip2 = True
                # Title: error
                self._errors.append(
                    ("PLC{} Inputs Package 2".format(id), plc.last_except()))
                plc1_1 = [None]*13

            time.sleep(0.1)

            plc1_2 = plc.read_input_registers(26, 30)
            if plc1_2 != None:
                fl_ip3 = False
                plc1_2 = decimal_list_to_float_litEndian(plc1_2)
            else:
                fl_ip3 = True
                # Title: error
                self._errors.append(
                    ("PLC{} Inputs Package 3".format(id), plc.last_except()))
                plc1_2 = [None]*15

            if id == 1:
                self.status[4] = fl_bp
                self.status[5] = fl_hp
                self.status[6] = fl_ip1
                self.status[7] = fl_ip2
                self.status[8] = fl_ip3
            elif id == 2:
                self.status[9] = fl_bp
                self.status[10] = fl_hp
                self.status[11] = fl_ip1
                self.status[12] = fl_ip2
                self.status[13] = fl_ip3

            if fl_bp and fl_hp and fl_ip1 and fl_ip2 and fl_ip3:
                if id == 1:
                    self.tries_plc1 += 1
                elif id == 2:
                    self.tries_plc2 += 1
            else:
                if id == 1:
                    self.tries_plc1 = 0
                elif id == 2:
                    self.tries_plc2 = 0

            return plc1_1, plc1_2, plc2, plc3, plc4

    def __routine_br20(self, br20):
        count = 0
        rb_devices = None
        rb_info = None
        while rb_devices == None and count <= 3:
            # print('Asking br20 of '+self._name)
            if not br20.is_open():
                if not br20.open():
                    self._errors.append(("BR20 Connection", br20.last_except()))
                    # br20.close()
                    count += 1
                    time.sleep(0.3)
                    self.tries_radio += 1

            if br20.is_open():
                self.tries_radio = 0
                rb_info = None
                # rb_info = br20.read_holding_registers(0, 10)
                # if rb_info == None:
                #     # Title: error
                #     self._errors.append(("BR20 Info", br20.last_except()))
                #     rb_info = [None]*10

                if self._flg_unique == None:
                    rb_devices = br20.read_holding_registers(10, self.sensors*10)
                elif self._flg_unique:
                    # Lee todos
                    # TODO: Que se lean por el numero de sensores y no fijo
                    rb_devices = br20.read_holding_registers(10, 60)
                elif not self._flg_unique:
                    # Leera en el texto
                    try:
                        with open(Address.DATA_FOLDER + 'br20_ip{}.txt'.format(self._ip.replace('.', '')), 'r+') as f:
                            a = str(f.read())
                            a = a.replace('[', '').replace(']', '').split(',')
                            for i in range(0, len(a)):
                                try:
                                    a[i] = float(a[i]) if a[i] != ' None' and a[i] != 'None' else None
                                except ValueError:
                                    a[i] = None
                            rb_devices = a + [None]*10
                    except IOError:
                        rb_devices = [None]*20
                        return rb_info, rb_devices

                if rb_devices != None and (self._flg_unique or self._flg_unique == None):
                    fl_br20 = False
                    rb_devices = decimal_list_to_float_bigEndian(rb_devices)
                    rb_devices += [None]*(20 - len(rb_devices))
                else:
                    # Title: error
                    count += 1
                    fl_br20 = True
                    self._errors.append(("BR20 Sensors", br20.last_except()))
                    # rb_devices = [None]*20

                self.status[14] = fl_br20

                if fl_br20:
                    if self._flg_unique or self._flg_unique == None:
                        self.tries_br20 += 1
                    elif rb_devices == [None]*20:
                        self.tries_br20 += 1
                else:
                    self.tries_br20 = 0

            # print('Data br20: {} Count: {}'.format(rb_devices, count))
        if count >= 3 or rb_devices == None:
            rb_info, rb_devices = [None]*10, [None]*20

        if len(rb_devices) > 20:
            with open(Address.DATA_FOLDER + 'br20_ip{}.txt'.format(self._ip.replace('.', '')), 'w+') as f:
                f.write(str(rb_devices[20:]))
            time.sleep(0.1)

        return rb_info, rb_devices

    def run_once(self):
        self.fecha, self.tiempo = dt.today().isoformat().split('T')

        t0 = time.time()

        # Title: BR20
        if self._flg_br20:
            rb_info, rb_devices = self.__routine_br20(self._tcp_br2)

            # if self.ip_br20 != None:
            #     rb_info, rb_devices = self.__routine_br20(self._tcp_br2)
            # else:
            #     self.cliente.unit_id(self.id_br20)
            #     rb_info, rb_devices = self.__routine_br20(self.cliente)

            self._ecd.set_well(rb_devices, self.fecha, self.tiempo)
        else:
            self._ecd.set_well(None, self.fecha, self.tiempo)

        t1 = time.time()

        # Title: PLC1
        if self._flg_plc1:
            # plc1_1, plc1_2, plc2, plc3, plc4 = self.__routine_plc(self._tcp_plc1, 1)
            self.cliente.unit_id(self.id_plc1)
            plc1_1, plc1_2, plc2, plc3, plc4 = self.__routine_plc(self.cliente, 1)
            self._ecd.set_compressor_1(
                self._name_compressor1, plc1_1, plc1_2, plc2, plc3, plc4)

        t2 = time.time()

        # Title: PLC2
        if self._flg_plc2:
            # plc1_1, plc1_2, plc2, plc3, plc4 = self.__routine_plc(self._tcp_plc2, 2)
            self.cliente.unit_id(self.id_plc2)
            plc1_1, plc1_2, plc2, plc3, plc4 = self.__routine_plc(self.cliente, 2)
            self._ecd.set_compressor_2(
                self._name_compressor2, plc1_1, plc1_2, plc2, plc3, plc4)

        self._ecd.set_realtime(True)

        t3 = time.time()
        # -- ERRORES
        self.sync_errors()

        # Title: Create json
        self._ecd.set_code_errors(self.status)
        data_dict, data_json = self._ecd.get_dict()
        # self.print_nice(self.status)
        self.update_status_connection()

        # Title: Base de datos

        self.__save_in_db(self._name)
        # Title: Mqtt
        t4 = time.time()
        self.__publish_mqtt(data_json)
        # self.__save_data(data_json)
        t5 = time.time()

        #print(data_json)

        # Title: Save in log
        if len(self._errors) > 0:
            self.__save_log(self._ecd.get_system_errors(self._errors, self.fecha, self.tiempo))
            self._errors[:] = []

        t6 = time.time()

        self.__save_times([t1-t0, t2-t1, t3-t2, t5-t4, t6-t0])
        self.__validate_data(data_dict)


    def run_loop(self):
        while True:
            self.run_once()
            time.sleep(self._scanrate)

    def print_nice(self, errors):
        os.system('cls')
        for i in range(0, len(names)):
            print("{1} --- {0}".format(names[i], errors[i]))
        print('Radio {} - PLC1 {} - PLC2 {} -  BR20 {}'.format(self.tries_radio, self.tries_plc1, self.tries_plc2, self.tries_br20))
        # print('Radio {} - PLC1 {} - BR20 {}'.format(self.tries_radio, self.tries_plc1, self.tries_br20))
        time.sleep(0.5)

    def sync_errors(self):
        # PLCs
        if self._flg_plc1:
            self.status[1] = True if self.tries_plc1 >= 3 else False
            if self.status[1]:
                self.status[4] = False
                self.status[5] = False
                self.status[6] = False
                self.status[7] = False
                self.status[8] = False
        if self._flg_plc2:
            self.status[2] = True if self.tries_plc2 >= 3 else False
            if self.status[2]:
                self.status[9] = False
                self.status[10] = False
                self.status[11] = False
                self.status[12] = False
                self.status[13] = False
        if self._flg_br20:
            self.status[3] = True if self.tries_br20 >= 2*3 else False
            if self.status[3]:
                self.status[14] = False

        if self._flg_plc1 and self._flg_plc2 and self._flg_br20:
            # FIXME: se suma mas 6 por las dos vueltas del br20, hacer mejor calculo
            self.status[0] = True if self.tries_radio > 9 + 6 else False
        elif (self._flg_plc1 or self._flg_plc2) and self._flg_br20:
            self.status[0] = True if self.tries_radio > 6 + 6 else False

        if self.status[0]:
            for i in range(1, len(self.status)):
                self.status[i] = False

    def update_status_connection(self):
        try:
            db = sqlite3.connect(Address.DATABASE_FOLDER, )
            c = db.cursor()

            tmp = list()
            for bit in self.status:
                bit = 1 if bit == True else 0
                tmp.append(bit)

            sql = """UPDATE connection_status SET isConnected={}, isOnPLC1={}, isOnPLC2={}, isOnBR20={}, isOkCoil1={}, 
                     isOkHold1={}, isOkInputs1_1={}, isOkInputs1_2={}, isOkInputs1_3={}, isOkCoil2={}, isOkHold2={}, 
                     isOkInputs2_1={}, isOkInputs2_2={}, isOkInputs2_3={}, isOkSensors={}""".format(*tmp)
            sql = sql + " WHERE name='{}';".format(self._name)
            c.execute(sql)
            db.commit()
            db.close()
            time.sleep(0.1)
        except sqlite3.Error as e:
            print(self._name, 'DB - updating connection', e)

    def __save_in_db(self, table):
        try:
            db = sqlite3.connect(Address.DATABASE_FOLDER, )
            c = db.cursor()
            data = self._ecd.get_lineal_dict()
            var = tuple(data.keys())
            values = list()
            for i in range(0, len(var)):
                values.append(data[var[i]])
            sql = "INSERT INTO {}{} VALUES({}?)".format(
                table, var, '?,'*(len(var)-1))
            c.execute(sql, values)
            db.commit()
            db.close()
        except Exception as e:
            print(self._name, 'DB - saving data', e)
            pass

    def __publish_mqtt(self, data):
        try:
            publish.single(self._topic, payload=data, keepalive=5, hostname=self._hostmqtt)
            # publish.single(self._topic, payload=data, keepalive=5, hostname="187.189.81.116")
        except socket.error as e:
            print(self._name, 'MQTT - sending data', e)
            self.__save_data(data)

    def __on_action_recive(self, client, userdata, message):
        print('Action recived')
        print(message.payload)

    def __subscribe_mqtt(self):
        try:
            # subscribe.simple(self._actions, hostname=self._hostmqtt, keepalive=5)
            subscribe.callback(self.__on_action_recive, self._actions, hostname=self._hostmqtt, keepalive=5)

            # TODO: El formato y las acciones a tomar.

        except Exception as e:
            print(self._name, 'MQTT - Subscription', e)

    def __validate_data(self, data):
        nulls = 0
        if "compressor_1" in data:
            for value in data["compressor_1"].values():
                if value == None:
                    nulls += 1
        if "compressor_2" in data:
            for value in data["compressor_2"].values():
                if value == None:
                    nulls += 1
        if "well_1" in data:
            for value in data["well_1"].values():
                if value == None:
                    nulls += 1
        
        if nulls < self.how_many_null:
            self.how_many_null = nulls
            self.json_ok = data

    def __save_data(self, data):
        with open(Address.DATA_FOLDER + 'data_{}.txt'.format(self._name), 'a+') as f:
            f.write(str(data)+'\n')

    def __save_data_daily(self):
        while True:
            time.sleep(5*60)
            if self.json_ok != None:
                self.json_ok = json.dumps(self.json_ok)
                with open(Address.BACKUP_DAILY_FOLDER +'bc{}_{}.txt'.format(self.fecha.replace('-', ''), self._name), 'a+') as f:
                    f.write(str(self.json_ok)+'\n')
            self.how_many_null = 100
            self.json_ok = None
        
    def __save_log(self, data):
        with open(Address.LOGS_FOLDER + 'log_{}.txt'.format(self._name), 'a+') as f:
            f.write(str(data)+'\n')

    def __isEnableWifi(self):
        arg = "if netcat -z google.com 80; then echo \"Ok\"; else echo \"Noup\"; fi"
        p = Popen(arg, shell=True, stdout=PIPE)
        data = p.communicate()[0].split('\n')[0]
        if data == "Ok":
            return True
        else:
            return False

    def __save_times(self, data):
        with open(Address.LOGS_FOLDER + 'time_{}.txt'.format(self._name), 'a+') as f:
            f.write(
                'FECHA {} {} | PLC1: {:.4f} | BR20: {:.4f} | PLC2: {:.4f} | Mqtt: {:.4f} | TOTAL: {:.4f}\n'.format(
                    self.fecha, self.tiempo, data[0], data[1], data[2], data[3], data[4]
                ))


def decimal_list_to_float_litEndian(values):
    p1 = decoder.word_list_to_long(values, big_endian=False)
    l1 = list()
    for register in p1:
        tmp = decoder.decode_ieee(register)
        if str(tmp) != 'nan':
            tmp = round(float(tmp), 4)
            l1.append(tmp)

        else:
            l1.append(None)
    return l1


def decimal_list_to_float_bigEndian(values):
    p1 = decoder.word_list_to_long(values, big_endian=True)
    l1 = list()
    for register in p1:
        tmp = decoder.decode_ieee(register)
        if str(tmp) != 'nan':
            tmp = round(float(tmp), 4)
            l1.append(tmp)
        else:
            l1.append(None)
    return l1

names = [   
    'Radio - Conexion perdida',
    'PLC1 - No responde',
    'PLC2 - No responde',
    'BR20 - No responde',
    'PLC1 - Coils Package Loss',
    'PLC1 - Holding Package Loss',
    'PLC1 - Inputs Package 1 Loss',
    'PLC1 - Inputs Package 2 Loss',
    'PLC1 - Inputs Package 3 Loss',
    'PLC2 - Coils Package Loss',
    'PLC2 - Holding Package Loss',
    'PLC2 - Inputs Package 1 Loss',
    'PLC2 - Inputs Package 2 Loss',
    'PLC2 - Inputs Package 3 Loss',
    'BR20 - Data Sensors Loss'
]
