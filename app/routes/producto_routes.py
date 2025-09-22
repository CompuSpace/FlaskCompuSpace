from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps
from app.schemas.producto_schema import ProductoForm
from app.controllers.producto_controller import (
    crear_producto,
    listar_productos,
    obtener_producto,
    actualizar_producto,
    eliminar_producto,
    buscar_productos
)

producto_bp = Blueprint("producto", __name__, url_prefix="/producto")

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
            return redirect(url_for('producto.listar', id_empresa=session.get('empresa_id')))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------------------------------------------------
# Listar productos
# ----------------------------------------------------------------------
@producto_bp.route("/listar/<int:id_empresa>")
@login_required
@verificar_acceso_empresa
def listar(id_empresa):
    # Obtener parámetros de búsqueda
    busqueda = request.args.get('busqueda', '').strip()
    
    if busqueda:
        productos = buscar_productos(id_empresa, busqueda)
        flash(f"Se encontraron {len(productos)} productos con: '{busqueda}'", "info")
    else:
        productos = listar_productos(id_empresa)
    
    return render_template("productos/listar.html", 
                         productos=productos, 
                         id_empresa=id_empresa,
                         busqueda=busqueda)

# ----------------------------------------------------------------------
# Crear producto
# ----------------------------------------------------------------------
@producto_bp.route("/crear/<int:id_empresa>", methods=["GET", "POST"])
@login_required
@verificar_acceso_empresa
def crear(id_empresa):
    form = ProductoForm()

    if form.validate_on_submit():
        exito, error = crear_producto(
            id_producto=form.id_producto.data,
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            stock=form.stock.data,
            id_empresa=id_empresa
        )

        if error:
            flash(error, "danger")
        else:
            flash("Producto creado con éxito ✅", "success")
            return redirect(url_for("producto.listar", id_empresa=id_empresa))
    else:
        if form.is_submitted():
            flash("Por favor corrige los errores en el formulario ❌", "danger")

    return render_template("productos/crear.html", form=form, id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Ver producto (detalle)
# ----------------------------------------------------------------------
@producto_bp.route("/ver/<int:id_empresa>/<string:id_producto>")
@login_required
@verificar_acceso_empresa
def ver(id_empresa, id_producto):
    producto = obtener_producto(id_empresa, id_producto)
    if not producto:
        flash("Producto no encontrado", "danger")
        return redirect(url_for("producto.listar", id_empresa=id_empresa))

    return render_template("productos/ver.html", producto=producto, id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Editar producto
# ----------------------------------------------------------------------
@producto_bp.route("/editar/<int:id_empresa>/<string:id_producto>", methods=["GET", "POST"])
@login_required
@verificar_acceso_empresa
def editar(id_empresa, id_producto):
    producto = obtener_producto(id_empresa, id_producto)
    if not producto:
        flash("Producto no encontrado", "danger")
        return redirect(url_for("producto.listar", id_empresa=id_empresa))

    form = ProductoForm(obj=producto)
    # Deshabilitar el campo ID en edición
    form.id_producto.render_kw = {'readonly': True}

    if form.validate_on_submit():
        exito, error = actualizar_producto(
            producto,
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            stock=form.stock.data
        )
        
        if error:
            flash(error, "danger")
        else:
            flash("Producto actualizado con éxito ✅", "success")
            return redirect(url_for("producto.ver", id_empresa=id_empresa, id_producto=id_producto))

    return render_template("productos/editar.html", form=form, producto=producto, id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Eliminar producto
# ----------------------------------------------------------------------
@producto_bp.route("/eliminar/<int:id_empresa>/<string:id_producto>", methods=["POST"])
@login_required
@verificar_acceso_empresa
def eliminar(id_empresa, id_producto):
    producto = obtener_producto(id_empresa, id_producto)
    if not producto:
        flash("Producto no encontrado", "danger")
    else:
        exito, error = eliminar_producto(producto)
        if error:
            flash(error, "danger")
        else:
            flash(f"Producto '{producto.nombre}' eliminado con éxito ✅", "success")

    return redirect(url_for("producto.listar", id_empresa=id_empresa))

# ----------------------------------------------------------------------
# Ajustar stock
# ----------------------------------------------------------------------
@producto_bp.route("/ajustar_stock/<int:id_empresa>/<string:id_producto>", methods=["GET", "POST"])
@login_required
@verificar_acceso_empresa
def ajustar_stock(id_empresa, id_producto):
    producto = obtener_producto(id_empresa, id_producto)
    if not producto:
        flash("Producto no encontrado", "danger")
        return redirect(url_for("producto.listar", id_empresa=id_empresa))

    if request.method == "POST":
        try:
            nuevo_stock = int(request.form.get("nuevo_stock", 0))
            motivo = request.form.get("motivo", "").strip()
            
            if nuevo_stock < 0:
                flash("El stock no puede ser negativo", "danger")
                return render_template("productos/ajustar_stock.html", producto=producto, id_empresa=id_empresa)
            
            if not motivo:
                flash("Debes especificar un motivo para el ajuste", "danger")
                return render_template("productos/ajustar_stock.html", producto=producto, id_empresa=id_empresa)
            
            # Aquí podrías registrar el movimiento de inventario
            stock_anterior = producto.stock
            producto.stock = nuevo_stock
            
            # Guardar cambios (esto debería estar en el controller)
            from app.models import db
            db.session.commit()
            
            flash(f"Stock ajustado: {stock_anterior} → {nuevo_stock}. Motivo: {motivo} ✅", "success")
            return redirect(url_for("producto.ver", id_empresa=id_empresa, id_producto=id_producto))
            
        except ValueError:
            flash("Stock debe ser un número válido", "danger")
        except Exception as e:
            flash(f"Error al ajustar stock: {str(e)}", "danger")

    return render_template("productos/ajustar_stock.html", producto=producto, id_empresa=id_empresa)

# ----------------------------------------------------------------------
# Productos con stock bajo
# ----------------------------------------------------------------------
@producto_bp.route("/stock_bajo/<int:id_empresa>")
@login_required
@verificar_acceso_empresa
def stock_bajo(id_empresa):
    # Productos con stock menor a 10 (puedes hacer esto configurable)
    limite_stock = request.args.get('limite', 10, type=int)
    productos = listar_productos(id_empresa)
    productos_bajo_stock = [p for p in productos if p.stock <= limite_stock]
    
    return render_template("productos/stock_bajo.html", 
                         productos=productos_bajo_stock, 
                         id_empresa=id_empresa,
                         limite_stock=limite_stock)