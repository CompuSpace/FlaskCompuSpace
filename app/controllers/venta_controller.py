from app.models import db, Venta, DetalleVenta, Producto, MovimientoInventario, Usuario
from flask import session
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, desc

# Modelo para métodos de pago (temporal, mientras no esté en la BD)
class MetodoPago:
    def __init__(self, id, nombre, descripcion="", activo=True):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.activo = activo

# Métodos de pago predeterminados (luego se pueden guardar en BD)
METODOS_PAGO_DEFAULT = {
    1: MetodoPago(1, "💵 Efectivo", "Pago en dinero físico", True),
    2: MetodoPago(2, "💳 Tarjeta de Débito", "Pago con tarjeta débito", True),
    3: MetodoPago(3, "💳 Tarjeta de Crédito", "Pago con tarjeta crédito", True),
    4: MetodoPago(4, "📱 Transferencia", "Transferencia bancaria", True),
    5: MetodoPago(5, "📱 PSE", "Pagos Seguros en Línea", True),
    6: MetodoPago(6, "🏦 Consignación", "Depósito bancario", True),
}

def crear_venta(items, metodo_pago, descuento=0, id_empresa=None, id_usuario=None):
    """
    Crear una nueva venta con sus detalles
    """
    try:
        # Calcular totales
        subtotal = 0
        cantidad_total = 0
        detalles_venta = []
        
        # Validar productos y calcular subtotal
        for item in items:
            producto = Producto.query.filter_by(
                id_producto=item['id_producto'],
                id_empresa=id_empresa
            ).first()
            
            if not producto:
                return None, f"Producto {item['id_producto']} no encontrado"
            
            cantidad = int(item['cantidad'])
            if cantidad <= 0:
                return None, f"La cantidad debe ser mayor a 0"
            
            if producto.stock < cantidad:
                return None, f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
            
            precio_unitario = producto.precio
            subtotal_item = precio_unitario * cantidad
            subtotal += subtotal_item
            cantidad_total += cantidad
            
            detalles_venta.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal_item
            })
        
        # Aplicar descuento
        descuento_valor = (subtotal * descuento / 100) if descuento > 0 else 0
        total = subtotal - descuento_valor
        
        # Crear la venta
        venta = Venta(
            fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            metodo_pago=metodo_pago,
            total=int(total),
            subtotal=int(subtotal),
            cantidad=cantidad_total,
            id_usuario=id_usuario,
            id_empresa=id_empresa
        )
        
        db.session.add(venta)
        db.session.flush()  # Para obtener el ID de la venta
        
        # Crear detalles de venta y actualizar stock
        for detalle_info in detalles_venta:
            # Crear detalle de venta
            detalle = DetalleVenta(
                id_detalle=f"DET_{venta.id_venta}_{detalle_info['producto'].id_producto}_{datetime.now().strftime('%H%M%S')}",
                id_venta=venta.id_venta,
                id_producto=detalle_info['producto'].id_producto,
                cantidad=detalle_info['cantidad'],
                precio_unitario=detalle_info['precio_unitario'],
                subtotal=detalle_info['subtotal']
            )
            db.session.add(detalle)
            
            # Actualizar stock del producto
            producto = detalle_info['producto']
            nuevo_stock = producto.stock - detalle_info['cantidad']
            producto.stock = nuevo_stock
            
            # Registrar movimiento de inventario
            registrar_movimiento_inventario(
                id_producto=producto.id_producto,
                tipo_movimiento="SALIDA",
                cantidad=detalle_info['cantidad'],
                motivo=f"Venta #{venta.id_venta}",
                id_usuario=id_usuario
            )
        
        db.session.commit()
        return venta, None
        
    except Exception as e:
        db.session.rollback()
        return None, f"Error al procesar venta: {str(e)}"

