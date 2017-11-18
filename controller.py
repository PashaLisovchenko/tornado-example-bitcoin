import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpclient
import tornado.template
import tornado.gen
from main import db


def update_table(s, p):
    if int(s["price"]) == int(p["price"]):
        sale_q = int(s["quantity"])
        purchase_q = int(p['quantity'])
        result = sale_q if sale_q < purchase_q else purchase_q
        if purchase_q == result:
            sale_q -= purchase_q
            tornado.gen.Task(db.hset, 'orders:%s' % str(s["id"]), 'quantity', str(sale_q))
            tornado.gen.Task(db.hset, 'orders:%s' % str(p["id"]), 'status', 'close')
        else:
            purchase_q -= sale_q
            tornado.gen.Task(db.hset, 'orders:%s' % str(p["id"]), 'quantity', str(purchase_q))
            tornado.gen.Task(db.hset, 'orders:%s' % str(s["id"]), 'status', 'close')


class MainHandler(tornado.web.RequestHandler):

    def data_received(self, chunk):
        pass

    async def get(self):

        last_id_order = await tornado.gen.Task(db.get, "id_order")
        orders = []
        for i in range(1, int(last_id_order)):
            order = await tornado.gen.Task(db.hgetall, 'orders:%s' % str(i))
            if order["status"] == 'active':
                orders.append(order)
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

    async def post(self, *args, **kwargs):
        last_id_order = await tornado.gen.Task(db.get, "id_order")
        orders = []
        for i in range(1, int(last_id_order)):
            orders.append(await tornado.gen.Task(db.hgetall, 'orders:%s' % str(i)))

        sale = [order for order in orders if order["type"] == "sale" and order["status"] == 'active']
        purchase = [order for order in orders if order["type"] == "purchase" and order["status"] == 'active']

        if len(sale) > len(purchase):
            for s in sale:
                if len(purchase) > 0:
                    for p in purchase:
                        update_table(s, p)
        else:
            for p in purchase:
                if len(sale) > 0:
                    for s in sale:
                        update_table(s, p)
        self.redirect('/')

class MyFormHandler(tornado.web.RequestHandler):

    def data_received(self, chunk):
        pass

    def get(self):
        self.render("templates/create_order.html")

    async def post(self):
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


class GetOrderById(tornado.web.RequestHandler):

    def data_received(self, chunk):
        pass

    async def get(self, pk):
        order = await tornado.gen.Task(db.hgetall, 'orders:%s' % str(pk))
        if len(order.keys()) > 0:
            self.render("templates/orders.html", order=order)
        else:
            self.set_header("Content-Type", "text/plain")
            self.write("It's order don't find")

