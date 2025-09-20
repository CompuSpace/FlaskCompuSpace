# app/schemas/usuario_schema.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class UsuarioForm(FlaskForm):
    nom_usuario = StringField("Nombre de Usuario", validators=[DataRequired()])
    contrasena = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    correo_recuperacion = StringField("Correo de Recuperación", validators=[Email()])
    rol = SelectField(
        "Rol",
        choices=[("1", "Admin"), ("2", "Empleado")],
        validators=[DataRequired()]
    )
    
    submit = SubmitField("Registrar")
 
