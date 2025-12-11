import os
from flask import Flask
from .models import db
from flask_bcrypt import Bcrypt

def create_app():
    app = Flask(__name__)

    # Obtener la URL de la base de datos que Render provee automáticamente
    uri = os.getenv("DATABASE_URL")

    # Render entrega URLs con formato antiguo: "postgres://"
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecreto")

    db.init_app(app)

    bcrypt = Bcrypt()
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()

    return app
