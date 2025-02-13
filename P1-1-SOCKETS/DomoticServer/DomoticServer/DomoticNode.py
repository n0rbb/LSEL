#!/usr/bin/env python
"""
Node client
"""
import socket
import sys
import argparse

"""
Raspberry client
"""

import socket
from DomoticLib import GetNumericValue, PrintMessage, SendMessage
from DomoticLib import InitializeDomoticModel

parser = argparse.ArgumentParser(description='DomoticNode',
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--host', default='127.0.0.1', help="Type of sensor")
parser.add_argument('--port', type=int, default=8080, help="Type of sensor")

parser.add_argument('--client', default='0', help="Value of client") #, required=True)
parser.add_argument('--sensor', default='T', help="Type of sensor")
parser.add_argument('--value', default='25', help="Value of sensor")

parser.add_argument('--auto', dest='auto', action='store_true')
parser.set_defaults(auto=False)

args = parser.parse_args()
print(args)

server = {'host': args.host, 'port': args.port, 'size': 1024}
clients, valid_clients, sensors, valid_sensors = InitializeDomoticModel()
message = {}

if args.auto:
    # Example: python2 DomoticNode.py --auto --client 2 --sensor N --value 90
    message['address'] = args.host
    message['client'] = args.client
    message['sensor'] = args.sensor
    message['value'] = args.value
    PrintMessage(message)
    SendMessage(message, server)
else:
    while True:
        message['address'] = args.host
        message['client'] = ''
        message['sensor'] = ''
        message['value'] = ''

        print('\n[READY TO SEND MESSAGES]\n')
        while True:
            print('Valid clients:')
            print(valid_clients)
            num_client = raw_input("[Client ID][???]\n")

            if num_client in ['q','Q']:
                exit()

            if num_client in valid_clients:
                break
            print("[ERROR!!!][Client %d is NOT AVAILABLE!!!]\n" % num_client)

        p_client = valid_clients.index(num_client)
        message['client'] = num_client
        print("[Client ID][%s]\n" % message['client'])

        while True:
            print('Valid sensors:')
            print(valid_sensors)
            sensor = raw_input("[Sensor][???]\n")

            if num_client in ['q','Q']:
                exit()

            if sensor in valid_sensors:
                break
            print("[ERROR!!!][Sensor %s is NOT AVAILABLE!!!]\n" % sensor)

        p_sensor = valid_sensors.index(sensor)
        message['sensor'] = sensor
        print("[Sensor][%s]\n" % message['sensor'])

        value = GetNumericValue(sensors[p_sensor]['name'], sensors[p_sensor]['units'])
        if value in ['q','Q']:
            exit()

        message['value'] = value
        print("[Value][%s]\n" % message['value'])

        PrintMessage(message)
        SendMessage(message, server)
