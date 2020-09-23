import json
import time
import http.client

class test_sqli():
    def __init__(self):
        self.filecnt = 1
        with open('config.json', 'r') as fp:
            self.conf = json.loads(fp.read())
    
    def format_save(self, method, uri, version, header, body):
        first_line = method + ' ' + uri + ' ' + version + '\n'
        hj = json.loads(header)
        for head in hj:
            first_line += head + ': ' + hj[head] + '\n'
        first_line += '\n'
        if method == 'POST':
            first_line += body

        fn = self.conf['scanner_path'] + "logs/" + time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime()) + '_SQLi.txt'
        with open(fn, 'w') as fp:
            fp.write(first_line)
        self.filecnt += 1
    
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
                    time.sleep(0.001 * self.conf["interval"])
                    params[i] = param_bak + payload.strip()
                    #print(params[i])
                    uri_new = '&'.join(params)
                    # print(uri_new)
                    hc = http.client.HTTPConnection(host, timeout=3)
                    hc.request(method, path+uri_new.replace(' ', '%20'), body, json.loads(header))
                    try:
                        hc.getresponse().read()
                    except Exception as exp:
                        print("=========== FIND VUL. =============")
                        print(uri_new.replace(' ', '%20'))
                        self.format_save(method, path+uri_new.replace(' ', '%20'), version, header, body)
                        # break 
                    params[i] = param_bak

    def test_sqli_body(self, method, uri, version, header, body, host):
        with open(self.conf['scanner_path'] + self.conf['payload_file'], "r") as fp:
            payloads = fp.readlines()

        if method != 'POST':
            return
        
        bodys = body.split('&')
        for i in range(len(bodys)):
            body_bak = bodys[i]
            if 'ContentPlaceHolder1%24code=' not in body_bak:
                continue
            for payload in payloads:
                time.sleep(0.001 * self.conf["interval"])
                bodys[i] = body_bak + payload.strip()
                body_new = '&'.join(bodys)
                # print(body_new)
                hc = http.client.HTTPConnection(host, timeout=3)

                hj = json.loads(header)
                hj['Content-Length'] = len(body_new.replace(' ', '%20'))
                hc.request(method, uri, body_new.replace(' ', '%20'), hj)
                try:
                    hc.getresponse().read()
                except Exception as exp:
                    print("=========== FIND VUL. =============")
                    print(body_new.replace(' ', '%20'))
                    self.format_save(method, uri, version, header, body_new.replace(' ', '%20'))
                    # break
                bodys[i] = body_bak
                    
    def run(self, method, uri, version, header, body, host):
        print('Doing SQL injection: ' + uri)
        self.test_sqli_uri(method, uri, version, header, body, host)
        if method == 'POST':
            self.test_sqli_body(method, uri, version, header, body, host)
