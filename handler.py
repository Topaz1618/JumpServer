import threading
import weakref
import paramiko
import tornado
from tornado import gen
import tornado.web
import tornado.websocket
from concurrent.futures import Future
from tornado.ioloop import IOLoop
from tornado.iostream import _ERRNO_CONNRESET
from tornado.util import errno_from_exception

BUF_SIZE = 1024
worker_dic = {}

class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, loop):
        print('i initialize')
        self.loop = loop

    def get(self):
        print('i get')
        self.render('index.html')
        # self.render('test.html')

    def get_port(self):
        value = self.get_value('port')
        try:
            port = int(value)
        except ValueError:
            raise ValueError('Invalid port {}'.format(value))
        if 0 < port < 65536:
            return port

    def get_value(self, name):
        value = self.get_argument(name)
        if not value:
            raise ValueError('Empty {}'.format(name))
        return value

    def get_args(self):
        hostname = self.get_value('hostname')
        username = self.get_value('username')
        password = self.get_value('password')
        port = self.get_port()
        args = (hostname, port, username, password)
        print("args >>>",args)
        return args

    @gen.coroutine
    def post(self):
        print('i post')
        worker_id = None
        status = None
        future = Future()
        # t = threading.Thread(target=self.ssh_connect_wrapped, args=(future,))
        t = threading.Thread(target=self.ssh_connect, args=(future,))
        t.setDaemon(True)  # 守护线程
        t.start()
        print('线程ID>> ', t.ident)
        try:
            # 通过这个yield，不管上面线程处理的函数有没有完成，都可以继续处理别的请求
            # yield关键字和return类似，都是返回结果，这符合了非阻塞io，能够立刻返回结果
            # 异步是如何实现的，future 方法，通过future的 result 和请求的进程进行交流。
            worker = yield future  # set_result(worker)
            print('work_id >>> ', worker.id, type(worker))
        except Exception as e:
            status = str(e)
        else:
            worker_id = worker.id  # 获取yield返回对象的唯一值
            worker_dic[worker_id] = worker
            print('loop前')
            self.loop.call_later(3, self.recycle_worker, worker)  # 每隔3s去找recycle_worker
            print('loop后')
        self.write(dict(id=worker_id, status=status))

    def ssh_connect(self, future):
        print('i ssh_conn')
        try:
            ssh_client = paramiko.SSHClient()  # 创建实例
            # sshclient.load_system_host_keys() 加载know_host文件
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 这行代码的作用是允许连接不在know_hosts文件中的主机。
            args = self.get_args()
            # ssh_client.connect('10.0.0.129', int(22), 'KFleader', '123456')
            ssh_client.connect(*args, timeout=6)
            chan = ssh_client.invoke_shell(term='xterm')  # 启动一个交互式shell会话，trem 传入要模拟的终端类型
            chan.setblocking(0)  # 非阻塞
            src_addr = self.get_client_addr()
            worker = Worker(self.loop, ssh_client, chan, src_addr)
            print("ssh ")
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result(worker)  # 完成后调用future.set_result设置值,必须给个值，yield下面才会继续执行
            return worker

    def get_client_addr(self):
        print('i get_client')
        '''获取真实ip'''
        ip = self.request.headers.get('X-Real-Ip')
        port = self.request.headers.get('X-Real-Port')
        if ip and port:
            real_ip = (ip, port)
        else:
            real_ip = self.request.connection.stream.socket.getpeername()
        return real_ip

    def recycle_worker(self, worker):
        print('i recycle')
        if not worker.handler:
            worker_dic.pop(worker.id, None)
            worker.close()


class WsockHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, loop):
        print('w initialize')
        self.loop = loop
        self.worker_ref = None

    def get_client_addr(self):
        print('w get_client_addr')
        ip = self.request.headers.get('X-Real-Ip')
        port = self.request.headers.get('X-Real-Port')
        if ip and port:
            real_ip = (ip, port)
        else:
            real_ip = self.stream.socket.getpeername()
        return real_ip

    def open(self):
        print('w hello open')
        current_src_addr = self.get_client_addr()
        current_id = self.get_argument('id')  # RequestHandler下的get_argument 返回你获取的值 ws?id=4384194064
        current_worker = worker_dic.get(current_id)
        worker_src_addr = current_worker.src_addr[0]
        if current_worker and worker_src_addr == current_src_addr[0]:
            worker_dic.pop(current_worker.id)
            self.set_nodelay(True)  # 默认情况下，小消息会会延迟，设置这项减少延迟
            current_worker.set_handler(self)  # 把自己传过去，在worker里需要调用本模块进行写入等操作
            self.worker_ref = weakref.ref(current_worker)  # 弱引用，对象引用计数为0或只有弱引用时将回收对象
            # add_handler(fd, handler, events) 注册一个handler，从fd那里接受事件。
            # fd呢就是一个描述符，events就是要监听的事件。events有这样几种类型，IOLoop.READ, IOLoop.WRITE, 还有IOLoop.ERROR.
            # 当我们选定的类型事件发生的时候，那么就会执行handler(fd, events) ==> worker(fd,events)
            # 我们监听了 read 事件
            self.loop.add_handler(current_worker.fd, current_worker, IOLoop.READ)
        else:
            self.close()

    def on_message(self, message):
        print("on_message", type(message), message)
        worker = self.worker_ref()
        worker.data_to_dst.append(message)
        worker.on_write()

    def on_close(self):
        print("w on_close")
        worker = self.worker_ref() if self.worker_ref else None
        if worker:
            worker.close()


class Worker(object):
    def __init__(self, loop, ssh, chan, src_addr):
        self.loop = loop
        self.ssh = ssh
        self.chan = chan
        self.src_addr = src_addr
        self.fd = chan.fileno()
        self.id = str(id(self))  # 返回对象的一个唯一身份值
        self.data_to_dst = []
        self.handler = None
        self.mode = IOLoop.READ
        print('self.id >>>', self.id)

    def __call__(self, fd, events):
        if events & IOLoop.READ:
            print(">>>>>>>>")
            self.on_read()

    def set_handler(self, handler):
        print('what self >>>', handler)  ## handler ==> <handler.WsockHandler object at 0x10bf6ea20>
        if not self.handler:
            print('handler NG')
            self.handler = handler

    def update_handler(self, mode):
        print("mode>>>", mode, self.mode)
        if self.mode != mode:
            self.loop.update_handler(self.fd, mode)
            self.mode = mode

    def on_read(self):
        '''服务器端的数据 '''
        print("on_read")
        try:
            data = self.chan.recv(BUF_SIZE)  # 从频道接收数据。返回值是表示接收到的数据的字符串.
            print("接收到的数据>>>", data)
            if not data:
                self.close()
        except (OSError, IOError) as e:
            if errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close()
        else:
            try:
                self.handler.write_message(data)
            except tornado.websocket.WebSocketClosedError:
                self.close()

    def on_write(self):
        print("on_write")
        if not self.data_to_dst:
            print("no data_to_dst")
            return
        data = ''.join(self.data_to_dst)

        try:
            sent = self.chan.send(data)
        except (OSError, IOError) as e:
            if errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close()
            else:
                self.update_handler(IOLoop.WRITE)
        else:
            self.data_to_dst = []
            data = data[sent:]
            if data:
                self.data_to_dst.append(data)
                self.update_handler(IOLoop.WRITE)
            else:
                self.update_handler(IOLoop.READ)

    def close(self):
        print("bye 呀")
        if self.handler:
            self.loop.remove_handler(self.fd)
            self.handler.close()
        self.chan.close()
        self.ssh.close()
