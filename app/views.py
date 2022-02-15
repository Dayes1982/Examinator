# -*- coding: utf-8 -*-
import os
from PIL import Image
from flask import flash,render_template, redirect, url_for, request, json, jsonify
from flask.helpers import send_file
from app import app, crearplantilla, db, admin, reconocimiento
from .forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Usuarios, Grupos, Test, Examenes
from app.forms import CrearTestForm, CrearUsuarioForm, ArchivosForm, CabeceraForm
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin import expose

# Manejo de archivos
EXAMENES_DIR = os.path.join(os.path.dirname(__file__), 'static/examenes')
PLANTILLAS_DIR = os.path.join(os.path.dirname(__file__), 'static/plantillas')
GRUPOS_DIR = os.path.join(os.path.dirname(__file__), 'static/cabezas')

########## Personalización de la vista de administrador #################
class UsuariosView(ModelView):
    can_export = True
    can_create = True
    can_edit = False
    column_list = ('nombre','grupo','administrador')
    column_searchable_list = ['nombre','grupo']
    column_exclude_list = ['password']
    def is_accessible(self):
        return current_user.administrador
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = CrearUsuarioForm()
        form.grupo.choices = [(g.nombre) for g in Grupos.query.order_by(Grupos.nombre.asc())]
        if form.validate_on_submit():
            u = Usuarios(nombre=form.nombre.data,grupo=form.grupo.data,administrador=form.administrador.data)
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            app.logger.info('%s da de alta al usuario %s', current_user.nombre,form.nombre.data)
            return self.render('admin/templates/create_user.html',form=form, mensaje="Usuario: " + form.nombre.data + " añadido.")
        return self.render('admin/templates/create_user.html',form=form)

class GruposView(ModelView):
    page_size = 50
    can_edit = False
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = CabeceraForm()
        if form.validate_on_submit():
            grupo = Grupos(nombre=form.nombre.data)
            fileDer = request.files['imagenDerecha']
            grupo.imagenDerecha = secure_filename(fileDer.filename)
            fileIzq = request.files['imagenIzquierda']
            grupo.imagenIzquierda = secure_filename(fileIzq.filename)
            db.session.add(grupo)
            db.session.commit()
            os.makedirs(GRUPOS_DIR, exist_ok=True)
            file_path = os.path.join(GRUPOS_DIR, grupo.imagenDerecha)
            fileDer.save(file_path)
            #Tamaño
            image = Image.open(file_path)
            image = image.resize((100, 150))
            image.save(file_path)
            file_path = os.path.join(GRUPOS_DIR, grupo.imagenIzquierda)
            fileIzq.save(file_path)
            image = Image.open(file_path)
            image = image.resize((100, 150))
            image.save(file_path)
            app.logger.info('%s ha creado el grupo %s', current_user.nombre,grupo.nombre)
            return self.render('admin/templates/create_grupos.html',form=form, mensaje="Grupo dado de alta correctamente.")
        return self.render('admin/templates/create_grupos.html',form=form)
    def delete_model(self, model):
        try:
            self.on_model_delete(model)
            os.remove(os.path.join(GRUPOS_DIR, model.imagenDerecha))
            os.remove(os.path.join(GRUPOS_DIR, model.imagenIzquierda))
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
        except Exception:
            self.session.rollback()
            return False
        else:
            self.after_model_delete(model)
        return True

class TestView(ModelView):
    column_list = ('titulo', 'grupo','preguntas','opciones','respuestas','sumaA','restaF')
    can_create = False
        
class ExamenView(ModelView):
    can_edit = False
    column_searchable_list = ['idSujeto','test']

admin.add_view(UsuariosView(Usuarios, db.session))
admin.add_view(GruposView(Grupos, db.session))
admin.add_view(TestView(Test, db.session))
admin.add_view(ExamenView(Examenes, db.session))
admin.add_link(MenuLink(name='Salir Administración', url='/'))


######## VISTAS ##############

