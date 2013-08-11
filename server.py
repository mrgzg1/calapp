import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
import logging
import enterpriseCal
from tornado.escape import json_encode

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)
define("debug", default=0, help="setdebug option 0= false, 1 = true(default)", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/files/brain.js", BrainHandler),
            (r"/files/formAjaxPlugin.js", PluginHandler),
            (r"/files/main.css", CssHandler),
            (r"/enterprise", EnterpriseHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "files"),
            static_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "files"),
            debug=bool(options.debug),
        )
        logging.error(settings)
        tornado.web.Application.__init__(self, handlers, **settings)
class EnterpriseHandler(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        br = enterpriseCal.EnterpriseBrowser(username,password)
        classes = br.getClassTable()
        self.write(json_encode(classes))

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class BrainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("brain.js")

class PluginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("formAjaxPlugin.js")

class CssHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.css")

if __name__ == "__main__":
    logging.error(bool(options.debug))
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
