# -*- coding: utf-8 -*-
# version: 0.2
# date: 2020.09.22

import mitmproxy
import json
import socket
import time
import threading

MAXBUFSIZ = 1048576


class parse_request:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with open('config.json', 'r') as fp:
            conf = json.loads(fp.read())
            self.server_host = conf['server_host']
            self.scanner_srv = (conf['scanner_host'], conf['scanner_port'])
        self.connect = False
        self.req_buff = []
        self.lock = threading.Lock()
        self.thr = threading.Thread(target=self.t_sendtoScanner, args=())
        self.thr.start()

    def t_sendtoScanner(self):
        while True:
            if len(self.req_buff) == 0:
                time.sleep(0.5)
                continue
            
            self.lock.acquire()
            message = self.req_buff.pop(0)
            self.lock.release()
            
            if len(message) >= MAXBUFSIZ:
                print("[WARNING] Package is too large.")
                continue

            while self.connect is False:
                try:
                    self.client.connect(self.scanner_srv)
                    self.connect = True
                except Exception as exp:
                    print(exp, flush=True)
                    time.sleep(1)

            try:
                self.client.sendall(message.encode())
            except Exception as exp:
                print(exp, flush=True)
                self.connect = False
            time.sleep(0.1)

    def request(self, flow: mitmproxy.http.HTTPFlow):
        req = flow.request

        if (self.server_host is "*") or (self.server_host in req.url):
            dic = {}
            dic['method'] = req.method
            dic['uri'] = req.path
            dic['version'] = req.http_version

            # headers
            head = {}
            for key,value in req.headers.items():
                head[key] = value
            dic['header'] = json.dumps(head)

            # post body
            dic['body'] = req.text

            self.lock.acquire()
            self.req_buff.append(json.dumps(dic))
            self.lock.release()


addons = [
    parse_request()
]
