#!/usr/bin/env python3

"""
A simple echo client
"""

import socket

host = 'localhost'
port = 50000
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
s.send('Hello, world'.encode('utf-8'))
data = s.recv(size).decode('utf-8')
s.close()
print('Received:', data)