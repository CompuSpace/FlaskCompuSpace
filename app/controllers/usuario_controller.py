from app.models import db, Usuario
from werkzeug.security import generate_password_hash

def crear_usuario(nom_usuario, contrasena, correo_recuperacion, rol, id_empresa):
    # 1. Validar si el usuario ya existe
    usuario_existente = Usuario.query.filter_by(nom_usuario=nom_usuario).first()
    if usuario_existente:
        return None, "El usuario ya existe"

    # 2. Crear nuevo usuario
    nuevo_usuario = Usuario(
        nom_usuario=nom_usuario,
        contrasena=generate_password_hash(contrasena),
        correo_recuperacion=correo_recuperacion,
        rol=int(rol),   # ✅ aquí conviertes el rol recibido en número
        id_empresa=int(id_empresa)  # por seguridad conviértelo también a int
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return nuevo_usuario, None

    #Login y autenticación
from werkzeug.security import check_password_hash
def autenticar_usuario(nom_usuario, contrasena):
    # 1. Buscar el usuario por nombre
    usuario = Usuario.query.filter_by(nom_usuario=nom_usuario).first()
    if not usuario:
        return None, "Usuario no encontrado"

    # 2. Verificar la contraseña
    if not check_password_hash(usuario.contrasena, contrasena):
        return None, "Contraseña incorrecta"

    # 3. Retornar usuario válido
    return usuario, None