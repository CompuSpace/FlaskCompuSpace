from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email

class UsuarioForm(FlaskForm):
    nom_usuario = StringField("Nombre de usuario", validators=[DataRequired(), Length(max=100)])
    contrasena = PasswordField("Contraseña", validators=[DataRequired()])
    correo_recuperacion = StringField("Correo recuperación (opcional)", validators=[Email()])
    rol = SelectField("Rol", choices=[("admin", "Administrador"), ("empleado", "Empleado")], validators=[DataRequired()])
    submit = SubmitField("Registrar Usuario")
