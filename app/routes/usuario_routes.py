from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.schemas.usuario_schema import UsuarioForm
from app.controllers.usuario_controller import crear_usuario

usuario_bp = Blueprint("usuario", __name__)

@usuario_bp.route("/registrar_usuario", methods=["GET", "POST"])
def registrar_usuario():
    id_empresa = request.args.get("id_empresa")  # llega desde la empresa
    form = UsuarioForm()
    if form.validate_on_submit():
        usuario, error = crear_usuario(
            nom_usuario=form.nom_usuario.data,
            contrasena=form.contrasena.data,
            correo_recuperacion=form.correo_recuperacion.data,
            rol=form.rol.data,
            id_empresa=id_empresa
        )
        if error:
            flash(error, "danger")
        else:
            flash("Usuario registrado con éxito", "success")
            return redirect(url_for("empresa.registrar_empresa"))  # o al login
    return render_template("registrar_usuario.html", form=form, id_empresa=id_empresa)
