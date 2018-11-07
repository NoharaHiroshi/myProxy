# encoding=utf-8

import socket
import re


class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connect_url = None
        self.client_date = None
        self.client_query = None
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
            if self.client_data:
                print 'client_query: %s' % self.client_query
                self.connect_url, self.client_query = Proxy.convert_http_request(self.client_data)
                response = self.client_proxy()
                conn.sendall(response)
            conn.close()

    def client_proxy(self):
        print 'connect_url: %s' % self.connect_url
        url = self.connect_url
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

    @classmethod
    def convert_http_request(cls, raw_data):
        _raw_data_list = '\n'.join(raw_data.split(' ')).split('\n')
        _raw_data_list = [data for data in _raw_data_list if data]
        new_data_dict = dict()
        for i, data_item in enumerate(_raw_data_list):
            if i == 0:
                new_data_dict['methods'] = data_item
            if i == 1:
                new_data_dict['query_url'] = data_item
            if i == 2:
                new_data_dict['version'] = data_item
            if data_item == "Host:":
                new_data_dict['host_k'] = data_item
                new_data_dict['host_v'] = _raw_data_list[i+1]
                new_data_dict['host'] = '%s %s' % (data_item, _raw_data_list[i+1])
            if data_item == "Proxy-Connection:":
                new_data_dict['connection'] = '%s %s' % ('Connection:', _raw_data_list[i+1])
            if data_item == "User-Agent:":
                new_data_dict['userAgent'] = \
                    'User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
        query_str = '%s / %s\r\n%s\r\n%s\r\n\r\n' % (new_data_dict['methods'],
                                                     new_data_dict['version'],
                                                     new_data_dict['host'],
                                                     new_data_dict['connection']
                                                     )
        print query_str
        return new_data_dict['host_v'], query_str


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9800
    proxy = Proxy(ip, port)
    Proxy.convert_http_request()
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # url = "element-cn.eleme.io"
    # port = 80
    # client_socket.connect((url, port))
    # client_socket.send('GET / HTTP/1.1\r\nHost: element-cn.eleme.io\r\nConnection: close\r\n\r\n')
    # buffer = []
    # while True:
    #     # 每次最多接收1k字节:
    #     d = client_socket.recv(1024)
    #     if d:
    #         buffer.append(d)
    #     else:
    #         break
    # data = ''.join(buffer)
    # print data