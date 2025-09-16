from flask import Blueprint, render_template, redirect, url_for, flash
from app.schemas.empresa_schema import EmpresaForm
from app.controllers.empresa_controller import crear_empresa

empresa_bp = Blueprint("empresa", __name__)

@empresa_bp.route("/registrar_empresa", methods=["GET", "POST"])
def registrar_empresa():
    form = EmpresaForm()
    if form.validate_on_submit():
        empresa, error = crear_empresa(
            nit=form.nit.data,
            nombre=form.nombre.data,
            correo_electronico=form.correo_electronico.data,
            telefono_contacto=form.telefono_contacto.data
        )
        if error:
            flash(error, "danger")
        else:
            flash("Empresa registrada con éxito", "success")
            # Redirige al registro de usuario pasando el id_empresa
            return redirect(url_for("usuario.registrar_usuario", id_empresa=empresa.id_empresa))
    return render_template("registrar_empresa.html", form=form)
