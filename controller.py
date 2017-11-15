import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.httpclient
import tornado.template
import tornado.gen
from main import db


class MainHandler(tornado.web.RequestHandler):

    async def get(self):
        o = await tornado.gen.Task(db.get, 'orders')
        if await tornado.gen.Task(db.exists, 'rate'):
            r = await tornado.gen.Task(db.get, 'rate')
            self.render("templates/index.html", current=r, redis='Redis')
            # self.write("!redis! current price : {}\n".format(r) +
            #            "orders {}".format(o))
        else:
            http_client = tornado.httpclient.AsyncHTTPClient()
            response = await http_client.fetch("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
            json_obj = tornado.escape.json_decode(response.body)
            price = json_obj['bpi']['USD']['rate_float']
            db.setex('rate', 10, price)
            self.render("templates/index.html", current=str(price), redis=False)


class MyFormHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/create_order.html")

    async def post(self):
        self.set_header("Content-Type", "text/plain")
        order = "You order : Type-" + self.get_body_argument("type") + "\n" + "Price-" + self.get_body_argument("price") + "\n" + "quantity-"+ self.get_body_argument("quantity")
        db.set('orders', order)
        self.redirect('/')
