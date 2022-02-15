import cv2                      # OpenCV
import numpy as np              # Arrays
from imutils import contours    # Para ordenar contornos
from imutils.perspective import four_point_transform    # Poner la imagen recta
from pyzbar import pyzbar       # Leer código de barras

def reconocer(preguntas,opciones,bondad,imagen,directorioImagenes):
    letra = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    respuestas = ["-"] * preguntas            # Lista donde se almacenan las respuestas
    imagenRuta = directorioImagenes + "/" + imagen
    image = cv2.imread(imagenRuta)                  # Apertura de la imagen
    alto, ancho = image.shape[0:2]                  # Dimensiones
    if ancho < 2480 or alto < 3508:
        return(["ERROR Resolucion"])
    image = cv2.resize(image, (2480, 3500))
    ################################################################################
    # Detectamos el cuadro más grande para establecer la hoja totalmente vertical  #
    ################################################################################
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)	# Convertimos en grises
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]    # Deteccion de bordes
    cnts,hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL  , cv2.CHAIN_APPROX_SIMPLE)       # Contornos
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)          # Ordenamos los contornos por tamaño
    todo_doc = None
    if len(cnts) > 0:
        peri = cv2.arcLength(cnts[0], True)
        approx = cv2.approxPolyDP(cnts[0], 0.02 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        if w > 2000 and h > 3000:
            todo_doc = approx
    if todo_doc is None:
        return(["ERROR No contorno"])
        
    todo_doc[0][0][0] = todo_doc[0][0][0] + 50
    todo_doc[1][0][0] = todo_doc[1][0][0] + 50
    image_corregida = four_point_transform(image, todo_doc.reshape(4, 2))   # Quitamos los margenes (selección del recuadro grande)

    ############################################
    # Detectamos el contorno de las respuestas #
    ############################################
    gray = cv2.cvtColor(image_corregida, cv2.COLOR_BGR2GRAY)	# Convertimos en grises
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]    # Deteccion de bordes
    cnts,hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL  , cv2.CHAIN_APPROX_SIMPLE)       # Contornos
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)          # Ordenamos los contornos por tamaño
    contorno_respuestas = ''
    encontradas_Respuestas = False

    if len(cnts) > 0:
        peri = cv2.arcLength(cnts[0], True)
        approx = cv2.approxPolyDP(cnts[0], 0.02 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        if h > 2000:
            encontradas_Respuestas = True
            contorno_respuestas = approx

    if encontradas_Respuestas == False:
        return(["ERROR No respuestas"])

    image_respuestas = four_point_transform(image_corregida, contorno_respuestas.reshape(4, 2))   # Dejamos solo la parte de las respuestas
        
    #############################
    # Análisis de respuestas    #
    #############################
    gray = cv2.cvtColor(image_respuestas, cv2.COLOR_BGR2GRAY)	                                    # Convertimos en grises
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]                # Deteccion de bordes
        
    filas = 46
    columnas = 30
    def split_image(thresh):
        r = len(thresh) // filas * filas           # Eliminamos pixel sobrantes (para división resto 0)
        c = len(thresh[0]) // columnas * columnas
        thresh = cv2.resize(thresh, (c*2, r*2))     # Cambiamos el tamaño de la imagen al doble y divisible
        rows = np.vsplit(thresh, filas)
        boxes = []
        for row in rows:
            cols = np.hsplit(row, columnas)
            for box in cols:
                boxes.append(box)
        return boxes
    boxes = split_image(thresh)

    #############################################################################
    # Solo se tiene que tener en cuenta las que están pintadas a la mitad.      #
    # Una casilla pintada entera oscila entre 12000 y 13000.                    #
    # Una casilla sin pintar, debido a los bordes, oscila entre 0 y 2900.       #
    # Una pintada oscila entre 7800 - 8767.                                     #
    #############################################################################

    maxB = 8300 + (8300 * int(bondad) / 100)        # Calculo de bondad superior
    mixB = 8300 - (8300 * int(bondad) / 100)        # Cálculo de bondad inferior
    last_Write = 0                                  # Control de dos respuestas marcadas
    pregunta = 0                                    # Número de pregunta por la que va
    for f in range(1, filas):
        if pregunta >= preguntas:
            break
        for c in range(1,columnas):
            # Quitar columnas de números de preguntas
            if (c+(opciones - (opciones-1))) % (opciones+1) == 1:
                break
            pixels = cv2.countNonZero(boxes[(f*columnas)+c])
            if pixels > mixB and pixels < maxB:
                # 1.- Búscamos el número de la pregunta en cuestión
                pregunta = ((c // (opciones + 1))*(filas-1))+f
                if pregunta >= preguntas:
                    break
                # 2.- Búscamos la respuesta seleccionada
                respuesta = "-"
                if (c+(opciones - (opciones-1))) % (opciones+1) == 0:
                    respuesta = letra[opciones-1]
                else:
                    respuesta = letra[(c+(opciones - (opciones-1))) % (opciones+1)-2]
                # Comprueba si ya estaba marcada.
                if last_Write == pregunta:
                    respuesta = "-"                     # Marcar 2 respuestas es como no marcar
                respuestas[pregunta-1] = respuesta      # La pregunta 1 se almacena en index 0
        
    ######################################
    # El id está en un código de barras. #
    ######################################
    cod_barras = pyzbar.decode(image)
    if len(cod_barras) == 0:
        cod_barras = "0"
    else:
        cod_barras = cod_barras[0].data.decode("utf-8")
    
    retorno = []
    retorno.append(cod_barras)
    respuestasString = "".join(respuestas)
    retorno.append(respuestasString)
    return retorno
