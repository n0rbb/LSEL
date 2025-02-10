#!/usr/bin/env python3

"""
An echo client that allows the user to send multiple lines to the server.
Entering a blank line will exit the client.
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
