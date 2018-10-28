#!/usr/bin/env python

import web

urls = (
    '/', 'index',
    '/h', 'test',
)


class index:
    def GET(self):
        print("hello world")


class test:
    def GET(self):
        print("Love!")


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
