# encoding=utf-8

import socket
import re


class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.request_url = None
        self.client_date = None
        self.server_proxy()

    def server_proxy(self):
        server_sock = socket.socket()
        server_sock.bind((self.ip, self.port))
        server_sock.listen(5)
        print "[*] listening on %s:%d" % (self.ip, self.port)

        while True:
            print 'server waiting...'
            conn, addr = server_sock.accept()

            self.client_data = conn.recv(1024)
            print self.client_data
            req_url = re.findall('http\S+', self.client_data)
            if len(req_url):
                self.request_url = req_url[0]
            response = self.client_proxy()
            conn.sendall(response)
            conn.close()

    def client_proxy(self):
        url = self.request_url
        port = 80
        client_socket = socket.socket()
        client_socket.connect((url, port))
        client_socket.send(self.client_data.encode())
        response = b''
        rec = client_socket.recv(1024)
        while rec:
            response += rec
            rec = client_socket.recv(1024)
        print(response.decode())
        return response.decode()

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9800
    proxy = Proxy(ip, port)
