# MossbackScanner
这是一个基于mitmproxy的被动式Web应用漏洞扫描工具。

**请使用者遵守当地法律，勿将 MossbackScanner 用于未授权的测试，参与本项目开发的任何人员不对利用本工具执行的违法行为负任何连带法律责任。**

# 使用方式
## 配置config.json文件
```
{
    "sqli_payload": "payloads/sqli-sqlserver.txt",  //sql注入的payload文件
    "server_host": "192.168.1.25",  //匹配目标服务器，*代表匹配所有目标
    "https_server":false,   //服务器是否为https
    "proxy_forward":"127.0.0.1:8888",   //代理配置，如无代理则为空字符串
    "static": ["html", "htm", "shtml", "js", "css", "jpeg", "jpg", "png", "gif", "ico", "woff2", "txt", "woff", "axd"], //不扫描的静态文件后缀
    "scanner_host": "127.0.0.1",    //扫描器地址
    "scanner_port": 9999,   //扫描器监听的端口
    "interval": 50      //发包间隔
}
```

## 启动扫描器
双击 run-scanner.bat 启动漏洞扫描引擎

## 代理流量
可以通过Burpsuit的Upstream Proxy Servers配置把流量导入到到mitmproxy，也可以通过chrome插件比如SwitchyOmega把流量导入到mitmproxy。

http流量会通过mitm模块转发给扫描引擎，扫描引擎对http流量进行漏洞扫描，包括未授权访问，xss，sqli等漏洞扫描。
扫描过程会在终端显示扫描情况及扫描结果，另外如发现异常，异常请求包也会被保存在logs目录下。
