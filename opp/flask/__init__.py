from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from opp.flask.frontend import app as frontend
from opp.flask.backend import app as backend


app = DispatcherMiddleware(frontend, {'/api': backend})

if __name__ == '__main__':
    run_simple('localhost', 5000, app, use_evalex=True,
               use_reloader=True, use_debugger=True)
