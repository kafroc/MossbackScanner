import json
import time
import http.client

class test_unauth_access():
    def __init__(self):
        self.filecnt = 1
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())
    
    def format_save(self, method, uri, version, header, body):
        print("**************************************************")
        print("Find unauth access")
        
        first_line = method + ' ' + uri + ' ' + version + '\n'
        hj = json.loads(header)
        for head in hj:
            first_line += head + ': ' + hj[head] + '\n'
        first_line += '\n'
        if method == 'POST':
            first_line += body

        fn = self.conf['scanner_path'] + "logs/" + time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime()) + '_unauthAccess.txt'
        with open(fn, 'w') as fp:
            fp.write(first_line)
        self.filecnt += 1
    
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
        if uri.split('?')[0].split('.')[-1] in ['asp']:
            l1 = self.test_req_with_cookie(method, uri, version, header, body, host)
            l2 = self.test_req_without_cookie(method, uri, version, header, body, host)
            if int(l1) == int(l2):
                self.format_save(method, uri, version, header, body)
            else:
                print(int(l1) - int(l2))