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
        self.log = format_save('unauth')
        self.checkpkg = check_repeat_package(key_with_value=True)
        self.name = 'unauth access'

    def test_req_with_cookie(self, method, uri, version, header, body, host):
        hc = http.client.HTTPConnection(host, timeout=3)
        hc.request(method, uri, body, json.loads(header))
        l1 = hc.getresponse().getheader("Content-Length")
        return l1

    def test_req_without_cookie(self, method, uri, version, header, body, host):
        hc = http.client.HTTPConnection(host, timeout=3)
        hj = json.loads(header)
        hj["Cookie"] = ''
        hc.request(method, uri, body, hj)
        l2 = hc.getresponse().getheader("Content-Length")
        return l2

    def run(self, method, uri, version, header, body, host):
        if self.checkpkg.is_repeat_pkg(method, uri, body) is True:
            return

        if "Cookie" not in header:
            return

        if uri.split('?')[0].split('.')[-1] not in ['html', 'htm', 'shtml', 'js', 'css', 'jpeg', 'jpg', 'png', 'gif', 'ico', 'woff2', 'txt']:
            printGreen('Doing %s testing: %s' % (self.name, uri))

            l1 = self.test_req_with_cookie(
                method, uri, version, header, body, host)
            l2 = self.test_req_without_cookie(
                method, uri, version, header, body, host)

            if int(l1) == int(l2):
                self.log.format_save(method, uri, version, header, body)
