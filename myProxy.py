# encoding=utf-8

import socket
import re
import gzip


class _Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        # self.server_proxy()

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
            if data_item == "Accept-Encoding":
                continue
        return new_data_dict


class Proxy:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        # self.server_proxy()

    def server_proxy(self):
        server_sock = socket.socket()
        server_sock.bind((self.ip, self.port))
        server_sock.listen(5)
        print "[*] listening on %s:%d" % (self.ip, self.port)

        while True:
            try:
                print 'server waiting...'
                conn, addr = server_sock.accept()
                raw_data = conn.recv(1024)
                if raw_data:
                    print raw_data
            except Exception as e:
                print 'server error...'

    def handle_raw_request(self, raw_data):
        raw_data_list = '\n'.join(raw_data.split(' ')).split('\n')
        _raw_data_list = [data for data in raw_data_list if data]
        new_data_dict = dict()
        for i, data_item in enumerate(_raw_data_list):
            # 基本参数
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
            if data_item == "Proxy-Connection:":
                new_data_dict['connection'] = _raw_data_list[i+1].replace('\r', '')
            if data_item == "User-Agent:":
                new_data_dict['userAgent'] = \
                    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            if data_item == "Accept:":
                new_data_dict['accept'] = _raw_data_list[i+1].replace('\r', '')
            if data_item == "Cookie:":
                new_data_dict['cookie'] = _raw_data_list[i+1].replace('\r', '')
        return new_data_dict

    def return_new_request(self, new_data_dict):
        # 处理url
        request_list = list()
        methods = new_data_dict['methods']
        if methods == 'CONNECT':
            return
        query_url = re.sub('.+?%s' % new_data_dict['host'], '', new_data_dict['query_full_url'])
        request_list.append(query_url)
        request_list.append('%s %s %s' % (methods, query_url, new_data_dict['version']))
        request_list.append('Host: %s' % new_data_dict['host'])
        request_list.append('User-Agent: %s' % new_data_dict['userAgent'])
        request_list.append('Connection: %s' % new_data_dict['connection'])
        for k, v in new_data_dict.items():
            if k in ['methods', 'host', 'version', 'userAgent', 'connection', 'query_full_url']:
                continue
            elif k == 'cookie':
                request_list.append('Cookie: %s' % new_data_dict['cookie'])
            elif k == 'accept':
                request_list.append('Accept: %s' % new_data_dict['accept'])
        return '\r\n'.join(request_list)


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9800
    proxy = Proxy(ip, port)
    test_raw_data = "GET http://www.runoob.com/http/http-messages.html HTTP/1.1\r\n" \
        "Host: www.runoob.com\r\n" \
        "Proxy-Connection: keep-alive\r\n"\
        "Cache-Control: max-age=0\r\n"\
        "Upgrade-Insecure-Requests: 1\r\n"\
        "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36\r\n"\
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n"\
        "Accept-Encoding: gzip, deflate\r\n"\
        "Accept-Language: zh-CN,zh;q=0.9\r\n"\
        "Cookie: Hm_lvt_8e2a116daf0104a78d601f40a45c75b4=1531204556,1531292087,1531293153,1531810509; _ga=GA1.2.101945719.1532075214; Hm_lvt_3eec0b7da6548cf07db3bc477ea905ee=1539859078,1540203684,1540437180,1541641433; _gid=GA1.2.1847875878.1541641434; Hm_lpvt_3eec0b7da6548cf07db3bc477ea905ee=1541641439\r\n"
    raw_data_dict = proxy.handle_raw_request(test_raw_data)
    return_data = proxy.return_new_request(raw_data_dict)
    print return_data
