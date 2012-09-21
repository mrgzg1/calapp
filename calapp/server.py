import daemon
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
import logging
import classCalendar
from tornado.escape import json_encode

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)
define("debug", default=0, help="setdebug option 0= false, 1 = true(default)", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/enterprise", EnterpriseHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates"),
            static_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "static"),
            debug=bool(options.debug),
        )
        logging.error(settings)
        tornado.web.Application.__init__(self, handlers, **settings)
class EnterpriseHandler(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        br = classCalendar.EnterpriseBrowser(username,password)
        classes = br.getClassTable()
        self.write(json_encode(classes))

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

if __name__ == "__main__":
    # if not bool(options.debug):
    #     log = open('tornado.' + str(options.port) + '.log', 'a+')
    #     ctx = daemon.DaemonContext(stdout=log, stderr=log,  working_directory='.')
    #     ctx.open()
    logging.error(bool(options.debug))
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
