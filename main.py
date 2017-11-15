import tornado.ioloop
import tornado.web
import tornadoredis
import urls

db = tornadoredis.Client()
db.connect()

if __name__ == "__main__":
    application = tornado.web.Application(urls.urls)
    application.listen(8000)
    tornado.ioloop.IOLoop.current().start()
