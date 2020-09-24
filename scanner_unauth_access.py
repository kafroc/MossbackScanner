import json
import time
import http.client
from utils import format_save


class test_unauth_access():
    def __init__(self):
        self.filecnt = 1
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())
        self.log = format_save('unauth')

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
        print('Doing unauth access: ' + uri)
        if uri.split('?')[0].split('.')[-1] not in ['html', 'htm', 'shtml', 'js', 'css', 'jpeg', 'jpg', 'png', 'gif', 'ico', 'woff2', 'txt']:
            l1 = self.test_req_with_cookie(
                method, uri, version, header, body, host)
            l2 = self.test_req_without_cookie(
                method, uri, version, header, body, host)

            if int(l1) == int(l2):
                self.log.format_save(method, uri, version, header, body)
            else:
                print(int(l1) - int(l2))
