#!/usr/bin/env python
"""
Domotic Server
"""

import socket
import datetime
import select
import sys
import re
import argparse
from DomoticLib import ParseMessage
from DomoticLib import PrintMessage

# Build webpage information
def parse_website(addr, refresh):
    try:
        file_handler = open(addr,'r')
        header = """HTTP/1.1 200 OK
Content-Type: text/html\r\n\r\n"""
        data = header + file_handler.read()
        thetime = datetime.datetime.now().time()
        data = data.replace('[hour]', str(thetime.hour), 1)
        data = data.replace('[minute]', str(thetime.minute), 1)
        data = data.replace('[second]', str(thetime.second), 1)
        for i in range(0,3):
            for j in range(0,4):
                if (node_data[i][j] == None):
                    data = data.replace('[node_data]', '', 1)
                else:
                    data = data.replace('[node_data]', str(node_data[i][j]), 1)
        if refresh > 0:
            data = data.replace('<head>', '<meta http-equiv="refresh" content="' + str(refresh) + '" />\n<head>', 1)
        file_handler.close()
    except Exception as e:
        # Just in case the file couldn't be opened or parsed
        data = 'HTTP/1.1 404 Not Found\r\n'
    return data

def load_regular_html(addr):
    try:
        file_handler = open(addr,'r')
        header = """HTTP/1.1 200 OK\r\n\r\n"""
        data = header + file_handler.read()
        file_handler.close()
    except Exception as e:
        # Just in case the file couldn't be opened or parsed
        data = 'HTTP/1.1 404 Not Found\r\n'
    return data

# Parse data received from node
def parse_node_info(data):
    message = ParseMessage(data)
    if (int(message['client']) < 3):
        node_data[int(message['client'])][p_sensor[message['sensor']]] = float(message['value'])
    return message

parser = argparse.ArgumentParser(description='DomoticServer',
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--host', default='127.0.0.1', help="Type of sensor")
parser.add_argument('--port', type=int, default=8080, help="Type of sensor")

args = parser.parse_args()
print(args)

p_sensor = {'B': 1, 'T': 2, 'N': 3}

# variables
web_addr = 'index.html'
backlog = 5
remain = 1
refresh = 0
node_data = [[0, None, None, None], [1, None, None, None], [2, None, None, None]]

server = {'host': args.host, 'port': args.port, 'size': 1024}

# Main function
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server['host'], server['port']))
server_socket.listen(backlog)

input_expected = [sys.stdin, server_socket]
output_expected = []

get_addr = re.compile(r'GET \/(\/?[!-z]+) HTTP\/1.[0-1]', re.I)

while remain:
    input_read, output_read, exception_read = select.select(input_expected, output_expected, [])
    for s in input_read:
        if s == server_socket:
            client, address = server_socket.accept()
            data = client.recv(server['size'])
            MatchObject = get_addr.search(data)
            if re.search('GET / HTTP/1.[0-1]', data):
                print('\n[SERVE MAIN WEBPAGE]\n[address] = [%s]' % address[0])
                # Serve main webpage and parse it to substitute tags
                data = parse_website(web_addr, refresh)
                client.send(data)
            elif MatchObject:
                # Serve different HTTP GET Request
                data = load_regular_html(MatchObject.groups()[0])
                client.send(data)
            elif re.search('NODE_INFO', data):
                refresh = 5
                # Update Sensor data
                message = parse_node_info(data)
                message['address'] = address[0]
                PrintMessage(message)
                data = parse_website(web_addr, refresh)
            else:
                # Simply answer with a Not Found HTTP response
                data = 'HTTP/1.1 404 Not Found\r\n'
                client.send(data)

            client.close()
        elif s == sys.stdin:
            # Read keys and exit
            junk = sys.stdin.readline()
            if 'q' in junk.lower():
                remain = 0
            else:
                print('Press \'q\' to exit server...')

server_socket.close()
