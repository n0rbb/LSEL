#!/usr/bin/env python3

"""
An echo server that uses select to handle multiple clients at a time.
Entering any line of input at the terminal will exit the server.
"""

import select
import socket
import sys
import datetime

def get_date():
    now = datetime.now()
    return f"It’s {now.strftime('%A')}, the {now.day}th of {now.strftime('%B')} of {now.year}"

def get_time():
    now = datetime.now()
    return f"It’s {now.strftime('%H:%M %p')}"

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
                command = data.decode().strip().lower()
                if command == "date":
                    response = get_date()
                elif command == "time":
                    response = get_time()
                else:
                    response = "Unknown command. Please use 'date' or 'time'.\n"
                s.sendall(response.encode())  # sendall() ensures all data is sent
            else:
                s.close()
                inputs.remove(s)

server.close()