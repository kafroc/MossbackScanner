import json
import time
import socket
import random
import http.client
import ssl
from utils import format_save
from utils import check_repeat_package
from color_print import *


class scanner_cmdi():
    def __init__(self):
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())
        self.name = 'CMDi'
        self.log = format_save(self.name)
        self.checkpkg = check_repeat_package(key_with_value=False)
        self.blind_timeout = 10
        self.http_client = None
        with open(self.conf['cmdi_payload'], "r") as fp:
            self.payloads = fp.read().replace('PH_TIMEOUT', str(self.blind_timeout)).split('\n')

    def send_recv(self, method, uri, version, header, body, host):
        if self.http_client == None:
            srv = host.split(':')
            srvhost = srv[0]
            if len(srv) != 2:
                if self.conf['https_server'] is True:
                    srvport = 443
                else:
                    srvport = 80
            else:
                srvport = srv[1]

            try:
                if self.conf['proxy_forward'] != '':
                    pxy = self.conf['proxy_forward'].split(':')
                    pxyhost = pxy[0]
                    pxyport = pxy[1]

                    if self.conf['https_server'] is True:
                        self.http_client = http.client.HTTPSConnection(
                            pxyhost, pxyport, timeout=self.blind_timeout, context=ssl._create_unverified_context())
                    else:
                        self.http_client = http.client.HTTPConnection(
                            pxyhost, pxyport, timeout=self.blind_timeout)

                    self.http_client.set_tunnel(srvhost, srvport)
                else:
                    if self.conf['https_server'] is True:
                        self.http_client = http.client.HTTPSConnection(
                            srvhost, srvport, timeout=self.blind_timeout, context=ssl._create_unverified_context())
                    else:
                        self.http_client = http.client.HTTPConnection(
                            srvhost, srvport, timeout=self.blind_timeout)
            except Exception as exp:
                printDarkRed("[ERROR] [CMDi] http.client.connection")
                printDarkRed(exp)
                return False

        headjson = json.loads(header)
        headjson['Content-Length'] = len(body)

        try:
            self.http_client.request(
                method, uri.replace(' ', '%20'), body, headjson)
        except Exception as exp:
            printDarkRed("[ERROR] [CMDi] http.client.request")
            printDarkRed(exp)
            self.http_client = None
            return False

        try:
            self.http_client.getresponse().read()
        except socket.timeout as exp:
            self.log.format_save(method, uri.replace(
                ' ', '%20'), version, header, body)
            self.http_client = None
            return True
        except Exception as exp:
            printDarkRed("[ERROR] [CMDi] http.client.response")
            printDarkRed(exp)
            self.http_client = None
            return False

    def test_cmdi_uri(self, method, uri, version, header, body, host):
        params = uri.split('?')
        if len(params) == 2:
            path = params[0] + '?'
            params = params[1].split('&')

            for i in range(len(params)):
                printDarkYellow("*", end='', flush=True)
                param_bak = params[i]
                for payload in self.payloads:
                    time.sleep(
                        0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                    params[i] = param_bak + payload.strip()
                    uri_new = '&'.join(params)
                    
                    if self.send_recv(method, path + uri_new, version, header, body, host) is True:
                        break

                    params[i] = param_bak
            printDarkYellow('')

    def test_kv_body(self, method, uri, version, header, body, host):
        bodys = body.split('&')
        for i in range(len(bodys)):
            printDarkYellow("*", end='', flush=True)
            body_bak = bodys[i]
            for payload in self.payloads:
                time.sleep(
                    0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                bodys[i] = body_bak + payload.strip()
                body_new = '&'.join(bodys)

                if self.send_recv(method, uri, version, header, body_new, host) is True:
                    break

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
                time.sleep(
                    0.001 * self.conf["interval"] + 0.001 * random.randint(1, 9))
                bodyj[key] = body_bak + payload.strip()
                body_new = json.dumps(bodyj)

                if self.send_recv(method, uri, version, header, body, host) is True:
                    break

                bodyj[key] = body_bak
        printDarkYellow('')

    def test_cmdi_body(self, method, uri, version, header, body, host):
        try:
            _ = json.loads(body)
            self.test_json_body(method, uri, version, header, body, host)
        except:
            self.test_kv_body(method, uri, version, header, body, host)

    def run(self, method, uri, version, header, body):
        if self.checkpkg.is_repeat_pkg(method, uri, body) is True:
            return
        if uri.split('?')[0].split('.')[-1] in self.conf['static']:
            return
        host = json.loads(header)['Host']
        printGreen('Doing %s testing: %s %s/%s' %
                   (self.name, method, host, uri))
        self.test_cmdi_uri(method, uri, version, header, body, host)
        if method == 'POST':
            self.test_cmdi_body(method, uri, version, header, body, host)
