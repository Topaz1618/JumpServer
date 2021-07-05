<img src='static/images/meowfile.png' width='400' title='MeowFile, A file management system'>


一个 Python 编写的 web 应用，基于 Tornado 和 paramiko 开发，实现通过浏览器 ssh 连接到远程服务器。作者: [Topaz](https://topaz1618.github.io/about)

[English README](https://github.com/Topaz1618/FileManageSystem/blob/master/README.md)

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

### 环境
- Python 3.6.5

- Tornado 5.0.1

- CentOS 7.4

### 安装与运行步骤


1.下载JumperServer

```
 # 从github下载最新版 JumperServer 源码

 git clone https://github.com/Topaz1618/JumpServer.git
 cd JumpServer/
```

2.安装依赖项
```
 pip3 install -r requirements.txt
```
3.运行
```
 python main.py &
```

### 配置说明

在 main.py 中 把如下行设置成自己的 ip 和端口
```
 app.listen('8048', '127.0.0.1')
```


### 截图

1. 登录页面
![avatar](static/img/login.png)

2. terminal
![avatar](static/img/terminal.png)

3. 执行命令效果1
![avatar](static/img/terminal1.png)

4. 执行命令效果2
![avatar](static/img/terminal2.png)


### 注意事项
- 目前只支持 Python3
- Mac 和 Linux 下可用，Windows 环境未测试

## License
Licensed under the MIT license
