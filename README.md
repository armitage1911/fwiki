# fwiki

Wiki-wannabe site on Flask with `psycopg`, `gunicorn[gevent]` and `markdown-it-py` stuff with a `Bootstrap`.

To install this package make sure you have a running Postgres Pro and nginx apps on your server.

Then:

* Clone this rep
* Make a /venv folder
* Type source venv/bin/activate
* cd into /INSTALLER dir
* Type 'pip install .'

Make sure you've prepared a systemd daemon service for Gunicorn and configured a nginx server. Check /NOTES for those files.

This package are still a work in progress so atm it doesn't have a proper index page and some kind of treeview.
