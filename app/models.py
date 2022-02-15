from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
	return Usuarios.query.get(int(id))

class Usuarios(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(64), index=True, unique=True,nullable=False)
	password = db.Column(db.String(128),nullable=False)
	administrador = db.Column(db.Boolean,nullable=False)
	grupo = db.Column(db.Integer, db.ForeignKey('grupos.id'))
	def set_password(self, contra):
		self.password = generate_password_hash(contra)
	def check_password(self, contra):
		return check_password_hash(self.password, contra)
	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	@property
	def is_admin(self):
		if self.administrador == True:
			return True
		else:
			return False
	def __repr__(self):
		return '<Usuario {}>'.format(self.nombre)

class Grupos(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(50), nullable=False)
	imagenDerecha = db.Column(db.String(50))
	imagenIzquierda = db.Column(db.String(50))
	def __repr__(self):
		return '<Grupo %r>' % self.nombre

class Test(db.Model):
	id = db.Column(db.Integer,primary_key=True, unique=True, nullable=False)
	titulo = db.Column(db.String(50), nullable=False)
	grupo = db.Column(db.Integer, db.ForeignKey('grupos.id'))
	preguntas = db.Column(db.Integer, nullable=False)
	opciones = db.Column(db.Integer, nullable=False)
	respuestas = db.Column(db.String(400), nullable=False)
	sumaA = db.Column(db.Float, nullable=False)
	restaF = db.Column(db.Float, nullable=False)
	bondad = db.Column(db.Integer, nullable=False)
	
class Examenes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	test = db.Column(db.Integer, db.ForeignKey('test.id'))
	archivo = db.Column(db.String(80), nullable=False)
	idSujeto = db.Column(db.String(50), nullable=False)
	respuestas = db.Column(db.String(400), nullable=False)
	nota = db.Column(db.Float)
	