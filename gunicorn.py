import os.path
import multiprocessing

BASEDIR = os.path.abspath(os.path.dirname(__file__))
# bind = f"unix://{BASEDIR}/logs/app.sock"
# OR
# bind = "0.0.0.0:8000"
bind = f"unix://{BASEDIR}/wiki/fwiki.sock"
backlog = 2048

# user = "www-data"
# group = "www-data"

loglevel = "warning"
errorlog = f"{BASEDIR}/logs/gunicorn.log"

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = workers * 3
timeout = 30
keepalive = 2
