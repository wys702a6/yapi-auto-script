# -*- coding:utf-8 -*-

from server import app


if __name__ == '__main__':
    try:
        from gevent.wsgi import WSGIServer
    except ImportError:
        app.run("0.0.0.0", port=4444, debug=False, threaded=True)
    else:
        http_server = WSGIServer("{}:{}".format("0.0.0.0", 4444), app)
        http_server.serve_forever()

