from controller import *


urls = [
    (r"/", MainHandler),
    (r"/order/", MyFormHandler),
    (r"/order/(?P<pk>[0-9]+)/", GetOrderById),
]

