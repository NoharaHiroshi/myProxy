# encoding=utf-8

import socket
import re
import gzip
import time
import traceback
import threading


class Proxy:
    def __init__(self, ip, port, thread=5):
        self.ip = ip
        self.port = port
        self.request_dict = dict()
        self.server_sock = socket.socket()
        self.server_sock.bind((self.ip, self.port))
        self.server_sock.listen(5)
        for i in range(thread):
            threading.Thread(target=self.server_proxy, args=(i,)).start()

    def server_proxy(self, num=0):
        print "[%s] listening on %s:%d" % (num, self.ip, self.port)
        while True:
            try:
                print '[%s] *************** server waiting... ***************' % num
                conn, addr = self.server_sock.accept()
                raw_data = conn.recv(1024)
                if raw_data:
                    handle_data = self.handle_raw_request(raw_data)
                    if handle_data:
                        response = self.client_proxy(self.request_dict['host_url'],
                                                     int(self.request_dict['host_port']),
                                                     handle_data, num)
                        conn.sendall(response)
                print '[%s] *************** server end ***************' % num
            except Exception as e:
                print 'server error...'
                print traceback.format_exc(e)
            finally:
                conn.close()

    def handle_raw_request(self, raw_data):
        raw_data_list = '\n'.join(raw_data.split(' ')).split('\n')
        _raw_data_list = [data for data in raw_data_list if data]
        full_cookie = ''
        new_data_dict = dict()
        for i, data_item in enumerate(_raw_data_list):
            # 获取基本参数
            if i == 0:
                new_data_dict['methods'] = data_item.replace('\r', '')
                if new_data_dict['methods'].upper() == 'CONNECT':
                    return
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
            self.request_dict = new_data_dict
        # 返回新的请求头
        raw_data_list = raw_data.split(' ')
        # 请求url
        raw_data_list[1] = re.sub('.+?%s' % new_data_dict['host'], '', new_data_dict['query_full_url'])
        new_data_str = ' '.join(raw_data_list)
        new_data_str = new_data_str.replace('Proxy-Connection', 'Connection')
        return new_data_str

    def client_proxy(self, url, port, client_data, num):
        print '[%s]' % num, client_data
        if not client_data:
            return
        response = ''
        data = 0
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(20)
        try:
            client_socket.connect((url, port))
            client_socket.send(client_data)
            rec = client_socket.recv(1024)
            while rec:
                response += rec
                rec = client_socket.recv(1024)
                print '%s url: %s:%s' % (data, url, port)
                data += 1
            print 'return info end'
        except Exception as e:
            err = traceback.format_exc(e)
            print err
            response = ''
        finally:
            client_socket.close()
            return response


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9800
    proxy = Proxy(ip, port)
    # test_raw_data = "GET http://www.runoob.com/http/http-messages.html HTTP/1.1\r\n" \
    #     "Host: www.runoob.com\r\n" \
    #     "Proxy-Connection: keep-alive\r\n"\
    #     "Cache-Control: max-age=0\r\n"\
    #     "Upgrade-Insecure-Requests: 1\r\n"\
    #     "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36\r\n"\
    #     "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n"\
    #     "Accept-Encoding: gzip, deflate\r\n"\
    #     "Accept-Language: zh-CN,zh;q=0.9\r\n"\
    #     "Cookie: Hm_lvt_8e2a116daf0104a78d601f40a45c75b4=1531204556,1531292087,1531293153,1531810509; _ga=GA1.2.101945719.1532075214; Hm_lvt_3eec0b7da6548cf07db3bc477ea905ee=1539859078,1540203684,1540437180,1541641433; _gid=GA1.2.1847875878.1541641434; Hm_lpvt_3eec0b7da6548cf07db3bc477ea905ee=1541641439\r\n"
    # raw_data_dict = proxy.handle_raw_request(test_raw_data)
    # return_data = proxy.return_new_request(raw_data_dict)
    # print return_data
