# encoding=utf-8

import socket
import re
import gzip
import time
import traceback
import ssl
import threading


class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.request_dict = dict()
        self.run_host_list = list()
        self.server = None

    def main(self):
        self.server_sock = socket.socket()
        self.server_sock.bind((self.ip, self.port))
        self.server_sock.listen(5)
        print "[*] listening on %s:%d" % (self.ip, self.port)
        self.server_proxy()

    def server_proxy(self):
        conn = None
        try:
            while True:
                print '*************** server waiting... ***************'
                # 接受请求
                conn, addr = self.server_sock.accept()
                self.server = conn
                raw_data, address = conn.recvfrom(1024)
                if raw_data:
                    handle_data_dict, handle_data_str = self.handle_raw_request(raw_data)
                    if handle_data_dict and handle_data_str:
                        print handle_data_str
                        print handle_data_dict
                        response = self.client_proxy(handle_data_dict, handle_data_str)
                        print response
                        conn.send(response)
                print '*************** server end ***************'
        except Exception as e:
            print 'server error...'
            print traceback.format_exc(e)
        finally:
            if conn:
                conn.close()

    def client_proxy(self, handle_data_dict, handle_data_str):
        port = int(handle_data_dict.get('host_port')) if handle_data_dict.get('host_port') else 80
        host = handle_data_dict.get('host_url')
        if port != 80:
            client_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print '*************** client start ***************'
            client_socket.connect((host, port))
            client_socket.send(handle_data_str)
            client_socket.settimeout(10)
            rec = client_socket.recv(1024)
            response = ''
            data_part_num = 0
            try:
                while rec:
                    response += rec
                    rec = client_socket.recv(1024)
                    data_part_num += 1
                    print 'client start part %s' % data_part_num
            except Exception as e:
                print traceback.format_exc(e)
            if response:
                return response
            else:
                return 'no info'
        except Exception as e:
            print traceback.format_exc(e)
            return 'no info'
        finally:
            if client_socket:
                client_socket.close()

    def handle_raw_request(self, raw_data):
        raw_data_list = '\n'.join(raw_data.split(' ')).split('\n')
        _raw_data_list = [data for data in raw_data_list if data]
        full_cookie = ''
        new_data_dict = dict()
        for i, data_item in enumerate(_raw_data_list):
            # 获取基本参数
            if i == 0:
                new_data_dict['methods'] = data_item.replace('\r', '')
                # if new_data_dict['methods'].upper() == 'CONNECT':
                #     return dict(), ''
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
            if data_item == "Proxy-Connection:":
                new_data_dict['connection'] = _raw_data_list[i+1].replace('\r', '')
            if data_item == "User-Agent:":
                new_data_dict['userAgent'] = \
                    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            if data_item == "Accept:":
                new_data_dict['accept'] = _raw_data_list[i+1].replace('\r', '')
            if data_item == "Cookie:":
                j = 1
                while len(_raw_data_list[i+j].split(';')) == 2:
                    full_cookie += _raw_data_list[i+j]
                    j += 1
                full_cookie += _raw_data_list[i+j]
                new_data_dict['cookie'] = full_cookie
        # 返回新的请求头
        raw_data_list = raw_data.split(' ')
        # 请求url
        raw_data_list[1] = re.sub('.+?%s' % new_data_dict['host'], '', new_data_dict['query_full_url'])
        new_data_str = ' '.join(raw_data_list)
        new_data_str = new_data_str.replace('Proxy-Connection', 'Connection')
        if new_data_dict.get('host_port') == 80:
            new_data_str = new_data_str.replace('keep-alive', 'close')
        new_data_str = new_data_str.replace('gzip, deflate', '*')
        return new_data_dict, new_data_str

    def handle_response(self, response):
        _response_list = response.split('\r\n')
        tmp_index = 0
        for i,  res in enumerate(_response_list):
            if res == '':
                tmp_index = i
                print tmp_index
                break
        if tmp_index:
            del _response_list[tmp_index+1]
            response = '\r\n'.join(_response_list)
        return response

    def handle_https_request(self, request):
        pass


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9800
    proxy = Proxy(ip, port)
    proxy.main()
    # request = 'HTTP/1.1 302 Found\r\n' \
    #           'Location: http://www.cnblogs.com/sufei/archive/2011/10/22/2221289.html\r\n' \
    #           'Connection: close\r\n' \
    #           'Content-Length: 0'
    # server_sock = socket.socket()
    # server_sock.bind(('127.0.0.1', 9800))
    # server_sock.listen(5)
    # try:
    #     while True:
    #         conn, addr = server_sock.accept()
    #         raw_data = conn.recv(1024)
    #         conn.send(request)
    # except Exception as e:
    #     print e
    # finally:
    #     server_sock.close()