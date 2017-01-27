from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from opp.flask.html_server import app as html_app
from opp.flask.json_server import app as json_app


app = DispatcherMiddleware(html_app, {'/api': json_app})

if __name__ == '__main__':
    run_simple('localhost', 5000, app, use_evalex=True,
               use_reloader=True, use_debugger=True)
