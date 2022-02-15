from flask import Flask, redirect, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView, expose
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(levelname)s [%(asctime)s] %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },'archivo': {
        'class' : 'logging.handlers.RotatingFileHandler',
        'formatter': 'default',
        'filename' : 'LOG.txt',
        'maxBytes': 5000000,
        'backupCount': 10
        }
    },
    'root': {
        'handlers': ['wsgi','archivo']
    }
})

app = Flask(__name__)
app.config.update(dict(
    DEBUG = True,
))

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

class MyView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_admin:
            return redirect(url_for('login'))
        else:
            return self.render('admin/index.html')

admin = Admin(app,name='Examinator',index_view=MyView())
app.logger.info('Iniciado el sistema')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from app import views, models, errors, crearplantilla
