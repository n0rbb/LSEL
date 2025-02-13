import socket
import pickle

def InitializeDomoticModel():
    clients = []
    clients.append({'id': '0', 'name': 'kitchen'})
    clients.append({'id': '1', 'name': 'living'})
    clients.append({'id': '2', 'name': 'room'})

    valid_clients = [i['id'] for i in clients]

    sensors = []
    sensors.append({'attribute': 'T', 'name': 'Temperature', 'units': 'C'})
    sensors.append({'attribute': 'B', 'name': 'Brightness', 'units': 'Lux'})
    sensors.append({'attribute': 'N', 'name': 'Noise', 'units': 'dB'})
    #sensors.append({'attribute': 'P', 'name': 'Pressure', 'units': 'mBar'})
    #sensors.append({'attribute': 'H', 'name': 'Humidity', 'units': '%%rH'})

    valid_sensors = [i['attribute'] for i in sensors]
    return clients, valid_clients, sensors, valid_sensors

def GetNumericValue (attribute, units):
    value = raw_input("[Input %s value][x(%s)???]\n" % (attribute, units))
    print("[%s]=[%s]\n" % (attribute, value))
    return value

def PrintMessage(message):
    print('\n[MESSAGE]')
    print('[address] = [%s]' % message['address'])
    print('[client] = [%s]' % message['client'])
    print('[sensor] = [%s]' % message['sensor'])
    print('[value] = [%s]' % message['value'])

def SendMessage(message, server):
    string_to_send = 'NODE_INFO;' + message['client'] + ';' + message['sensor'] + ';' + message['value']
    print('\n[SEND]=[%s]' % string_to_send)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((server['host'], server['port']))
    server_socket.send(string_to_send)
    server_socket.close()

def ParseMessage(data):
    header, received_client, received_sensor, received_value = data.split(';')
    message = {}
    message['client'] = received_client
    message['sensor'] = received_sensor
    message['value'] = received_value
    return message
