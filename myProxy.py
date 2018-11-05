# encoding=utf-8

import socket


def server_proxy():
    ip = "127.0.0.1"
    port = 9800
    server_sock = socket.socket()
    server_sock.bind((ip, port))
    server_sock.listen(5)
    print "[*] listening on %s:%d" % (ip, port)
    part = 0

    while True:
        print 'server waiting...'
        conn, addr = server_sock.accept()
        remote_addr = conn.getpeername()
        print remote_addr

        client_data = conn.recv(1024)
        print client_data
        part += 1
        conn.sendall(str(part))
        conn.close()


def client_proxy():
    url = 'http://www.sina.com.cn'
    port = 80
    client_socket = socket.socket()
    client_socket.connect((url, port))
    request_url = 'GET / HTTP/1.1\r\nHost: www.sina.com.cn\r\nConnection: close\r\n\r\n'
    client_socket.send(request_url.encode())
    response = b''
    rec = client_socket.recv(1024)
    while rec:
        response += rec
        rec = client_socket.recv(1024)
    print(response.decode())

if __name__ == '__main__':
    client_proxy()
