import json
import time
import http.client
import ssl
from utils import format_save
from utils import check_repeat_package
from color_print import *


class scanner_unauth_access():
    def __init__(self):
        self.filecnt = 1
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())
        self.name = 'unauth'
        self.log = format_save(self.name)
        self.httptimeout = 10
        self.http_client = None
        self.checkpkg = check_repeat_package(key_with_value=True)

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
                            pxyhost, pxyport, timeout=self.httptimeout, context=ssl._create_unverified_context())
                    else:
                        self.http_client = http.client.HTTPConnection(
                            pxyhost, pxyport, timeout=self.httptimeout)

                    self.http_client.set_tunnel(srvhost, srvport)
                else:
                    if self.conf['https_server'] is True:
                        self.http_client = http.client.HTTPSConnection(
                            srvhost, srvport, timeout=self.httptimeout, context=ssl._create_unverified_context())
                    else:
                        self.http_client = http.client.HTTPConnection(
                            srvhost, srvport, timeout=self.httptimeout)
            except Exception as exp:
                printDarkRed("[ERROR] [UNAUTH] http.client.connection")
                printDarkRed(exp)
                return -1

        headjson = json.loads(header)
        headjson['Content-Length'] = len(body)
        try:
            self.http_client.request(
                method, uri.replace(' ', '%20'), body, headjson)
        except Exception as exp:
            printDarkRed("[ERROR] [UNAUTH] http.client.request")
            printDarkRed(exp)
            self.http_client = None
            return -1

        try:
            ret = self.http_client.getresponse().getheader("Content-Length")
            self.http_client = None
            return int(ret)
        except Exception as exp:
            printDarkRed("[ERROR] [UNAUTH] http.client.response")
            printDarkRed(exp)
            self.http_client = None
            return -1

    def run(self, method, uri, version, header, body):
        if self.checkpkg.is_repeat_pkg(method, uri, body) is True:
            return

        if "Cookie" not in header:
            return

        if uri.split('?')[0].split('.')[-1] not in self.conf['static']:
            host = json.loads(header)['Host']
            printGreen('Doing %s testing: %s %s/%s' %
                       (self.name, method, host, uri))

            l1 = self.send_recv(
                method, uri, version, header, body, host)

            header_new = json.loads(header)
            header_new["Cookie"] = ''
            header = json.dumps(header_new)
            l2 = self.send_recv(
                method, uri, version, header, body, host)

            try:
                if l1 != -1 and l2 != -1 and l1 == l2:
                    self.log.format_save(method, uri, version, header, body)
            except Exception as exp:
                printDarkRed("[ERROR] [UNAUTH] save log to file")
                printDarkRed(exp)
