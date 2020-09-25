# MossbackScanner
这是一个基于mitmproxy的Web应用漏洞扫描工具。

# 使用方式
## 配置config.json文件
```
{
    "scanner_path": "配置扫描器所在的路径，比如C:/Users/DH/Desktop/xasdf/MossbackScanner-master/",
    "payload_file": "配置扫描器使用的payload文件，比如payloads/mysql_payloads.txt",
    "server_host": "配置Web服务器地址，比如192.168.1.133，或者www.example.com",
    "scanner_host": "配置扫描器监听的地址，一般可设置为127.0.0.1，如果mitmproxy和扫描器不是同一台主机，则设置为扫描器的ip地址",
    "interval": 配置发包间隔，以毫秒为单位，比如100,
    "scanner_port": 扫描器监听的端口，比如9999
}
```

## 启动扫描器
双击 run-scanner.bat 启动漏洞扫描引擎

## 代理流量
可以通过Burpsuit的Upstream Proxy Servers配置把流量导入到到mitmproxy，也可以通过chrome插件比如SwitchyOmega把流量导入到mitmproxy。

http流量会通过mitm模块转发给扫描引擎，扫描引擎对http流量进行漏洞扫描，包括未授权访问，xss，sqli等漏洞扫描。
扫描过程会在终端显示扫描情况及扫描结果，另外如发现异常，异常请求包也会被保存在logs目录下。
