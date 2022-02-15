# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Grupos, Usuarios
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename

class LoginForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="Es necesario un nombre de usuario.")])
    password = PasswordField('Password', validators=[DataRequired(message="Es necesario un password.")])
    submit = SubmitField('Identificarse')
    def validate_nombre(self, nombre):
        user = Usuarios.query.filter_by(nombre=nombre.data).first()
        if user is None:
            raise ValidationError('El nombre de usuario no existe.')
    def validate_password(self, password):
        user = Usuarios.query.filter_by(nombre=self.nombre.data).first()
        if user is None or not user.check_password(password.data):
            raise ValidationError('Password incorrecto.')

class CrearUsuarioForm(FlaskForm):
    nombre = StringField('nombre', validators=[DataRequired(message="Es necesario un nombre de usuario.")])
    password = PasswordField('Password', validators=[DataRequired(message="Es necesario un password.")])
    grupo = SelectField('Grupo', choices=[], validators=[DataRequired(message="Debe pertenecer a un grupo.")])
    administrador = BooleanField('Administrador')
    submit = SubmitField('Dar de alta')

    def validate_nombre(self, nombre):
        user = Usuarios.query.filter_by(nombre=nombre.data).first()
        if user is not None:
            raise ValidationError('El nombre de usuario ya esta escogido.')
    # def validate_password(self, password):
    #     if len(password.data) < 8:
    #         raise ValidationError('La longitud de la contraseña debe ser mayor a 8 caracteres.')
    #     if not any(char.isdigit() for char in password.data):
    #         raise ValidationError('La contraseña debe contener un número.')
    #     if not any(char.isupper() for char in password.data): 
    #         raise ValidationError('La contraseña debe contener una mayúscula.')
    #     if not any(char.islower() for char in password.data):
    #         raise ValidationError('La contraseña debe contener una minúscula.')

class CrearTestForm(FlaskForm):
    iden = HiddenField('identificador')
    titulo = StringField('Titulo', validators=[DataRequired(message="Es necesario seleccionar un test.")])
    preguntas = StringField('Preguntas', validators=[DataRequired(message="Es necesario establecer el número de preguntas")])
    opciones = StringField('Opciones', validators=[DataRequired(message="Es necesario establecer el número de opciones")])
    respuestas = StringField('Respuestas',validators=[DataRequired(message="Es necesario establecer las respuestas correctas")])
    suma = StringField('Suma')
    resta = StringField('Resta')
    bondad = StringField('Bondad')
    submit = SubmitField('Guardar')
    def validate_respuestas(self, respuestas):
        if len(respuestas.data) != int(self.preguntas.data):
            texto = "El número de preguntas("+ self.preguntas.data + ") no se corresponde con las respuestas (" + str(len(respuestas.data)) +")."
            raise ValidationError(texto)

class ArchivosForm(FlaskForm):
    test = HiddenField('test')
    nombre = FileField('Archivo', validators=[FileRequired(message="Es necesario que selecciones un archivo.")])
    submit = SubmitField('Cargar Exámenes')

class CabeceraForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="Es necesario un nombre del grupo.")])
    imagenDerecha = FileField('Imagen a la derecha')
    imagenIzquierda = FileField('Imagen a la izquierda')
    submit = SubmitField('Guardar')