def listar_ventas(id_empresa, fecha_desde=None, fecha_hasta=None, limit=50):
    """
    Obtener lista de ventas con filtros
    """
    try:
        query = Venta.query.filter_by(id_empresa=id_empresa)
        
        if fecha_desde:
            query = query.filter(func.date(Venta.fecha_hora) >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(func.date(Venta.fecha_hora) <= fecha_hasta)
        
        ventas = query.order_by(desc(Venta.id_venta)).limit(limit).all()
        return ventas
        
    except Exception as e:
        print(f"Error al listar ventas: {str(e)}")
        return []

def obtener_venta(id_empresa, id_venta):
    """
    Obtener una venta específica con sus detalles
    """
    try:
        venta = Venta.query.filter_by(
            id_venta=id_venta,
            id_empresa=id_empresa
        ).first()
        return venta
    except Exception as e:
        print(f"Error al obtener venta: {str(e)}")
        return None

def obtener_productos_disponibles(id_empresa):
    """
    Obtener productos disponibles para la venta (con stock > 0)
    """
    try:
        productos = Producto.query.filter(
            Producto.id_empresa == id_empresa,
            Producto.stock > 0
        ).order_by(Producto.nombre).all()
        return productos
    except Exception as e:
        print(f"Error al obtener productos: {str(e)}")
        return []

def buscar_producto_venta(id_empresa, termino_busqueda):
    """
    Buscar productos para la venta por nombre o ID
    """
    try:
        productos = Producto.query.filter(
            Producto.id_empresa == id_empresa,
            (Producto.nombre.ilike(f"%{termino_busqueda}%") |
             Producto.id_producto.ilike(f"%{termino_busqueda}%"))
        ).limit(10).all()
        
        return productos
    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        return []

def calcular_venta(items, descuento=0):
    """
    Calcular totales de una venta sin crearla
    """
    try:
        subtotal = 0
        cantidad_total = 0
        items_calculados = []
        
        for item in items:
            cantidad = int(item.get('cantidad', 0))
            precio = float(item.get('precio', 0))
            subtotal_item = precio * cantidad
            
            subtotal += subtotal_item
            cantidad_total += cantidad
            
            items_calculados.append({
                'id_producto': item.get('id_producto'),
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal_item
            })
        
        descuento_valor = (subtotal * descuento / 100) if descuento > 0 else 0
        total = subtotal - descuento_valor
        
        return {
            'items': items_calculados,
            'cantidad_total': cantidad_total,
            'subtotal': subtotal,
            'descuento_porcentaje': descuento,
            'descuento_valor': descuento_valor,
            'total': total
        }
        
    except Exception as e:
        return {'error': str(e)}

def obtener_metodos_pago(id_empresa):
    """
    Obtener métodos de pago disponibles
    """
    # Por ahora devolvemos los métodos predeterminados
    # En el futuro se pueden personalizar por empresa
    return [metodo for metodo in METODOS_PAGO_DEFAULT.values() if metodo.activo]

def crear_metodo_pago(nombre, descripcion="", activo=True, id_empresa=None):
    """
    Crear nuevo método de pago personalizado
    """
    try:
        # Por ahora agregamos al diccionario temporal
        # En el futuro se guardará en BD
        nuevo_id = max(METODOS_PAGO_DEFAULT.keys()) + 1
        nuevo_metodo = MetodoPago(nuevo_id, nombre, descripcion, activo)
        METODOS_PAGO_DEFAULT[nuevo_id] = nuevo_metodo
        
        return True, None
    except Exception as e:
        return False, f"Error al crear método de pago: {str(e)}"

def actualizar_metodo_pago(id_metodo, nombre, descripcion="", activo=True):
    """
    Actualizar método de pago existente
    """
    try:
        if id_metodo in METODOS_PAGO_DEFAULT:
            metodo = METODOS_PAGO_DEFAULT[id_metodo]
            metodo.nombre = nombre
            metodo.descripcion = descripcion
            metodo.activo = activo
            return True, None
        else:
            return False, "Método de pago no encontrado"
    except Exception as e:
        return False, f"Error al actualizar método de pago: {str(e)}"

def eliminar_metodo_pago(id_metodo):
    """
    Eliminar método de pago
    """
    try:
        if id_metodo in METODOS_PAGO_DEFAULT and id_metodo > 6:  # No eliminar los básicos
            del METODOS_PAGO_DEFAULT[id_metodo]
            return True, None
        else:
            return False, "No se puede eliminar este método de pago"
    except Exception as e:
        return False, f"Error al eliminar método de pago: {str(e)}"

def anular_venta(id_venta, motivo, id_usuario):
    """
    Anular una venta y restaurar stock
    """
    try:
        venta = Venta.query.get(id_venta)
        if not venta:
            return False, "Venta no encontrada"
        
        # Restaurar stock de todos los productos
        for detalle in venta.detalles:
            producto = detalle.producto
            producto.stock += detalle.cantidad
            
            # Registrar movimiento de devolución
            registrar_movimiento_inventario(
                id_producto=producto.id_producto,
                tipo_movimiento="ENTRADA",
                cantidad=detalle.cantidad,
                motivo=f"Anulación venta #{id_venta}: {motivo}",
                id_usuario=id_usuario
            )
        
        # Marcar venta como anulada (podrías agregar un campo 'estado' a la tabla)
        # Por ahora, podrías cambiar el total a negativo o agregar un prefijo
        venta.metodo_pago = f"ANULADA - {venta.metodo_pago}"
        
        db.session.commit()
        return True, None
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error al anular venta: {str(e)}"

def obtener_resumen_ventas_hoy(id_empresa):
    """
    Obtener resumen de ventas del día actual
    """
    try:
        hoy = date.today()
        
        query = Venta.query.filter(
            Venta.id_empresa == id_empresa,
            func.date(Venta.fecha_hora) == hoy,
            ~Venta.metodo_pago.like('ANULADA%')  # Excluir anuladas
        )
        
        ventas_hoy = query.all()
        
        total_ventas = len(ventas_hoy)
        total_ingresos = sum(venta.total for venta in ventas_hoy)
        total_productos = sum(venta.cantidad for venta in ventas_hoy)
        
        # Métodos de pago más usados
        metodos_count = {}
        for venta in ventas_hoy:
            metodo = venta.metodo_pago
            metodos_count[metodo] = metodos_count.get(metodo, 0) + 1
        
        return {
            'fecha': hoy,
            'total_ventas': total_ventas,
            'total_ingresos': total_ingresos,
            'total_productos': total_productos,
            'promedio_venta': total_ingresos / total_ventas if total_ventas > 0 else 0,
            'metodos_populares': sorted(metodos_count.items(), key=lambda x: x[1], reverse=True)[:3],
            'ventas_recientes': sorted(ventas_hoy, key=lambda x: x.fecha_hora, reverse=True)[:5]
        }
        
    except Exception as e:
        print(f"Error al obtener resumen: {str(e)}")
        return {
            'fecha': date.today(),
            'total_ventas': 0,
            'total_ingresos': 0,
            'total_productos': 0,
            'promedio_venta': 0,
            'metodos_populares': [],
            'ventas_recientes': []
        }

def registrar_movimiento_inventario(id_producto, tipo_movimiento, cantidad, motivo, id_usuario):
    """
    Registrar movimiento de inventario
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        id_movimiento = f"MOV_{id_producto}_{timestamp}"
        
        movimiento = MovimientoInventario(
            id_movimiento=id_movimiento,
            tipo_movimiento=tipo_movimiento,
            fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cantidad=cantidad,
            id_producto=id_producto,
            id_usuario=id_usuario
        )
        
        db.session.add(movimiento)
        return True
        
    except Exception as e:
        print(f"Error al registrar movimiento: {str(e)}")
        return False

def obtener_productos_mas_vendidos(id_empresa, dias=30, limit=10):
    """
    Obtener productos más vendidos en los últimos días
    """
    try:
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        # Subconsulta para sumar cantidades por producto
        subquery = db.session.query(
            DetalleVenta.id_producto,
            func.sum(DetalleVenta.cantidad).label('total_vendido')
        ).join(Venta).filter(
            Venta.id_empresa == id_empresa,
            Venta.fecha_hora >= fecha_limite,
            ~Venta.metodo_pago.like('ANULADA%')
        ).group_by(DetalleVenta.id_producto).subquery()
        
        # Query principal con información del producto
        productos = db.session.query(
            Producto,
            subquery.c.total_vendido
        ).join(subquery, Producto.id_producto == subquery.c.id_producto)\
        .order_by(desc(subquery.c.total_vendido))\
        .limit(limit).all()
        
        return productos
        
    except Exception as e:
        print(f"Error al obtener productos más vendidos: {str(e)}")
        return []

def obtener_estadisticas_ventas(id_empresa, fecha_desde=None, fecha_hasta=None):
    """
    Obtener estadísticas detalladas de ventas
    """
    try:
        query = Venta.query.filter(
            Venta.id_empresa == id_empresa,
            ~Venta.metodo_pago.like('ANULADA%')
        )
        
        if fecha_desde:
            query = query.filter(func.date(Venta.fecha_hora) >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(func.date(Venta.fecha_hora) <= fecha_hasta)
        
        ventas = query.all()
        
        if not ventas:
            return {
                'total_ventas': 0,
                'total_ingresos': 0,
                'promedio_venta': 0,
                'venta_maxima': 0,
                'venta_minima': 0,
                'por_metodo_pago': {},
                'por_dia': {},
                'productos_vendidos': 0
            }
        
        totales = [venta.total for venta in ventas]
        metodos = {}
        por_dia = {}
        total_productos = 0
        
        for venta in ventas:
            # Contar por método de pago
            metodo = venta.metodo_pago
            if metodo not in metodos:
                metodos[metodo] = {'count': 0, 'total': 0}
            metodos[metodo]['count'] += 1
            metodos[metodo]['total'] += venta.total
            
            # Contar por día
            fecha = venta.fecha_hora.split(' ')[0] if isinstance(venta.fecha_hora, str) else venta.fecha_hora.strftime('%Y-%m-%d')
            if fecha not in por_dia:
                por_dia[fecha] = {'ventas': 0, 'total': 0}
            por_dia[fecha]['ventas'] += 1
            por_dia[fecha]['total'] += venta.total
            
            # Contar productos
            total_productos += venta.cantidad
        
        return {
            'total_ventas': len(ventas),
            'total_ingresos': sum(totales),
            'promedio_venta': sum(totales) / len(totales),
            'venta_maxima': max(totales),
            'venta_minima': min(totales),
            'por_metodo_pago': metodos,
            'por_dia': por_dia,
            'productos_vendidos': total_productos
        }
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {str(e)}")
        return {}

from datetime import timedelta