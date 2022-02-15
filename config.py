import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	#Para los formularios
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	#para el envio de tokens en los email
	SECURITY_PASSWORD_SALT = 'you-will-never-admin'
	# Debug
	DEBUG = True
	#Para la BBDD
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'examenes.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
