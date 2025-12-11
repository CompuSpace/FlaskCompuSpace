from app.models import db, Usuario
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# ----------------------------------------------------------------------
# Crear usuario
# ----------------------------------------------------------------------
def crear_usuario(nom_usuario, contrasena, correo_recuperacion, rol, id_empresa):
    usuario_existente = Usuario.query.filter_by(
        nom_usuario=nom_usuario,
        id_empresa=id_empresa
    ).first()
    if usuario_existente:
        return None, "El usuario ya existe en esta empresa"

    # Si es el primer usuario de la empresa, darle rol admin automáticamente
    existe_usuario = Usuario.query.filter_by(id_empresa=id_empresa).first()
    if not existe_usuario:
        rol = 1  # Admin

    # Generar hash con bcrypt
    hashed_password = bcrypt.generate_password_hash(contrasena).decode("utf-8")

    nuevo_usuario = Usuario(
        nom_usuario=nom_usuario,
        contrasena=hashed_password,
        correo_recuperacion=correo_recuperacion,
        rol=int(rol),
        id_empresa=int(id_empresa)
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return nuevo_usuario, None


# ----------------------------------------------------------------------
# Autenticación
# ----------------------------------------------------------------------
def autenticar_usuario(nom_usuario, contrasena):
    usuario = Usuario.query.filter_by(
        nom_usuario=nom_usuario,
    ).first()

    if not usuario:
        return None, "Usuario no encontrado en esta empresa"

    if not bcrypt.check_password_hash(usuario.contrasena, contrasena):
        return None, "Contraseña incorrecta"

    return usuario, None


# ----------------------------------------------------------------------
# CRUD
# ----------------------------------------------------------------------
def listar_usuarios(id_empresa):
    return Usuario.query.filter_by(id_empresa=id_empresa).all()


def obtener_usuario(id_empresa, id_usuario):
    return Usuario.query.filter_by(id_empresa=id_empresa, id_usuario=id_usuario).first()


def actualizar_usuario(usuario, nom_usuario, contrasena, correo_recuperacion, rol):
    usuario.nom_usuario = nom_usuario
    if contrasena:
        usuario.contrasena = bcrypt.generate_password_hash(contrasena).decode("utf-8")
    usuario.correo_recuperacion = correo_recuperacion
    usuario.rol = int(rol)
    db.session.commit()
    return usuario


def eliminar_usuario(usuario):
    db.session.delete(usuario)
    db.session.commit()
