import paho.mqtt.subscribe as subscribe
from datetime import datetime as dt
import os
import json

host = "187.217.207.73"
# host = "187.189.81.116"
path = os.path.realpath(__file__)
init_teco = path[:path.find('test')] + "inits\\init_teco.json"
init_mora = path[:path.find('test')] + "inits\\init_mora.json"


def on_message(client, userdata, message):
	# fecha, tiempo = dt.today().isoformat().split('T')
	global name

	os.system('cls')

	print('{:^5}'.format('Mqtt debugger of '+ name + ' in '+host))
	try:
		keys = list()
		values = list()
		data = json.loads(message.payload)
		if 'realtime' in data:
			keys.append('realtime')
			values.append(data['realtime'])
		if 'compressor_1' in data:
			for p in data['compressor_1'].keys():
				keys.append(str(p))
			for p in data['compressor_1'].values():
				values.append(p)
		if 'compressor_2' in data:
			for p in data['compressor_2'].keys():
				keys.append(str(p))
			for p in data['compressor_2'].values():
				values.append(p)
		if 'well_1' in data:
			for p in data['well_1'].keys():
				keys.append(str(p))
			for p in data['well_1'].values():
				values.append(p)
		if 'status' in data:
			keys.append('status')
			values.append(data['status'])

		data = dict(zip(keys, values))
		data = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
		print(data)
		
	except Exception as e:
		print(e)
		print('-'*50)
		print(message.payload)


def start_mqtt_debugger(topic):
	subscribe.callback(on_message, topic, hostname=host, qos=0, keepalive=5)

	
if __name__ == '__main__':
	topics = list()
	with open(init_teco, "r") as f:
		repo = json.load(f)
		for pozo in repo["pozos"]:
				topics.append((str(pozo["nombre"]), str(pozo["topic"])))

	with open(init_mora, "r") as f:
		repo = json.load(f)
		for pozo in repo["pozos"]:
				topics.append((str(pozo["nombre"]), str(pozo["topic"])))

	topics.append(("Pozo Prueba", "/1234/prueba/attrs"))

	for i in range(0, len(topics)):
		print("{0:<5}{1:<20}{2}".format(i+1, topics[i][0], topics[i][1]))

	response = None
	while not type(response) == int:
		try:
			response = int(raw_input('Select a well --$ '))
		except ValueError:
			print('A number')

	name = topics[response-1][0]
	start_mqtt_debugger(topic=topics[response-1][1])
