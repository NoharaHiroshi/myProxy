# encoding=utf-8

import socket


def proxy():
    ip = "127.0.0.1"
    port = 9800
    sock = socket.socket()
    sock.bind((ip, port))
    sock.listen(5)
    print "[*] listening on %s:%d" % (ip, port)

    while True:
        print 'server waiting...'
        conn, addr = sock.accept()

        client_data = conn.recv(1024)
        response = str('test')
        sock.sendall(response)

if __name__ == '__main__':
    proxy()
