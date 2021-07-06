<img src='static/img/donuts_logo.png' title='
DonutsTerminal, A online termainal'>
 

An online terminal web application written in Python, based on Tornado and paramiko, allow remote connection to the server via ssh in the browser. 

Author: [Topaz](https://topaz1618.github.io/about) ([Website](http://topazaws.com/)|[Blog](https://topaz1618.github.io/blog/)

[Chinese README](https://github.com/Topaz1618/DonutsTerminal/blob/master/README_CN.markdown)


## Environment
- Python 3.6.5
- Tornado 5.0.1
- CentOS 7.4

## Installation
1. Download MeowFile

```
  $git clone https://github.com/Topaz1618/DonutsTerminal.git
  $cd DonutsTerminal/
```

2. Install dependencies
```
  pip3 install -r requirements.txt
```
3. Run
```
  python main.py &
```

## Configuration

Set the following lines to your own Ip and port in main.py
```
 app.listen('8048', '127.0.0.1')
```


## Screenshots

## 【Login Page】
![avatar](static/img/login.png)

## 【Web version terminal】
![avatar](static/img/terminal.png)

## 【Execution command effect 1】
![avatar](static/img/terminal1.png)

## 【Execution command effect 2】
![avatar](static/img/terminal2.png)


## Precautions
Available under Mac and Linux, not tested in Windows environment

## License
Licensed under the MIT license
