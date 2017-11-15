import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpclient
import tornado.template
import tornado.gen
from main import db


class MainHandler(tornado.web.RequestHandler):

    async def get(self):

        last_id_order = await tornado.gen.Task(db.get, "id_order")
        orders = []
        for i in range(1, int(last_id_order)):
            orders.append(await tornado.gen.Task(db.hgetall, 'orders:%s' % str(i)))
        if await tornado.gen.Task(db.exists, 'rate'):
            price = await tornado.gen.Task(db.get, 'rate')
            mark_db = 'Radis'
        else:
            http_client = tornado.httpclient.AsyncHTTPClient()
            response = await http_client.fetch("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
            json_obj = tornado.escape.json_decode(response.body)
            price = json_obj['bpi']['USD']['rate_float']
            db.setex('rate', 10, price)
            mark_db = False

        self.render("templates/index.html", current=str(price), redis=mark_db, orders=orders)


class MyFormHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/create_order.html")

    async def post(self):
        self.set_header("Content-Type", "text/plain")
        id_order = await tornado.gen.Task(db.get, "id_order")
        db.hmset('orders:%s' % str(id_order),
                 {"id": str(id_order),
                  "type": str(self.get_body_argument("type")),
                  "price": str(self.get_body_argument("price")),
                  "quantity": str(self.get_body_argument("quantity")),
                  "status": "active",
                  })
        db.incr("id_order")
        self.redirect('/')
