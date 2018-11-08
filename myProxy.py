# encoding=utf-8

import socket
import re
import gzip


class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_proxy()

    def server_proxy(self):
        server_sock = socket.socket()
        server_sock.bind((self.ip, self.port))
        server_sock.listen(5)
        print "[*] listening on %s:%d" % (self.ip, self.port)

        while True:
            print 'server waiting...'
            conn, addr = server_sock.accept()
            raw_data = conn.recv(1024)
            print '---------------- query info ----------------'
            print raw_data
            if raw_data:
                client_query_dict = Proxy.analysis_http_request(raw_data)
                url = client_query_dict.get('host_url')
                port = client_query_dict.get('host_port')
                query_str = '%s %s %s \r\nHost: %s\r\nConnection: close\r\n\r\n' % (client_query_dict['methods'],
                                                                                    client_query_dict['query_full_url'],
                                                                                    client_query_dict['version'],
                                                                                    client_query_dict['host']
                                                                                    )
                if client_query_dict.get('methods') != 'CONNECT':
                    response = self.client_proxy(url, port, query_str)
                    conn.sendall(response)
            conn.close()

    def client_proxy(self, url, port, client_data=None):
        data = 0
        print '[%s] url: %s:%s' % (data, url, port)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((url, port))
        if not client_data:
            response = b'HTTP/1.1 200 Connection Established'
            client_socket.close()
            return response.decode()
        else:
            client_socket.send(client_data)
            response = b''
            rec = client_socket.recv(1024)
            print '---------------- return info ----------------'
            print rec
            while rec:
                print rec
                response += rec
                rec = client_socket.recv(1024)
                data += 1
                print '[%s] url: %s:%s' % (data, url, port)
            response_dict = Proxy.analysis_http_response(rec)
            client_socket.close()
            return response

    @classmethod
    def analysis_http_request(cls, raw_data):
        _raw_data_list = '\n'.join(raw_data.split(' ')).split('\n')
        _raw_data_list = [data for data in _raw_data_list if data]
        new_data_dict = dict()
        for i, data_item in enumerate(_raw_data_list):
            if i == 0:
                new_data_dict['methods'] = data_item.replace('\r', '')
            if i == 1:
                new_data_dict['query_full_url'] = data_item.replace('\r', '')
            if i == 2:
                new_data_dict['version'] = data_item.replace('\r', '')
            if data_item == "Host:":
                new_data_dict['host'] = _raw_data_list[i + 1].replace('\r', '')
                host_list = new_data_dict['host'].split(':')
                new_data_dict['host_url'] = host_list[0].replace('\r', '')
                if len(host_list) == 1:
                    new_data_dict['host_port'] = 80
                else:
                    new_data_dict['host_port'] = host_list[1].replace('\r', '')
            if data_item == "Accept-Encoding":
                continue
            if data_item == "Proxy-Connection:":
                new_data_dict['connection'] = _raw_data_list[i+1].replace('\r', '')
            if data_item == "User-Agent:":
                new_data_dict['userAgent'] = \
                    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
        return new_data_dict

    @classmethod
    def analysis_http_response(cls, raw_data):
        _raw_data_list = raw_data.split('\n')
        _raw_data_list = [data for data in _raw_data_list if data]
        new_data_dict = dict()
        for i, data_item in enumerate(_raw_data_list):
            if i == 0:
                new_data_dict['version'] = data_item.replace('\r', '')
            if i == 1:
                new_data_dict['status'] = data_item.replace('\r', '')
            if i == 2:
                new_data_dict['status_text'] = data_item.replace('\r', '')
        return new_data_dict


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9800
    proxy = Proxy(ip, port)
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