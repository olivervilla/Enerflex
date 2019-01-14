import os
import json

path = os.path.realpath(__file__)
path = path[:path.find('ids.py')]

with open(path + "init.json", "r") as f:
    info = json.load(f)
    for pozo in info["pozos"]:
        plc1 = pozo["ids"][0]
        br20 = pozo["ids"][1]
        plc2 = pozo["ids"][2]
        print('{} {} {}'.format(plc1, br20, plc2))