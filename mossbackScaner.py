# -*- coding: utf-8 -*-
# version: 0.5
# date: 2020.09.22

import json
import socket
import time
import threading
import socket
from subprocess import PIPE

from color_print import *
from utils import format_save

global glo_conf
global glo_pkg_list
global glo_lock
global glo_scanner

glo_pkg_list = []
glo_lock = threading.Lock()
glo_scanner = []

with open('config.json', 'r') as fp:
    glo_conf = json.loads(fp.read())

for plugin in glo_conf['plugins']:
    exec("from " + plugin + " import " + plugin)
    glo_scanner.append(eval(plugin + "()"))

def do_scan_thread():
    global glo_pkg_list
    global glo_lock
    global glo_scanner

    req2file = format_save('')
    while True:
        glo_lock.acquire()
        if len(glo_pkg_list) > 0:
            pkg = json.loads(glo_pkg_list.pop(0))
            glo_lock.release()

            
            if glo_conf['server_host'] != '*':
                req2file.save_request(pkg['method'], pkg['uri'], pkg['version'], pkg['header'], pkg['body'])
            
            # do all test here
            for fun in glo_scanner:
                fun.run(pkg['method'], pkg['uri'], pkg['version'], pkg['header'], pkg['body'])
            # test finished
        else:
            glo_lock.release()
            time.sleep(1)


def main():
    global glo_pkg_list
    global glo_lock
    global glo_conf

    t = threading.Thread(target=do_scan_thread, args=())
    t.start()

    MAXBUFSIZ = 1048576
    ADDRESS = ('', glo_conf['scanner_port'])
    tcpServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServerSocket.bind(ADDRESS)
    tcpServerSocket.listen()
    mitmCli = None

    while True:
        while mitmCli is None:
            try:
                mitmCli, _ = tcpServerSocket.accept()
            except:
                time.sleep(0.1)

        
        try:
            pack_data = mitmCli.recv(MAXBUFSIZ)
        except:
            mitmCli = None

        glo_lock.acquire()
        glo_pkg_list.append(pack_data)
        glo_lock.release()


if __name__ == "__main__":
    main()
