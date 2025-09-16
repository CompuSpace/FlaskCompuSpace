from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class EmpresaForm(FlaskForm):
    nit = IntegerField("NIT", validators=[DataRequired()])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    correo_electronico = StringField("Correo empresarial", validators=[DataRequired(), Email()])
    telefono_contacto = StringField("Teléfono", validators=[DataRequired(), Length(max=15)])
    submit = SubmitField("Registrar Empresa")
