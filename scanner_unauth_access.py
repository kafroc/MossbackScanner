import json
import time
import http.client
from utils import format_save
from utils import check_repeat_package
from color_print import *


class test_unauth_access():
    def __init__(self):
        self.filecnt = 1
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())
        self.name = 'unauth'
        self.log = format_save(self.name)
        self.httptimeout = 10
        self.checkpkg = check_repeat_package(key_with_value=True)

    def test_req_with_cookie(self, method, uri, version, header, body, host):
        if self.conf['https_server'] is True:
            hc = http.client.HTTPSConnection(host, timeout=self.httptimeout)
        else:
            hc = http.client.HTTPConnection(host, timeout=self.httptimeout)
        hc.request(method, uri, body, json.loads(header))
        l1 = hc.getresponse().getheader("Content-Length")

        if l1 is None:
            return 0

        return int(l1)

    def test_req_without_cookie(self, method, uri, version, header, body, host):
        if self.conf['https_server'] is True:
            hc = http.client.HTTPSConnection(host, timeout=self.httptimeout)
        else:
            hc = http.client.HTTPConnection(host, timeout=self.httptimeout)
        hj = json.loads(header)
        hj["Cookie"] = ''
        hc.request(method, uri, body, hj)
        l2 = hc.getresponse().getheader("Content-Length")

        if l2 is None:
            return -1

        return int(l2)

    def run(self, method, uri, version, header, body, host):
        if self.checkpkg.is_repeat_pkg(method, uri, body) is True:
            return

        if "Cookie" not in header:
            return

        if uri.split('?')[0].split('.')[-1] not in self.conf['static']:
            printGreen('Doing %s testing: %s' % (self.name, uri))

            l1 = self.test_req_with_cookie(
                method, uri, version, header, body, host)
            l2 = self.test_req_without_cookie(
                method, uri, version, header, body, host)

            try:
                if l1 == l2:
                    self.log.format_save(method, uri, version, header, body)
            except Exception as exp:
                printRed(exp)
