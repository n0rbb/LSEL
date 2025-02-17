#!/usr/bin/env python3

"""
A server that receives date and time as commands and acts accordingly
"""

import select
import socket
import sys
from datetime import datetime

# Functions
def get_date():
    now = datetime.now()
    if now.day == 1:
        suffix = "st"
    elif now.day == 2:
        suffix = "nd"
    elif now.day == 3:
        suffix = "rd"
    else:
        suffix = "th"
    return f"It’s {now.strftime('%A')}, the {now.day}{suffix} of {now.strftime('%B')} of {now.year}\n"

def get_time():
    now = datetime.now()
    return f"It’s {now.strftime('%H:%M %p')}\n"

# Loop setup
host = ''
port = 50000
backlog = 5
size = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(backlog)

inputs = [server, sys.stdin]
running = True

# Main loop
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