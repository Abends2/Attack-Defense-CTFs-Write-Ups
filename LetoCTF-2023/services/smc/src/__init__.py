from flask import Flask
from config import Config
from flask_session import Session


app = Flask(__name__)
app.config.from_object(Config)
sess = Session()
sess.init_app(app)

from src.sql import db
db = db()
db.init_db()
from src import routes
