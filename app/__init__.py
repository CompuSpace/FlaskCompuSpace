from flask import Flask
from .models import db
from flask_bcrypt import Bcrypt

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/sistema_inventario'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "supersecreto"
     
    db.init_app(app)
     
    bcrypt = Bcrypt()
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()

    return app
