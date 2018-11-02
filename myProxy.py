# encoding=utf-8

import socket

def proxy():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 9800))
    sock.listen(5)

    while True:
        print 'server waiting...'
        conn, addr = sock.accept()
        response = b''

        client_data = conn.recv(1024)
        while client_data:
            response += client_data
            client_data = conn.recv(1024)
        print response
        conn.sendall(response.encode('utf-8'))

if __name__ == '__main__':
    proxy()
