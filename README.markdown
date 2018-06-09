# JumpServer
一个基于 Tornado 开发的 webssh。

### 架构简要说明
```
┌── handler(核心代码)
├── main.py(运行 Server)
├── static(静态文件)
├── templates(模板)
├── tests(测试文件)
├── README.md(项目说明)
└── requirements.txt(python库依赖)
```

### 安装与运行步骤
以下是 Linux 下的安装步骤

1. 下载JumperServer

从github下载最新版 JumperServer 源码。
```
 git clone https://github.com/Topaz1618/JumpServer.git
 cd JumpServer/
```

2. 安装依赖项
```
 pip3 install -r requirements.txt
```
3. 运行
```
 python main.py &
```

### 配置说明

在 main.py 中 把如下行设置成自己的Ip,port
```
 app.listen('8048', '127.0.0.1')
```


### 注意事项
- 目前只支持 Python3
- Mac 和 Linux 下可用，Windows 环境未测试


### LICENSE
开源协议：MPL
请遵守MPL协议，对Minos进行二次开发与使用。

