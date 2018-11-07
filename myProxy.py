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
                need_clean_url = req_url[0]
                _req_url = re.sub('http://', '', need_clean_url)
                cleaned_url = re.sub('/', '', _req_url)
                self.request_url = cleaned_url
                response = self.client_proxy()
                conn.sendall(response)
            conn.close()

    def client_proxy(self):
        url = self.request_url
        print url
        port = 80
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((url, port))
        client_socket.send(self.client_data.encode())
        response = b''
        rec = client_socket.recv(1024)
        while rec:
            response += rec
            rec = client_socket.recv(1024)
        print(response.decode())
        client_socket.close()
        return response.decode()

if __name__ == '__main__':
    # ip = '127.0.0.1'
    # port = 9800
    # proxy = Proxy(ip, port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    url = "element-cn.eleme.io"
    port = 80
    client_socket.connect((url, port))
    client_socket.send('GET / HTTP/1.1\r\nHost: element-cn.eleme.io\r\nConnection: close\r\n\r\n')
    buffer = []
    while True:
        # 每次最多接收1k字节:
        d = client_socket.recv(1024)
        if d:
            buffer.append(d)
        else:
            break
    data = ''.join(buffer)
    print data