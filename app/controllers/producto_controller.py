from app.models import db, Producto, MovimientoInventario
from flask import session
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def crear_producto(id_producto, nombre, descripcion, precio, stock, id_empresa):
    """
    Crear un nuevo producto
    """
    try:
        # Verificar que el ID no exista en la empresa
        existing = Producto.query.filter_by(
            id_producto=id_producto, 
            id_empresa=id_empresa
        ).first()
        
        if existing:
            return None, "Ya existe un producto con este ID en tu empresa"
        
        # Crear el producto
        nuevo_producto = Producto(
            id_producto=id_producto,
            nombre=nombre,
            descripcion=descripcion or None,
            precio=precio,
            stock=stock,
            id_empresa=id_empresa
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        # Registrar movimiento de inventario inicial
        if stock > 0:
            registrar_movimiento_inventario(
                id_producto=id_producto,
                tipo_movimiento="ENTRADA",
                cantidad=stock,
                motivo="Stock inicial"
            )
        
        return nuevo_producto, None
        
    except IntegrityError:
        db.session.rollback()
        return None, "Error de integridad: verifica que todos los datos sean válidos"
    except Exception as e:
        db.session.rollback()
        return None, f"Error al crear producto: {str(e)}"

def listar_productos(id_empresa):
    """
    Obtener todos los productos de una empresa
    """
    try:
        productos = Producto.query.filter_by(id_empresa=id_empresa).order_by(Producto.nombre).all()
        return productos
    except Exception as e:
        print(f"Error al listar productos: {str(e)}")
        return []

def obtener_producto(id_empresa, id_producto):
    """
    Obtener un producto específico
    """
    try:
        producto = Producto.query.filter_by(
            id_producto=id_producto,
            id_empresa=id_empresa
        ).first()
        return producto
    except Exception as e:
        print(f"Error al obtener producto: {str(e)}")
        return None

def actualizar_producto(producto, nombre, descripcion, precio, stock):
    """
    Actualizar un producto existente
    """
    try:
        # Guardar stock anterior para registrar movimiento si cambió
        stock_anterior = producto.stock
        
        # Actualizar datos
        producto.nombre = nombre
        producto.descripcion = descripcion or None
        producto.precio = precio
        
        # Si cambió el stock, registrar movimiento
        if stock != stock_anterior:
            diferencia = stock - stock_anterior
            tipo_movimiento = "ENTRADA" if diferencia > 0 else "SALIDA"
            cantidad = abs(diferencia)
            
            registrar_movimiento_inventario(
                id_producto=producto.id_producto,
                tipo_movimiento=tipo_movimiento,
                cantidad=cantidad,
                motivo=f"Ajuste manual: {stock_anterior} → {stock}"
            )
            
            producto.stock = stock
        
        db.session.commit()
        return True, None
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error al actualizar producto: {str(e)}"

def eliminar_producto(producto):
    """
    Eliminar un producto
    """
    try:
        # Verificar si tiene ventas asociadas
        if hasattr(producto, 'detalles_venta') and producto.detalles_venta:
            return False, "No se puede eliminar: el producto tiene ventas registradas"
        
        # Registrar movimiento de salida total si tenía stock
        if producto.stock > 0:
            registrar_movimiento_inventario(
                id_producto=producto.id_producto,
                tipo_movimiento="SALIDA",
                cantidad=producto.stock,
                motivo="Eliminación de producto"
            )
        
        db.session.delete(producto)
        db.session.commit()
        return True, None
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error al eliminar producto: {str(e)}"

def buscar_productos(id_empresa, termino_busqueda):
    """
    Buscar productos por nombre, descripción o ID
    """
    try:
        productos = Producto.query.filter(
            Producto.id_empresa == id_empresa,
            (Producto.nombre.ilike(f"%{termino_busqueda}%") |
             Producto.descripcion.ilike(f"%{termino_busqueda}%") |
             Producto.id_producto.ilike(f"%{termino_busqueda}%"))
        ).order_by(Producto.nombre).all()
        
        return productos
    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        return []

def obtener_productos_stock_bajo(id_empresa, limite=10):
    """
    Obtener productos con stock bajo
    """
    try:
        productos = Producto.query.filter(
            Producto.id_empresa == id_empresa,
            Producto.stock <= limite
        ).order_by(Producto.stock).all()
        
        return productos
    except Exception as e:
        print(f"Error al obtener productos con stock bajo: {str(e)}")
        return []

def registrar_movimiento_inventario(id_producto, tipo_movimiento, cantidad, motivo=""):
    """
    Registrar un movimiento de inventario
    """
    try:
        # Generar ID único para el movimiento
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        id_movimiento = f"MOV_{id_producto}_{timestamp}"
        
        movimiento = MovimientoInventario(
            id_movimiento=id_movimiento,
            tipo_movimiento=tipo_movimiento,
            fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cantidad=cantidad,
            id_producto=id_producto,
            id_usuario=session.get('usuario_id', 1)  # Usuario actual
        )
        
        db.session.add(movimiento)
        # No hacer commit aquí, se hace en la función que llama
        
        return True
    except Exception as e:
        print(f"Error al registrar movimiento: {str(e)}")
        return False

def actualizar_stock(id_empresa, id_producto, nuevo_stock, motivo="Ajuste manual"):
    """
    Actualizar solo el stock de un producto
    """
    try:
        producto = obtener_producto(id_empresa, id_producto)
        if not producto:
            return False, "Producto no encontrado"
        
        stock_anterior = producto.stock
        diferencia = nuevo_stock - stock_anterior
        
        if diferencia != 0:
            tipo_movimiento = "ENTRADA" if diferencia > 0 else "SALIDA"
            cantidad = abs(diferencia)
            
            registrar_movimiento_inventario(
                id_producto=id_producto,
                tipo_movimiento=tipo_movimiento,
                cantidad=cantidad,
                motivo=f"{motivo}: {stock_anterior} → {nuevo_stock}"
            )
        
        producto.stock = nuevo_stock
        db.session.commit()
        
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, f"Error al actualizar stock: {str(e)}"