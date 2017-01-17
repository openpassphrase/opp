import sys


sys.path.insert(0, "/var/www/openpassphrase")
sys.path.insert(0, "/var/www/openpassphrase/venv/lib/python2.7/site-packages")
activate_this = '/var/www/openpassphrase/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))


from opp.api.v1 import app as application
