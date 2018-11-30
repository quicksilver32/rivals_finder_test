#!/usr/bin/env python

import socket

if __name__ == '__main__':
    TCP_IP = ''
    TCP_PORT = 5005
    BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

    s = socket.socket()
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    print(s)
    print(dir(s))

    conn, addr = s.accept()
    print('Connection address:', addr)
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
    print("received data:", data)
    conn.send(data)  # echo
    conn.close()