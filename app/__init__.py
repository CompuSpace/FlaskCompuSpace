from flask import Flask
from .models import db
from flask_bcrypt import Bcrypt

def create_app():
    app = Flask(__name__)

    uri = os.getenv("postgresql://sistema_inventario_iqq9_user:RHt1XffIELq3lDp1Fm4jfU5c7aDQX1vg@dpg-d4thqpvpm1nc73982lc0-a/sistema_inventario_iqq9")
    if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "supersecreto"
     
    db.init_app(app)
     
    bcrypt = Bcrypt()
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()

    return app
