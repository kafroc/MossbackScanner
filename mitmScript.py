# -*- coding: utf-8 -*-
# version: 0.2
# date: 2020.09.22

import mitmproxy
import json
import socket
import time
import hashlib

UDP_PACK_LEN = 1024


class parse_request:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reqhash = []
        with open('config.json', 'r') as fp:
            conf = json.loads(fp.read())
            self.server_host = conf['server_host']
            self.scanner_srv = (conf['scanner_host'], conf['scanner_port'])

    def request(self, flow: mitmproxy.http.HTTPFlow):
        req = flow.request

        if (self.server_host is "*") or (self.server_host in req.url):
            dic = {}
            dic['method'] = req.method
            dic['uri'] = req.path
            dic['version'] = req.http_version

            # headers
            header = {}
            for key, value in req.headers.items():
                header[key] = value
                if key == 'Host':
                    dic['host'] = value
            dic['header'] = json.dumps(header)

            # post body
            dic['body'] = req.text

            output = json.dumps(dic)
            m = hashlib.md5()
            m.update(output.encode())

            pack_len = len(output)
            pack_num = pack_len // UDP_PACK_LEN
            if pack_len % UDP_PACK_LEN != 0:
                pack_num += 1

            self.client.sendto((str(pack_num).zfill(
                4) + m.hexdigest()).encode('utf-8'), self.scanner_srv)
            time.sleep(0.01)

            for i in range(pack_num - 1):
                self.client.sendto(
                    output[i * UDP_PACK_LEN:(i + 1) * UDP_PACK_LEN].encode('utf-8'), self.scanner_srv)
                time.sleep(0.01)

            self.client.sendto(
                output[(pack_num - 1) * UDP_PACK_LEN:].encode('utf-8'), self.scanner_srv)

            response, _ = self.client.recvfrom(2)
            if response.decode() != "OK":
                time.sleep(0.5)


addons = [
    parse_request()
]
