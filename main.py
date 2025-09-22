from flask import render_template
from app import create_app
from app.routes.empresa_routes import empresa_bp
from app.routes.usuario_routes import usuario_bp
from app.routes.producto_routes import producto_bp


app = create_app()

# Registrar los blueprints
app.register_blueprint(empresa_bp)
app.register_blueprint(usuario_bp, url_prefix="/usuario")
app.register_blueprint(producto_bp)


# Ruta principal
@app.route("/")
def index():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)

