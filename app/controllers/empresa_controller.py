from app.models import db, Empresa

def crear_empresa(nit, nombre, correo_electronico, telefono_contacto):
    # Convertir nit y telefono a string para evitar errores con VARCHAR
    nit = str(nit)
    telefono_contacto = str(telefono_contacto)

    # 1. Validar si ya existe la empresa
    empresa_existente = Empresa.query.filter_by(nit=nit).first()
    if empresa_existente:
        return None, "La empresa ya existe"

    # 2. Crear nueva empresa
    nueva_empresa = Empresa(
        nit=nit,
        nombre=nombre,
        correo_electronico=correo_electronico,
        telefono_contacto=telefono_contacto
    )
    db.session.add(nueva_empresa)
    db.session.commit()

    return nueva_empresa, None
