import json
import time
import socket
import random
import http.client
from utils import format_save
from utils import check_repeat_package
from color_print import *


class test_sqli():
    def __init__(self):
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())
        self.name = 'SQLi'
        self.log = format_save('SQLi')
        self.checkpkg = check_repeat_package(key_with_value=False)

    def test_sqli_uri(self, method, uri, version, header, body, host):
        with open(self.conf['scanner_path'] + self.conf['payload_file'], "r") as fp:
            payloads = fp.readlines()

        params = uri.split('?')
        if len(params) == 2:
            path = params[0] + '?'
            params = params[1].split('&')

            for i in range(len(params)):
                param_bak = params[i]
                for payload in payloads:
                    time.sleep(
                        0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                    params[i] = param_bak + payload.strip()
                    uri_new = '&'.join(params)
                    hc = http.client.HTTPConnection(host, timeout=3)
                    hc.request(method, path+uri_new.replace(' ',
                                                            '%20'), body, json.loads(header))
                    try:
                        hc.getresponse().read()
                    except socket.timeout as exp:
                        self.log.format_save(
                            method, path+uri_new.replace(' ', '%20'), version, header, body)
                        # break
                    except Exception as exp:
                        printDarkRed(exp)
                    params[i] = param_bak

    def test_sqli_body(self, method, uri, version, header, body, host):
        with open(self.conf['scanner_path'] + self.conf['payload_file'], "r") as fp:
            payloads = fp.readlines()

        bodys = body.split('&')
        for i in range(len(bodys)):
            body_bak = bodys[i]
            for payload in payloads:
                time.sleep(
                    0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                bodys[i] = body_bak + payload.strip()
                body_new = '&'.join(bodys)
                hc = http.client.HTTPConnection(host, timeout=3)
                hj = json.loads(header)
                hj['Content-Length'] = len(body_new)
                hc.request(method, uri, body_new, hj)
                try:
                    hc.getresponse().read()
                except socket.timeout as exp:
                    self.log.format_save(
                        method, uri, version, header, body_new)
                except Exception as exp:
                    printDarkRed(exp)
                bodys[i] = body_bak

    def run(self, method, uri, version, header, body, host):
        if self.checkpkg.is_repeat_pkg(method, uri, body) is True:
            return
        if uri.split('?')[0].split('.')[-1] in self.conf['static']:
            return
        printGreen('Doing %s testing: %s' % (self.name, uri))
        self.test_sqli_uri(method, uri, version, header, body, host)
        if method == 'POST':
            self.test_sqli_body(method, uri, version, header, body, host)
