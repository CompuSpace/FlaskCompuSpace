from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, BooleanField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from datetime import date

class VentaForm(FlaskForm):
    metodo_pago = SelectField(
        'Método de Pago', 
        validators=[DataRequired(message="Debe seleccionar un método de pago")],
        coerce=str
    )
    
    descuento = FloatField(
        'Descuento (%)',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message="El descuento debe estar entre 0% y 100%")
        ],
        default=0
    )
    
    observaciones = TextAreaField(
        'Observaciones',
        validators=[
            Optional(),
            Length(max=500, message="Las observaciones no pueden exceder 500 caracteres")
        ],
        render_kw={"rows": 3, "placeholder": "Observaciones adicionales (opcional)"}
    )
    
    def validate_descuento(self, field):
        """Validar que el descuento sea razonable"""
        if field.data and field.data < 0:
            raise ValidationError('El descuento no puede ser negativo.')
        if field.data and field.data > 50:  # Máximo 50% de descuento
            raise ValidationError('El descuento no puede ser mayor al 50%.')

class MetodoPagoForm(FlaskForm):
    nombre = StringField(
        'Nombre del Método', 
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=2, max=50, message="El nombre debe tener entre 2 y 50 caracteres")
        ],
        render_kw={"placeholder": "Ej: Efectivo, Tarjeta de Crédito, Transferencia"}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Optional(),
            Length(max=200, message="La descripción no puede exceder 200 caracteres")
        ],
        render_kw={
            "rows": 3,
            "placeholder": "Descripción del método de pago (opcional)"
        }
    )
    
    activo = BooleanField(
        'Activo',
        default=True,
        render_kw={"checked": True}
    )
    
    def validate_nombre(self, field):
        """Validar que el nombre no contenga caracteres especiales problemáticos"""
        caracteres_prohibidos = ['<', '>', '"', "'", '&']
        if any(char in field.data for char in caracteres_prohibidos):
            raise ValidationError('El nombre contiene caracteres no permitidos.')

class FiltroVentasForm(FlaskForm):
    fecha_desde = DateField(
        'Fecha Desde',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    
    fecha_hasta = DateField(
        'Fecha Hasta',
        validators=[Optional()],
        format='%Y-%m-%d',
        default=date.today
    )
    
    metodo_pago = SelectField(
        'Método de Pago',
        validators=[Optional()],
        choices=[('', 'Todos los métodos')],
        coerce=str
    )
    
    usuario = SelectField(
        'Usuario',
        validators=[Optional()],
        choices=[('', 'Todos los usuarios')],
        coerce=str
    )
    
    def validate_fecha_desde(self, field):
        """Validar que fecha desde no sea posterior a fecha hasta"""
        if field.data and self.fecha_hasta.data:
            if field.data > self.fecha_hasta.data:
                raise ValidationError('La fecha desde no puede ser posterior a la fecha hasta.')

class AnularVentaForm(FlaskForm):
    motivo = TextAreaField(
        'Motivo de Anulación',
        validators=[
            DataRequired(message="Debe especificar un motivo"),
            Length(min=10, max=500, message="El motivo debe tener entre 10 y 500 caracteres")
        ],
        render_kw={
            "rows": 4,
            "placeholder": "Explique el motivo por el cual se anula esta venta..."
        }
    )
    
    confirmar = BooleanField(
        'Confirmo que deseo anular esta venta',
        validators=[DataRequired(message="Debe confirmar la anulación")],
        render_kw={"required": True}
    )