from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from app.models import Producto

class ProductoForm(FlaskForm):
    id_producto = StringField(
        'ID del Producto', 
        validators=[
            DataRequired(message="El ID del producto es obligatorio"),
            Length(min=1, max=100, message="El ID debe tener entre 1 y 100 caracteres")
        ],
        render_kw={"placeholder": "Ej: PROD001, SKU123, etc."}
    )
    
    nombre = StringField(
        'Nombre del Producto', 
        validators=[
            DataRequired(message="El nombre del producto es obligatorio"),
            Length(min=2, max=100, message="El nombre debe tener entre 2 y 100 caracteres")
        ],
        render_kw={"placeholder": "Nombre del producto"}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Length(max=255, message="La descripción no puede exceder 255 caracteres")
        ],
        render_kw={
            "placeholder": "Descripción opcional del producto",
            "rows": 3
        }
    )
    
    precio = IntegerField(
        'Precio',
        validators=[
            DataRequired(message="El precio es obligatorio"),
            NumberRange(min=0, message="El precio no puede ser negativo")
        ],
        render_kw={"placeholder": "Precio en pesos"}
    )
    
    stock = IntegerField(
        'Stock Inicial',
        validators=[
            DataRequired(message="El stock es obligatorio"),
            NumberRange(min=0, message="El stock no puede ser negativo")
        ],
        render_kw={"placeholder": "Cantidad en inventario"}
    )
    
    def validate_id_producto(self, field):
        """Validar que el ID del producto sea único en la empresa"""
        # Esta validación se ejecuta solo al crear, no al editar
        if hasattr(self, '_empresa_id') and hasattr(self, '_is_edit') and not self._is_edit:
            existing = Producto.query.filter_by(
                id_producto=field.data, 
                id_empresa=self._empresa_id
            ).first()
            if existing:
                raise ValidationError('Ya existe un producto con este ID en tu empresa.')
    
    def validate_precio(self, field):
        """Validar que el precio sea razonable"""
        if field.data and field.data > 999999999:  # 999 millones
            raise ValidationError('El precio es demasiado alto.')
    
    def validate_stock(self, field):
        """Validar que el stock sea razonable"""
        if field.data and field.data > 999999:  # 999 mil
            raise ValidationError('El stock es demasiado alto.')

# Formulario simplificado para ajuste de stock
class AjusteStockForm(FlaskForm):
    nuevo_stock = IntegerField(
        'Nuevo Stock',
        validators=[
            DataRequired(message="El nuevo stock es obligatorio"),
            NumberRange(min=0, message="El stock no puede ser negativo")
        ]
    )
    
    motivo = StringField(
        'Motivo del Ajuste',
        validators=[
            DataRequired(message="Debes especificar un motivo"),
            Length(min=5, max=255, message="El motivo debe tener entre 5 y 255 caracteres")
        ],
        render_kw={"placeholder": "Ej: Inventario físico, producto dañado, etc."}
    )