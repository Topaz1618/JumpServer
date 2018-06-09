import tornado.web
import tornado.ioloop
import os
import uuid
from handler import IndexHandler,WsockHandler

def main():
    base_dir = os.path.dirname(__file__)
    settings = dict(
        template_path=os.path.join(base_dir, 'templates'),
        static_path=os.path.join(base_dir, 'static'),
        cookie_secret=uuid.uuid4().hex,
        xsrf_cookies=True)

    loop = tornado.ioloop.IOLoop.current()
    handlers = [
        (r'/', IndexHandler, dict(loop=loop)),  #字典方式传参，会传到对应类的 initialize()方法中
        (r'/ws', WsockHandler, dict(loop=loop)),
    ]
    app = tornado.web.Application(handlers, **settings)
    app.listen('8048', '127.0.0.1')
    loop.start()

if __name__ == '__main__':
    main()
