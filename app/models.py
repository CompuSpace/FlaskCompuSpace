from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Empresa(db.Model):
    __tablename__ = "empresa"

    id_empresa = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nit = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    correo_electronico = db.Column(db.String(100), nullable=False)
    telefono_contacto = db.Column(db.String(20), nullable=False)

    usuarios = db.relationship("Usuario", back_populates="empresa")
    productos = db.relationship("Producto", back_populates="empresa")
    proveedores = db.relationship("Proveedor", back_populates="empresa")
    ventas = db.relationship("Venta", back_populates="empresa")


class Rol(db.Model):
    __tablename__ = "rol"

    id_rol = db.Column(db.String(100), primary_key=True)
    nombre_rol = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(100))

    usuarios = db.relationship("Usuario", back_populates="rol_rel")


class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_usuario = db.Column(db.String(100), nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), db.ForeignKey("rol.id_rol"), nullable=False)
    correo_recuperacion = db.Column(db.String(100))
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresa.id_empresa"), nullable=False)

    empresa = db.relationship("Empresa", back_populates="usuarios")
    rol_rel = db.relationship("Rol", back_populates="usuarios")
    ventas = db.relationship("Venta", back_populates="usuario")
    movimientos = db.relationship("MovimientoInventario", back_populates="usuario")
    desactivaciones = db.relationship(
        "DesactivacionUsuario",
        back_populates="usuario",
        foreign_keys="DesactivacionUsuario.id_usuario"
    )


class Proveedor(db.Model):
    __tablename__ = "proveedor"

    id_proveedores = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.Integer)
    correo = db.Column(db.String(100))
    direccion = db.Column(db.String(100))
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresa.id_empresa"), nullable=False)

    empresa = db.relationship("Empresa", back_populates="proveedores")


class Producto(db.Model):
    __tablename__ = "producto"

    id_producto = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(100))
    precio = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresa.id_empresa"), nullable=False)

    empresa = db.relationship("Empresa", back_populates="productos")
    detalles_venta = db.relationship("DetalleVenta", back_populates="producto")
    movimientos = db.relationship("MovimientoInventario", back_populates="producto")


class Venta(db.Model):
    __tablename__ = "venta"

    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.String(100), nullable=False)
    metodo_pago = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresa.id_empresa"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)

    usuario = db.relationship("Usuario", back_populates="ventas")
    empresa = db.relationship("Empresa", back_populates="ventas")
    detalles = db.relationship("DetalleVenta", back_populates="venta")


class DetalleVenta(db.Model):
    __tablename__ = "detalle_venta"

    id_detalle = db.Column(db.String(100), primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey("venta.id_venta"), nullable=False)
    id_producto = db.Column(db.String(100), db.ForeignKey("producto.id_producto"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)

    venta = db.relationship("Venta", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles_venta")


class MovimientoInventario(db.Model):
    __tablename__ = "movimiento_inventario"

    id_movimiento = db.Column(db.String(100), primary_key=True)
    tipo_movimiento = db.Column(db.String(100), nullable=False)
    fecha_hora = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    id_producto = db.Column(db.String(100), db.ForeignKey("producto.id_producto"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)

    producto = db.relationship("Producto", back_populates="movimientos")
    usuario = db.relationship("Usuario", back_populates="movimientos")


class DesactivacionUsuario(db.Model):
    __tablename__ = "desactivacion_usuario"

    id_desactivacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    fecha_desactivacion = db.Column(db.DateTime, default=datetime.utcnow)
    id_admin = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)

    usuario = db.relationship(
        "Usuario",
        back_populates="desactivaciones",
        foreign_keys=[id_usuario]
    )
    admin = db.relationship("Usuario", foreign_keys=[id_admin])
