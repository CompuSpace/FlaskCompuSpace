from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.schemas.usuario_schema import UsuarioForm
from app.controllers.usuario_controller import (
    crear_usuario,
    autenticar_usuario,
    listar_usuarios,
    obtener_usuario,
    actualizar_usuario,
    eliminar_usuario
)

usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuario")

# ----------------------------------------------------------------------
# Registrar usuario
# ----------------------------------------------------------------------
@usuario_bp.route("/registrar_usuario/<int:id_empresa>", methods=["GET", "POST"])
def registrar_usuario(id_empresa):
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
            flash("Usuario registrado con éxito ✅", "success")
            return redirect(url_for("usuario.login"))

    else:
        if form.is_submitted():
            flash("Por favor corrige los errores en el formulario ❌", "danger")

    return render_template("registrar_usuario.html", form=form, id_empresa=id_empresa)


# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------
@usuario_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nom_usuario = request.form.get("nom_usuario")
        contrasena = request.form.get("contrasena")

        usuario, error = autenticar_usuario(nom_usuario, contrasena)

        if error:  
            flash(error, "danger")  # ← Usa el mensaje que viene de tu controller ("Usuario no encontrado" o "Contraseña incorrecta")
            return render_template("login.html")

        # Si todo bien → guardar sesión
        session["usuario_id"] = usuario.id_usuario
        session["empresa_id"] = usuario.id_empresa
        session["rol"] = usuario.rol  
        session["nom_usuario"] = usuario.nom_usuario 

        flash("Inicio de sesión exitoso ✅", "success")
        return redirect(url_for("usuario.listar", id_empresa=session["empresa_id"]))

    return render_template("login.html")


# ----------------------------------------------------------------------
# Logout
# ----------------------------------------------------------------------
@usuario_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión", "info")
    return redirect(url_for("usuario.login"))


# ----------------------------------------------------------------------
# CRUD de usuarios (asociados a empresa)
# ----------------------------------------------------------------------
@usuario_bp.route("/listar/<int:id_empresa>")
def listar(id_empresa):
    usuarios = listar_usuarios(id_empresa)
    return render_template("usuarios/listar.html", usuarios=usuarios, id_empresa=id_empresa)


@usuario_bp.route("/editar/<int:id_empresa>/<int:id_usuario>", methods=["GET", "POST"])
def editar(id_empresa, id_usuario):
    usuario = obtener_usuario(id_empresa, id_usuario)
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("usuario.listar", id_empresa=id_empresa))

    form = UsuarioForm(obj=usuario)

    if form.validate_on_submit():
        actualizar_usuario(
            usuario,
            nom_usuario=form.nom_usuario.data,
            contrasena=form.contrasena.data,
            correo_recuperacion=form.correo_recuperacion.data,
            rol=form.rol.data
        )
        flash("Usuario actualizado con éxito ✅", "success")
        return redirect(url_for("usuario.listar", id_empresa=id_empresa))

    return render_template("usuarios/editar.html", form=form, usuario=usuario, id_empresa=id_empresa)


@usuario_bp.route("/eliminar/<int:id_empresa>/<int:id_usuario>", methods=["POST"])
def eliminar(id_empresa, id_usuario):
    usuario = obtener_usuario(id_empresa, id_usuario)
    if not usuario:
        flash("Usuario no encontrado", "danger")
    else:
        eliminar_usuario(usuario)
        flash("Usuario eliminado con éxito ✅", "success")

    return redirect(url_for("usuario.listar", id_empresa=id_empresa))

# ----------------------------------------------------------------------
# Gestión de perfil
# ----------------------------------------------------------------------
@usuario_bp.route("/perfil")
def perfil():
    # Verificar que haya sesión
    if 'usuario_id' not in session or 'empresa_id' not in session:
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for('usuario.login'))
    
    # Obtener usuario usando tu función del controller
    usuario = obtener_usuario(
        id_empresa=session['empresa_id'],
        id_usuario=session['usuario_id']
    )

    # Validar si existe en la base de datos
    if not usuario:
        flash("El usuario no existe o la empresa no coincide", "danger")
        return redirect(url_for('usuario.login'))

    # Enviar a plantilla
    return render_template("usuarios/perfil.html", usuario=usuario)

@usuario_bp.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for('usuario.login'))
    
    usuario = obtener_usuario(session['empresa_id'], session['usuario_id'])
    if not usuario:
        flash("Error al cargar el perfil", "danger")
        return redirect(url_for("usuario.listar", id_empresa=session['empresa_id']))

    form = UsuarioForm(obj=usuario)
    
    if form.validate_on_submit():
        actualizar_usuario(
            usuario,
            nom_usuario=form.nom_usuario.data,
            contrasena=form.contrasena.data if form.contrasena.data else None,
            correo_recuperacion=form.correo_recuperacion.data,
            rol=form.rol.data
        )
        
        # Actualizar session si cambió el nombre
        session['nom_usuario'] = form.nom_usuario.data
        flash("Perfil actualizado con éxito ✅", "success")
        return redirect(url_for("usuario.perfil"))

    return render_template("usuarios/editar_perfil.html", form=form, usuario=usuario)
