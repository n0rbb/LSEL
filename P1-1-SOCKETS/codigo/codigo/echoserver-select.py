#!/usr/bin/env python3

"""
An echo server that uses select to handle multiple clients at a time.
Entering any line of input at the terminal will exit the server.
"""

import select
import socket
import sys

host = ''
port = 50000
backlog = 5
size = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(backlog)

inputs = [server, sys.stdin]
running = True

while running:
    input_ready, _, _ = select.select(inputs, [], [])

    for s in input_ready:
        if s == server:
            # Handle the server socket
            client, address = server.accept()
            inputs.append(client)

        elif s == sys.stdin:
            # Handle standard input
            input_text = input()  # Python 3 uses input() instead of sys.stdin.readline()
            if input_text.strip():
                running = False

        else:
            # Handle all other sockets
            data = s.recv(size)
            if data:
                s.sendall(data)  # sendall() ensures all data is sent
            else:
                s.close()
                inputs.remove(s)

server.close()