@app.route('/') 
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(nombre=form.nombre.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            app.logger.info('Ha accedido %s', user.nombre)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    app.logger.info('%s cierra sesion', current_user.nombre)
    logout_user()
    return redirect(url_for('login'))

@app.route('/menu', methods=['POST', 'GET'])
@login_required
def menu():
    g = Usuarios.query.filter_by(nombre=current_user.nombre).first()
    testGrupo = Test.query.filter_by(grupo=g.grupo).all()
    return render_template("menu.html", title='Pagína principal',test=testGrupo)

@app.route('/newtest', methods=['POST', 'GET'])
@login_required
def newtest():
    form = CrearTestForm()
    if form.validate_on_submit():
        g = Usuarios.query.filter_by(nombre=current_user.nombre).first()
        print("El usuario pertenece al grupo de: ",g.grupo)
        test = Test(titulo=form.titulo.data,grupo=g.grupo,preguntas=form.preguntas.data,opciones=form.opciones.data,respuestas=form.respuestas.data,sumaA=form.suma.data,restaF=form.resta.data,bondad=form.bondad.data)
        db.session.add(test)
        db.session.commit()
        flash('Test creado!!!')
        app.logger.info('%s añade test %s al grupo %s', current_user.nombre,form.titulo.data,g.grupo)
        testGrupo = Test.query.filter_by(grupo=g.grupo).all()
        return render_template("menu.html", title='Pagína principal',test=testGrupo)
    return render_template("edittest.html", title='Creación de test',form=form,tipo="Creación de test")
    
@app.route('/edittest', methods=['POST', 'GET'])
@login_required
def edittest():
    form = CrearTestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            te = Test.query.filter_by(id=form.iden.data).first()
            te.titulo = form.titulo.data
            te.preguntas = form.preguntas.data
            te.opciones = form.opciones.data
            # Si cambian respuestas, suma, resta tb notas !!!!
            if te.respuestas != form.respuestas.data or te.sumaA != form.suma.data or te.restaD != form.resta.data:
                te.respuestas = form.respuestas.data
                te.sumaA = form.suma.data
                te.restaF = form.resta.data
                # Recalcular nota
                examenes = Examenes.query.filter_by(test=form.iden.data).all() # Obtener todos examenes del test
                for e in examenes:
                    nota = 0
                    for n in range(0,int(te.preguntas)):
                        if te.respuestas[n] == e.respuestas[n]:
                            nota = nota + float(te.sumaA)
                        elif e.respuestas[n] == "-":
                            pass
                        else:
                            nota = nota - float(te.restaF)
                    e.nota = nota
                    db.session.add(e)
                    db.session.commit()
                flash('Recalculada nota de todos los exámenes.')
            # Si cambia bondad, corregimos de nuevo??
            te.bondad = form.bondad.data
            db.session.commit()
            flash('Test modificado.')
            return redirect('menu')
    else:
        t = request.args.get('id', default = 0, type = int)
        if t != 0:
            te = Test.query.filter_by(id=t).first()
            form.iden.data = t
            form.titulo.data = te.titulo
            form.preguntas.data = te.preguntas
            form.opciones.data = te.opciones
            form.respuestas.data = te.respuestas
            form.suma.data = te.sumaA
            form.resta.data = te.restaF
            form.bondad.data = te.bondad
            return render_template("edittest.html", title='Edición de test',form=form,tipo="Edición de test")
    return redirect(url_for('menu'))

# Eliminación de Test. !!!También borra los examenes asociados!!!
@app.route('/deltest', methods=['POST', 'GET'])
@login_required
def deltest():
    t = request.form.get('id', default = 0, type = int)
    if t != 0:
        # Eliminar los examenes y carpeta de examenes
        examenes = Examenes.query.filter_by(test=t).all()
        for exa in examenes:
            eliminarExamen(exa.id)
        EXAMENTEST_DIR = os.path.join(os.path.dirname(__file__), 'static/examenes/'+str(t)+'/')
        pat = os.path.join(EXAMENTEST_DIR, 'resultados.xml')
        if os.path.exists(pat) == True:
            os.remove(pat)
        if os.path.exists(os.path.join(os.path.dirname(__file__), 'static/examenes/'+str(t))) == True:
            os.rmdir(os.path.join(os.path.dirname(__file__), 'static/examenes/'+str(t)))
        # Elimina el test
        Test.query.filter_by(id=t).delete()
        db.session.commit()
        flash('Test eliminado!!!')
    return redirect(url_for('menu'))

@app.route('/downloadP', methods=['POST', 'GET'])
@login_required
def downloadP():
    t = request.form.get('id', default = 0, type = int)
    if t != 0:
        te = Test.query.filter_by(id=t).first()
        u = Usuarios.query.filter_by(nombre=current_user.nombre).first()
        g = Grupos.query.filter_by(nombre=u.grupo).first()
        sms = crearplantilla.crear(te.preguntas,te.opciones,te.titulo,"Guardia Civil",PLANTILLAS_DIR,g.imagenDerecha,g.imagenIzquierda,GRUPOS_DIR)
        if sms == 'ok':
            nombre = te.titulo+'.xlsx'
            app.logger.info('El usuario %s descarga %s', current_user.nombre,nombre)
            file_path = os.path.join(PLANTILLAS_DIR, nombre)
            return send_file(file_path)
        else:
            flash(sms)
    return redirect(url_for('menu'))

@app.route('/examenes', methods=['POST', 'GET'])
@login_required
def examenes():
    form = ArchivosForm()
    if request.method == 'POST':
        t = form.test.data
        uploaded_files = request.files.getlist("file[]")
        for file in uploaded_files:
            if file.filename != "":
                # Subimos el archivo
                os.makedirs(EXAMENES_DIR, exist_ok=True)
                EXAMENTEST_DIR = os.path.join(os.path.dirname(__file__), 'static/examenes/'+t)
                os.makedirs(EXAMENTEST_DIR, exist_ok=True)
                file.save(os.path.join(EXAMENES_DIR, t+'/'+file.filename))
                # OPENCV
                test = Test.query.filter_by(id=t).first()
                idRespu = reconocimiento.reconocer(test.preguntas,test.opciones,test.bondad,t+'/'+file.filename,EXAMENES_DIR)
                if idRespu[0] == "ERROR Resolucion":
                    print("La imagen no tiene la resolución suficiente")
                elif idRespu[0] == "ERROR No contorno":
                    print("La imagen no se puede analizar, no se detectan contornos.")
                elif idRespu[0] == "ERROR No respuestas":
                    print("La imagen no se puede analizar, no se detectan respuestas.")
                else:
                    # Solo falta la nota
                    nota = 0

                    for n in range(0,test.preguntas):
                        if test.respuestas[n] == idRespu[1][n]:
                            nota = nota + test.sumaA
                        elif idRespu[1][n] == "-":
                            pass
                        else:
                            nota = nota - test.restaF
                    # Tenemos todo. Guardamos.
                    e = Examenes(test=t,archivo=file.filename,idSujeto=idRespu[0],respuestas=idRespu[1],nota=nota)
                    db.session.add(e)
                    db.session.commit()
                    flash('Examen '+file.filename+' guardado.')
                    app.logger.info('%s añade examen %s al test %s', current_user.nombre,file.filename,test.titulo)

        exa = Examenes.query.filter_by(test=t).all()    #Obtenemos examenes del test
        return render_template("exam.html", title='Emamenes', examenes=exa, form=form,testid=t)
    else:
        t = request.args.get('idtest', default = 0, type = int)
        if t != 0:
            # Comprueba permisos
            g = Usuarios.query.filter_by(nombre=current_user.nombre).first() # Grupo del user
            test = Test.query.filter_by(id=t).first() # Grupo del test
            if test is not None and g.grupo == test.grupo:
                exa = Examenes.query.filter_by(test=t).all() #Obtenemos examenes del test
                form.test.data = t
                return render_template("exam.html", title='Emamenes', examenes=exa, form=form,testid=t)
            else:
                app.logger.info('[SEGURIDAD] El usuario %s intenta acceder a los examenes de %s', current_user.nombre,t)
                return render_template("exam.html", title='Emamenes',nopermiso="no",form=form,testid=t)

@app.route('/delexam', methods=['POST', 'GET'])
@login_required
def delexam():
    t = request.form.get('id', default = 0, type = int)
    if t != 0:
        exam = Examenes.query.filter_by(id=t).first()
        eliminarExamen(t)
        flash('Examen eliminado!!!')
        exa = Examenes.query.filter_by(test=exam.test).all() #Obtenemos examenes del test
        form = ArchivosForm()
        form.test.data = t
        return render_template("exam.html", title='Emamenes', examenes=exa, form=form,testid=t)
        
@app.route('/downexam', methods=['POST', 'GET'])
@login_required
def downexam():
    t = request.form.get('id', default = 0, type = int)
    if t != 0:
        exam = Examenes.query.filter_by(id=t).first()
        EXAMENTEST_DIR = os.path.join(os.path.dirname(__file__), 'static/examenes/'+str(exam.test))
        app.logger.info('El usuario %s descarga %s', current_user.nombre,exam.archivo)
        file_path = os.path.join(EXAMENES_DIR, str(exam.test)+'/'+exam.archivo)
        return send_file(file_path)
    return redirect(url_for('examenes'))

# Genera xml de todos los examenes de un test y lo descarga
@app.route('/downexamenes', methods=['POST', 'GET'])
@login_required
def downexamenes():
    t = request.form.get('id', default = 0, type = int)
    if t != 0:
        letra = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        exam = Examenes.query.filter_by(id=t).first()
        dirSalida = os.path.join(os.path.dirname(__file__), 'static/examenes/'+str(t))
        f = open(dirSalida + "/resultados.xml","w")
        f.write("<sujetos>\n")
        exa = Examenes.query.filter_by(test=t).all() #Obtenemos examenes del test
        for e in exa:
            f.write("<sujeto idSujeto='" + e.idSujeto + "' nombre='0' edad='0' sexo='9' respuestas='")
            for r in range(0,len(e.respuestas)):
                if e.respuestas[r] == "-":
                    f.write("0")
                else:
                    f.write(str(letra.index(e.respuestas[r])+1))
            f.write("' />\n")
        f.write("</sujetos>\n")
        f.close()
        # Lo descargamos
        EXAMENTEST_DIR = os.path.join(os.path.dirname(__file__), 'static/examenes/'+str(t)+'/')
        file_path = os.path.join(EXAMENTEST_DIR, 'resultados.xml')
        return send_file(file_path)
    return redirect(url_for('examenes'))

def eliminarExamen(t):
    # Eliminamos el archivo
    EXAMENTEST_DIR = os.path.join(os.path.dirname(__file__), 'static/examenes/'+str(t))
    print("Eliminando test: ",str(t))
    exam = Examenes.query.filter_by(id=t).first()
    os.remove(os.path.join(EXAMENES_DIR, str(exam.test)+'/'+exam.archivo))
    # Eliminamos de la BBDD
    Examenes.query.filter_by(id=t).delete()
    db.session.commit()
