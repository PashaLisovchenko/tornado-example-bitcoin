import tornado.ioloop
import tornado.web
import tornadoredis
import urls


POOL = tornadoredis.ConnectionPool(host='127.0.0.1', port=6379)
db = tornadoredis.Client(connection_pool=POOL)
db.connect()

if __name__ == "__main__":
    application = tornado.web.Application(urls.urls)
    application.listen(8000)
    tornado.ioloop.IOLoop.current().start()
