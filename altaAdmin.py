#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.models import Usuarios, Grupos
from app import db
import argparse

#Procesar argumentos de entrada
parser = argparse.ArgumentParser(description='%(prog)s es para dar de alta un nuevo usuario administrador.')
parser.add_argument("u", help="Nombre del usuario administrador.")
parser.add_argument("p", help="Password")

args = parser.parse_args()

#Variables globales
usuario = ""
password = ""

# Aquí procesamos lo que se tiene que hacer con cada argumento
if args.u:
    usuario = args.u
if args.p:
	password = args.p

# Inicio del programa
g = Grupos(nombre="administradores")
u = Usuarios(nombre=usuario, administrador=True, grupo="administradores")
u.set_password(password)
db.session.add(g)
db.session.add(u)

try:
	db.session.commit()
	print ("Usuario creado como admin.")
except:
	print ("El usuario ya existe.")

print("[ok]- Terminado mantenimiento.")

