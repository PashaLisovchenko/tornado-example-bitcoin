import tornadoredis
import urls
from tornado import gen, web, ioloop

POOL = tornadoredis.ConnectionPool(host='127.0.0.1', port=6379)
db = tornadoredis.Client(connection_pool=POOL)
db.connect()

if __name__ == "__main__":
    if gen.Task(db.exists, 'id_order'):
        pass
    else:
        db.set('id_order', 1)
    application = web.Application(urls.urls)
    application.listen(8000)
    ioloop.IOLoop.current().start()
