from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from functools import wraps
from app.schemas.venta_schema import VentaForm, MetodoPagoForm
from app.controllers.venta_controller import (
    crear_venta,
    listar_ventas,
    obtener_venta,
    anular_venta,
    obtener_productos_disponibles,
    buscar_producto_venta,
    calcular_venta,
    obtener_metodos_pago,
    crear_metodo_pago,
    actualizar_metodo_pago,
    eliminar_metodo_pago,
    obtener_resumen_ventas_hoy
)

venta_bp = Blueprint("venta", __name__, url_prefix="/venta")

# ----------------------------------------------------------------------
# Decoradores de autenticación
# ----------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debes iniciar sesión para acceder a esta página", "warning")
            return redirect(url_for('usuario.login'))
        return f(*args, **kwargs)
    return decorated_function

def verificar_acceso_empresa(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        id_empresa = kwargs.get('id_empresa')
        if id_empresa and session.get('empresa_id') != id_empresa:
            flash("No tienes permisos para acceder a esta empresa", "danger")
            return redirect(url_for('venta.punto_venta', id_empresa=session.get('empresa_id')))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------------------------------------
# Punto de Venta Principal (POS)
# ----------------------------------------------------------------------
@venta_bp.route("/pos/<int:id_empresa>")
@login_required
@verificar_acceso_empresa
def punto_venta(id_empresa):
    """Pantalla principal del punto de venta"""
    productos = obtener_productos_disponibles(id_empresa)
    metodos_pago = obtener_metodos_pago(id_empresa)
    resumen_hoy = obtener_resumen_ventas_hoy(id_empresa)
    
    return render_template("ventas/punto_venta.html", 
                         productos=productos, 
                         metodos_pago=metodos_pago,
                         resumen_hoy=resumen_hoy,
                         id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Procesar Venta
# ----------------------------------------------------------------------
@venta_bp.route("/procesar/<int:id_empresa>", methods=["POST"])
@login_required
@verificar_acceso_empresa
def procesar_venta(id_empresa):
    """Procesar una nueva venta"""
    try:
        data = request.get_json()
        
        items = data.get('items', [])
        metodo_pago = data.get('metodo_pago')
        descuento = float(data.get('descuento', 0))
        
        if not items:
            return jsonify({'success': False, 'message': 'No hay productos en la venta'})
        
        if not metodo_pago:
            return jsonify({'success': False, 'message': 'Debe seleccionar un método de pago'})
        
        venta, error = crear_venta(
            items=items,
            metodo_pago=metodo_pago,
            descuento=descuento,
            id_empresa=id_empresa,
            id_usuario=session['usuario_id']
        )
        
        if error:
            return jsonify({'success': False, 'message': error})
        
        return jsonify({
            'success': True, 
            'message': f'Venta #{venta.id_venta} procesada exitosamente',
            'venta_id': venta.id_venta,
            'total': venta.total
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al procesar venta: {str(e)}'})

# ----------------------------------------------------------------------
# Buscar Producto para POS
# ----------------------------------------------------------------------
@venta_bp.route("/buscar_producto/<int:id_empresa>")
@login_required
@verificar_acceso_empresa
def buscar_producto(id_empresa):
    """Buscar producto por código o nombre para el POS"""
    termino = request.args.get('q', '').strip()
    
    if not termino:
        return jsonify([])
    
    productos = buscar_producto_venta(id_empresa, termino)
    
    return jsonify([{
        'id_producto': p.id_producto,
        'nombre': p.nombre,
        'precio': p.precio,
        'stock': p.stock,
        'disponible': p.stock > 0
    } for p in productos])

# ----------------------------------------------------------------------
# Historial de Ventas
# ----------------------------------------------------------------------
@venta_bp.route("/historial/<int:id_empresa>")
@login_required
@verificar_acceso_empresa
def historial(id_empresa):
    """Ver historial de ventas"""
    fecha_desde = request.args.get('desde')
    fecha_hasta = request.args.get('hasta')
    
    ventas = listar_ventas(id_empresa, fecha_desde, fecha_hasta)
    
    return render_template("ventas/historial.html", 
                         ventas=ventas, 
                         id_empresa=id_empresa,
                         fecha_desde=fecha_desde,
                         fecha_hasta=fecha_hasta)

# ----------------------------------------------------------------------
# Ver Detalle de Venta
# ----------------------------------------------------------------------
@venta_bp.route("/detalle/<int:id_empresa>/<int:id_venta>")
@login_required
@verificar_acceso_empresa
def detalle(id_empresa, id_venta):
    """Ver detalle de una venta específica"""
    venta = obtener_venta(id_empresa, id_venta)
    
    if not venta:
        flash("Venta no encontrada", "danger")
        return redirect(url_for("venta.historial", id_empresa=id_empresa))
    
    return render_template("ventas/detalle.html", 
                         venta=venta, 
                         id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Anular Venta
# ----------------------------------------------------------------------
@venta_bp.route("/anular/<int:id_empresa>/<int:id_venta>", methods=["POST"])
@login_required
@verificar_acceso_empresa
def anular(id_empresa, id_venta):
    """Anular una venta"""
    motivo = request.form.get('motivo', '').strip()
    
    if not motivo:
        flash("Debe especificar un motivo para anular la venta", "danger")
        return redirect(url_for("venta.detalle", id_empresa=id_empresa, id_venta=id_venta))
    
    exito, error = anular_venta(id_venta, motivo, session['usuario_id'])
    
    if error:
        flash(error, "danger")
    else:
        flash(f"Venta #{id_venta} anulada exitosamente", "success")
    
    return redirect(url_for("venta.historial", id_empresa=id_empresa))

# ----------------------------------------------------------------------
# Gestión de Métodos de Pago
# ----------------------------------------------------------------------
@venta_bp.route("/metodos_pago/<int:id_empresa>")
@login_required
@verificar_acceso_empresa
def metodos_pago(id_empresa):
    """Gestionar métodos de pago"""
    metodos = obtener_metodos_pago(id_empresa)
    
    return render_template("ventas/metodos_pago.html", 
                         metodos=metodos, 
                         id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Crear Método de Pago
# ----------------------------------------------------------------------
@venta_bp.route("/metodos_pago/crear/<int:id_empresa>", methods=["GET", "POST"])
@login_required
@verificar_acceso_empresa
def crear_metodo(id_empresa):
    """Crear nuevo método de pago"""
    form = MetodoPagoForm()
    
    if form.validate_on_submit():
        exito, error = crear_metodo_pago(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            activo=form.activo.data,
            id_empresa=id_empresa
        )
        
        if error:
            flash(error, "danger")
        else:
            flash("Método de pago creado exitosamente ✅", "success")
            return redirect(url_for("venta.metodos_pago", id_empresa=id_empresa))
    
    return render_template("ventas/crear_metodo.html", 
                         form=form, 
                         id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Editar Método de Pago
# ----------------------------------------------------------------------
@venta_bp.route("/metodos_pago/editar/<int:id_empresa>/<int:id_metodo>", methods=["GET", "POST"])
@login_required
@verificar_acceso_empresa
def editar_metodo(id_empresa, id_metodo):
    """Editar método de pago existente"""
    metodo = next((m for m in obtener_metodos_pago(id_empresa) if m.id == id_metodo), None)
    
    if not metodo:
        flash("Método de pago no encontrado", "danger")
        return redirect(url_for("venta.metodos_pago", id_empresa=id_empresa))
    
    form = MetodoPagoForm(obj=metodo)
    
    if form.validate_on_submit():
        exito, error = actualizar_metodo_pago(
            id_metodo,
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            activo=form.activo.data
        )
        
        if error:
            flash(error, "danger")
        else:
            flash("Método de pago actualizado exitosamente ✅", "success")
            return redirect(url_for("venta.metodos_pago", id_empresa=id_empresa))
    
    return render_template("ventas/editar_metodo.html", 
                         form=form, 
                         metodo=metodo,
                         id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Eliminar Método de Pago
# ----------------------------------------------------------------------
@venta_bp.route("/metodos_pago/eliminar/<int:id_empresa>/<int:id_metodo>", methods=["POST"])
@login_required
@verificar_acceso_empresa
def eliminar_metodo(id_empresa, id_metodo):
    """Eliminar método de pago"""
    exito, error = eliminar_metodo_pago(id_metodo)
    
    if error:
        flash(error, "danger")
    else:
        flash("Método de pago eliminado exitosamente ✅", "success")
    
    return redirect(url_for("venta.metodos_pago", id_empresa=id_empresa))

# ----------------------------------------------------------------------
# API para cálculos en tiempo real
# ----------------------------------------------------------------------
@venta_bp.route("/api/calcular/<int:id_empresa>", methods=["POST"])
@login_required
@verificar_acceso_empresa
def api_calcular(id_empresa):
    """Calcular totales de venta en tiempo real"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        descuento = float(data.get('descuento', 0))
        
        resultado = calcular_venta(items, descuento)
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ----------------------------------------------------------------------
# Generar Factura
# ----------------------------------------------------------------------
@venta_bp.route("/factura/<int:id_empresa>/<int:id_venta>")
@login_required
@verificar_acceso_empresa
def generar_factura(id_empresa, id_venta):
    """Generar factura tipo POS"""
    venta = obtener_venta(id_empresa, id_venta)
    
    if not venta:
        flash("Venta no encontrada", "danger")
        return redirect(url_for("venta.historial", id_empresa=id_empresa))
    
    # Información de la empresa (esto debería venir de la BD)
    empresa_info = {
        'nombre': 'SIIGO S.A.S',  # Cambiar por datos reales
        'nit': '800200100-0',
        'direccion': 'Call 54 32 71',
        'ciudad': 'Bogotá',
        'telefono': '41512108',
        'resolucion': '191816549/8156',
        'fecha_autorizacion': '2019/01/22',
        'prefijo_desde': '1',
        'prefijo_hasta': '1000000'
    }
    
    # Información del cliente (por defecto)
    cliente_info = {
        'nombre': 'CUANTAS MENORES',
        'documento': '222222222-0',
        'direccion': 'CALLE FALSA 123'
    }
    
    # Información del sistema
    sistema_info = {
        'elaborado': 'SIIGO/POS',
        'website': 'www.siigo.com',
        'nit': '830.048.145'
    }
    
    return render_template("ventas/factura.html", 
                         venta=venta, 
                         empresa_info=empresa_info,
                         cliente_info=cliente_info,
                         sistema_info=sistema_info)

# ----------------------------------------------------------------------
# Dashboard de Ventas
# ----------------------------------------------------------------------
@venta_bp.route("/dashboard/<int:id_empresa>")
@login_required
@verificar_acceso_empresa
def dashboard(id_empresa):
    """Dashboard con estadísticas de ventas"""
    resumen_hoy = obtener_resumen_ventas_hoy(id_empresa)
    
    return render_template("ventas/dashboard.html", 
                         resumen=resumen_hoy, 
                         id_empresa=id_empresa)