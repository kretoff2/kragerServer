import socket
import json
from threading import *
from time import time, sleep

servers_load = []

def minimal_number_index(massiv):
    min = massiv[0]
    index = 0
    for i in range(0, len(massiv)):
        if massiv[i] <= min:
            min = massiv[i]
            index = i
    return i

config = None
with open('router_config.json', 'r') as f:
    config = json.load(f)

for el in config["servers"]:
    if config["servers"][el]["status"] == True:
        servers_load.append(0)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1',config['PORT']))
server.listen(100)
print('server started')

while True:
    user, address = server.accept()
    print(f'connected:\t{user}')
    user.send(f'PATH⫓{config["servers"][str(minimal_number_index(servers_load))]["ip"]}⫓{config["servers"][str(minimal_number_index(servers_load))]["port"]}'.encode('utf-8'))


