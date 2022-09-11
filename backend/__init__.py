# load env
from dotenv import load_dotenv
load_dotenv()

# create app
from flask import Flask
app = Flask(__name__)

# db setting
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://linpinhung:password@localhost/flask_testing_dev'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# migrate setting
# 這行 import models 可以讓 "flask db migrate" 順利偵測到 models.py 檔
from backend import models
"""
flask db init
flask db migrate
flask db upgrade
"""

# routes setting
from backend.routes.home import home
from backend.routes.signup import signup
from backend.routes.session import session
from backend.routes.basic_auth import basic_auth

app.register_blueprint(home)
app.register_blueprint(signup)
app.register_blueprint(session)
app.register_blueprint(basic_auth)


