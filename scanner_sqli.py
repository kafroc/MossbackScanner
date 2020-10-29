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
        self.blind_timeout = 10
        with open(self.conf['payload_file'], "r") as fp:
            self.payloads = fp.read().replace('PH_TIMEOUT', str(self.blind_timeout)).split('\n')

    def test_sqli_uri(self, method, uri, version, header, body, host):
        params = uri.split('?')
        if len(params) == 2:
            path = params[0] + '?'
            params = params[1].split('&')

            for i in range(len(params)):
                printDarkYellow("*", end='', flush=True)
                param_bak = params[i]
                for payload in self.payloads:
                    time.sleep(0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                    params[i] = param_bak + payload.strip()
                    uri_new = '&'.join(params)

                    try:
                        if self.conf['https_server'] is True:
                            hc = http.client.HTTPSConnection(host, timeout=self.blind_timeout)
                        else:
                            hc = http.client.HTTPConnection(host, timeout=self.blind_timeout)
                        hc.request(method, path+uri_new.replace(' ', '%20'), body, json.loads(header))
                    except Exception as exp:
                        printDarkRed(exp)

                    try:
                        hc.getresponse().read()
                    except socket.timeout as exp:
                        self.log.format_save(method, path+uri_new.replace(' ', '%20'), version, header, body)
                    except Exception as exp:
                        printDarkRed(exp)
                    params[i] = param_bak
            printDarkYellow('')

    def test_kv_body(self, method, uri, version, header, body, host):
        bodys = body.split('&')
        for i in range(len(bodys)):
            printDarkYellow("*", end='', flush=True)
            body_bak = bodys[i]
            for payload in self.payloads:
                time.sleep(0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                bodys[i] = body_bak + payload.strip()
                body_new = '&'.join(bodys)
                
                try:
                    if self.conf['https_server'] is True:
                        hc = http.client.HTTPSConnection(host, timeout=self.blind_timeout)
                    else:
                        hc = http.client.HTTPConnection(host, timeout=self.blind_timeout)
                    hj = json.loads(header)
                    hj['Content-Length'] = len(body_new)
                    hc.request(method, uri, body_new, hj)
                except Exception as exp:
                    printDarkRed(exp)

                try:
                    hc.getresponse().read()
                except socket.timeout as exp:
                    self.log.format_save(method, uri, version, header, body_new)
                except Exception as exp:
                    printDarkRed(exp)
                bodys[i] = body_bak
        printDarkYellow('')

    def test_json_body(self, method, uri, version, header, body, host):
        bodyj = json.loads(body)
        for key in bodyj:
            printDarkYellow("*", end='', flush=True)
            body_bak = bodyj[key]
            if not isinstance(bodyj[key], str):
                continue
            for payload in self.payloads:
                time.sleep(0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                bodyj[key] = body_bak + payload.strip()
                body_new = json.dumps(bodyj)
                
                try:
                    if self.conf['https_server'] is True:
                        hc = http.client.HTTPSConnection(host, timeout=self.blind_timeout)
                    else:
                        hc = http.client.HTTPConnection(host, timeout=self.blind_timeout)
                    hj = json.loads(header)
                    hj['Content-Length'] = len(body_new)
                    hc.request(method, uri, body_new, hj)
                except Exception as exp:
                    printDarkRed(exp)

                try:
                    hc.getresponse().read()
                except socket.timeout as exp:
                    self.log.format_save(method, uri, version, header, body_new)
                except Exception as exp:
                    printDarkRed(exp)
                bodyj[key] = body_bak
        printDarkYellow('')

    def test_sqli_body(self, method, uri, version, header, body, host):
        try:
            _ = json.loads(body)
            self.test_json_body(method, uri, version, header, body, host)
        except:
            self.test_kv_body(method, uri, version, header, body, host)
            
    def run(self, method, uri, version, header, body, host):
        if self.checkpkg.is_repeat_pkg(method, uri, body) is True:
            return
        if uri.split('?')[0].split('.')[-1] in self.conf['static']:
            return
        printGreen('Doing %s testing: %s %s/%s' % (self.name, method, host, uri))
        self.test_sqli_uri(method, uri, version, header, body, host)
        if method == 'POST':
            self.test_sqli_body(method, uri, version, header, body, host)
