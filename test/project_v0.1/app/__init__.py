from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
#from flask_sqlalchemy import SQLAlchemy
#from flaskext.sqlalchemy import SQLAlchemy
import os
#from flask.ext.login import LoginManager
#from flask.ext.openid import OpenID
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

import socket
# This is a terrible hack, but oh well:
if socket.gethostname() == "roberts":
    import logging
    from logging.handlers import SMTPHandler, RotatingFileHandler
    handlers = []
    mail_handler = SMTPHandler("127.0.0.1",
                               "ben-word-guess@vorpus.org",
                               ["njs@vorpus.org"], "ben-word-guess error")
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter("""
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    """))
    handlers.append(mail_handler)
    file_handler = RotatingFileHandler("/home/ben-word-guess/wsgi.log",
                                       maxBytes=100000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
    file_handler.setLevel(logging.WARNING)
    handlers.append(file_handler)

    for logger in [app.logger, logging.getLogger("sqlalchemy")]:
        for handler in handlers:
            logger.addHandler(handler)


# lm = LoginManager()
# lm.setup_app(app)
# lm.login_view = 'login'
# oid = OpenID(app, os.path.join(basedir, 'tmp'))

from app import views, models
