from os import makedirs
from os.path import join, dirname, realpath
# from os.path import abspath, dirname
from flask import Flask

# https://stackoverflow.com/questions/37901716/flask-uploads-ioerror-errno-2-no-such-file-or-directory
# Чекнуть различия realpath от abspath
# BASE_DiR = abspath(dirname(__file__))
# UPLOAD_FOLDER = "./static/uploads"
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/images/')
DSN = ("host=localhost user=USERNAME password=PASSWORD "
       "port=5432 dbname=flask_wiki")


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # 16 megabytes

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import wiki
    app.register_blueprint(wiki.bp)
    app.add_url_rule('/', endpoint='index')

    return app
