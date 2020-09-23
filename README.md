# MossbackScanner
这是一个基于mitmproxy的Web应用漏洞扫描工具。

# 使用方式
执行 run-mitm.bat 启动mitm代理

执行 run-scanner.bat 启动漏洞扫描引擎

http流量会通过mitm模块转发给扫描引擎，扫描引擎对http流量进行漏洞扫描，包括未授权访问，xss，sqli等漏洞扫描。
