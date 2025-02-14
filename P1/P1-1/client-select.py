#!/usr/bin/env python3

"""
This code is the same as the echoclient example as there is no need
to add more functionality to it, the extra functionality has to be
added to the server
"""

import socket
import sys

host = 'localhost'
port = 50000
size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

print('%', end='', flush=True)  # Equivalent to sys.stdout.write('%')

while True:
    # Read from keyboard
    line = sys.stdin.readline()
    if line == '\n':  # If Enter is pressed without input, exit
        break
    s.sendall(line.encode('utf-8'))  # Encode string to bytes before sending
    data = s.recv(size).decode('utf-8')  # Decode received bytes to string
    print(data, end='')  # Equivalent to sys.stdout.write(data)
    print('%', end='', flush=True)  # Equivalent to sys.stdout.write('%')

s.close()
