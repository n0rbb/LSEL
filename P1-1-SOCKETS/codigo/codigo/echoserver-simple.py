#!/usr/bin/env python3

"""
A simple echo server
"""

import socket

host = ''
port = 50000
backlog = 5
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
while True:
    client, address = s.accept()
    data = client.recv(size)
    if data:
        print("Received:", data.decode('utf-8'))
        client.send(data)
    client.close()
