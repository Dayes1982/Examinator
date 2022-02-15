import xlsxwriter
import os


def crear(preguntas,respuestas,titulo,cabecera,PLANTILLA_DIR,imgder,imgizq,GRUPOS_DIR):
    # Columnas posibles (dobles)
    MaxColumnas = 30 # Comienzan en la 3 (blanca). Son dobles 60.
    filas = 45 # Comienzan en la 7, donde van las letras de las respuestas
    letra = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","AA","AB","AC","AD","AE","AF","AG","AH","AI","AJ","AK","AL","AM","AN","AO","AP","AQ","AR","AS","AT","AU","AV","AW","AX","AY","AZ","BA","BB","BC","BD","BE","BF","BG","BH","BI","BJ","BK","BL"]
    respuestaLetra = ["","a","b","c","d","e","f","g","h","i","j"]
    # Las columnas indican las respuestas. Ocupan el número de opciones + 1 del número de preguntas
    columnasPreguntas = ((preguntas - 1)  // filas) +1 # Las necesarias
    numeroMaxPreguntas = filas * (MaxColumnas // (respuestas + 1))
    if preguntas <= numeroMaxPreguntas:
        os.makedirs(PLANTILLA_DIR, exist_ok=True)
        nombre = os.path.join(PLANTILLA_DIR, titulo+'.xlsx')
        workbook  = xlsxwriter.Workbook(nombre)
        worksheet = workbook.add_worksheet()
        # Tamaño filas y columnas
        worksheet.set_column('A:BL', 2.1)
        worksheet.set_column('BM:BN', 0.1)
        for i in range(57):
            worksheet.set_row(i, 28)
        worksheet.set_row(5, 36)
        for i in range(56,64):
            worksheet.set_row(i, 20)
        worksheet.set_row(61, 28)
        worksheet.set_row(62, 28)
        worksheet.set_row(63, 1)

        # Formato para titulos
        formatoTitulo = workbook.add_format()
        formatoTitulo.set_font_size(36)
        formatoTitulo.set_bold()
        formatoTitulo.set_align('center')
        formatoTitulo.set_align('vcenter')
        formatoTitulo.set_left(1)
        formatoTitulo.set_right(1)

        # formato para letras y numeros de preguntas
        formato = workbook.add_format()
        formato.set_font_size(18)
        formato.set_align('center')
        formato.set_align('vcenter')

        # formato texto explica
        formatoExplica = workbook.add_format()
        formatoExplica.set_font_size(14)

        # formato texto ejemplo
        formatoEjemplo = workbook.add_format()
        formatoEjemplo.set_font_size(18)

        # formato casilla de respuesta
        formatCasRespuestaIzq = workbook.add_format()
        formatCasRespuestaIzq.set_bottom(1)
        formatCasRespuestaIzq.set_top(1)
        formatCasRespuestaIzq.set_left(1)
        formatCasRespuestaIzq.set_right(7)
        formatCasRespuestaDer = workbook.add_format()
        formatCasRespuestaDer.set_bottom(1)
        formatCasRespuestaDer.set_top(1)
        formatCasRespuestaDer.set_right(1)

        formatCasRespuestaIzqLlena = workbook.add_format()
        formatCasRespuestaIzqLlena.set_bottom(1)
        formatCasRespuestaIzqLlena.set_top(1)
        formatCasRespuestaIzqLlena.set_left(1)
        formatCasRespuestaIzqLlena.set_right(7)
        formatCasRespuestaDerLlena = workbook.add_format()
        formatCasRespuestaDerLlena.set_bottom(1)
        formatCasRespuestaDerLlena.set_top(1)
        formatCasRespuestaDerLlena.set_right(1)
        formatCasRespuestaDerLlena.set_bg_color('black')
        formatCasRespuestaIzqLlena.set_bg_color('black')

        # Linea superior
        formatLinSup = workbook.add_format()
        formatLinSup.set_top(1)
        formatLinSup.set_left(1)
        formatLinSup.set_right(1)

        # Solo lados finos
        formatLinLat = workbook.add_format()
        formatLinLat.set_left(1)
        formatLinLat.set_right(1)

        # lados finos abajo gordo
        formatLinGorButt = workbook.add_format()
        formatLinGorButt.set_left(1)
        formatLinGorButt.set_right(1)
        formatLinGorButt.set_bottom(5)

        # Gordo Grande Izquierda
        formatGordoIzq = workbook.add_format()
        formatGordoIzq.set_left(5)

        # Gordo Grande Abajo
        formatGordoAba = workbook.add_format()
        formatGordoAba.set_bottom(5)

        # Gordo Grande Arriba
        formatGordoArri = workbook.add_format()
        formatGordoArri.set_top(5)

        # Esquinas gordas
        formatEsquinas = workbook.add_format()
        formatEsquinas.set_bottom(5)
        formatEsquinas.set_left(5)

        # Para marco de respuestas
        formatMarcoSup = workbook.add_format()
        formatMarcoSup.set_top(2)
        formatMarcoInf = workbook.add_format()
        formatMarcoInf.set_top(5)
        formatMarcoInf.set_bottom(2)
        formatMarcoIzq = workbook.add_format()
        formatMarcoIzq.set_left(2)
        formatMarcoDer = workbook.add_format()
        formatMarcoDer.set_right(2)

        # dibujamos lineas laterales grodas
        for x in range(6,64):
            worksheet.write("A" + str(x), "", formatGordoIzq)
            worksheet.write("BM" + str(x), "", formatGordoIzq)
        for x in range(57,64):
            worksheet.write("AF" + str(x), "", formatGordoIzq)
        # lineas horizontales abajo gordas
        for x in range(0,64):
            worksheet.write(letra[x] + "56", "", formatGordoAba)
            worksheet.write(letra[x] + "63", "", formatGordoAba)

        #Esquinas
        worksheet.write("A56", "", formatEsquinas)
        worksheet.write("A63", "", formatEsquinas)
        worksheet.write("AF63", "", formatEsquinas)

        #Marco de preguntas
        for x in range(2,62):
            worksheet.write(letra[x] + "6", "", formatMarcoInf)
            worksheet.write(letra[x] + "53", "", formatMarcoSup)
        for x in range(7,53):
            worksheet.write("B" + str(x), "", formatMarcoDer)
            worksheet.write("BK" + str(x), "", formatMarcoIzq)



        # Escribimos y unimos
        worksheet.merge_range('A1:BL1',"",formatLinSup)
        worksheet.merge_range('A2:BL2', cabecera,formatoTitulo)
        worksheet.merge_range('A3:BL3',"",formatLinLat)
        worksheet.merge_range('A4:BL4', titulo,formatoTitulo)
        worksheet.merge_range('A5:BL5',"",formatLinGorButt)
        # Imagenes
        if imgder is not None:
            worksheet.insert_image('BF1', GRUPOS_DIR + "/" + imgder, {'x_offset': 15, 'y_offset': 10})
        if imgizq is not None:
            worksheet.insert_image('A1', GRUPOS_DIR + "/" + imgizq, {'x_offset': 15, 'y_offset': 10})
        
        
        
        # Preguntas y respuestas (comenzamos en C7)
        # "columnasPreguntas" contiene el total de columnas de "respuestas + 1 (número pregunta)"
        columnasRellanar = (columnasPreguntas * (respuestas + 1)) * 2 # SON DOBLES
        col = 0   # Columna de respuesta
        fil = 8   # fila
        p = 1     # pregunta
        for i in range(2,columnasRellanar+1,2):
            # Encabezado (respuestas)
            selCasillas = letra[i] + "7:" + letra[i+1] + "7"
            worksheet.merge_range(selCasillas, respuestaLetra[col],formato)
            # Números de preguntas
            if col==0:
                # Casillas de número de pregunta
                for x in range(1,filas+1):
                    sel2Casillas = letra[i] + str(fil) + ":" + letra[i+1] + str(fil)
                    if p <= preguntas:
                        if col==0:
                            worksheet.merge_range(sel2Casillas, str(p), formato)
                        
                    fil = fil + 1
                    p = p + 1
                fil = 8
            else:
                # Casillas de respuesta
                p = p - filas
                for x in range(1,filas+1):
                    if p <= preguntas:
                        worksheet.write(letra[i] + str(fil), "", formatCasRespuestaIzq)
                        worksheet.write(letra[i+1] + str(fil), "", formatCasRespuestaDer)
                    fil = fil + 1
                    p = p + 1
                fil = 8
            col=col+1
            if col > respuestas:
                col=0
        # Explicaciones
        worksheet.write("B57", "Rellene una de las dos mitades para seleccionar la opción.", formatoExplica)
        worksheet.write("B58", "Para anular, rellene las dos mitades.", formatoExplica)
        worksheet.write("B59", "Procure rellenar sin salirse del recuadro.", formatoExplica)
        worksheet.write("B60", "Utilice rotulador o boligrafo negro.", formatoExplica)
        worksheet.write("M62", "Ejemplo:", formatoEjemplo)
        worksheet.write("AB62", "1-a", formatoEjemplo)
        worksheet.write("AB63", "2-c", formatoEjemplo)
        worksheet.merge_range("R61:S61", "", formato)
        worksheet.merge_range("T61:U61", "a", formato)
        worksheet.merge_range("V61:W61", "b", formato)
        worksheet.merge_range("X61:Y61", "c", formato)
        worksheet.merge_range("R62:S62", "1", formato)
        worksheet.merge_range("R63:S63", "2", formato)
        worksheet.write("T63", "", formatCasRespuestaIzq)
        worksheet.write("X62", "", formatCasRespuestaIzq)
        worksheet.write("X63", "", formatCasRespuestaIzq)
        worksheet.write("U62", "", formatCasRespuestaDer)
        worksheet.write("U63", "", formatCasRespuestaDer)
        worksheet.write("W63", "", formatCasRespuestaDer)
        worksheet.write("Y62", "", formatCasRespuestaDer)
        worksheet.write("T62", "", formatCasRespuestaIzqLlena)
        worksheet.write("V62", "", formatCasRespuestaIzqLlena)
        worksheet.write("W62", "", formatCasRespuestaDerLlena)
        worksheet.write("Y63", "", formatCasRespuestaDerLlena)

        for x in range(0,64):
            worksheet.write(letra[x] + "64", "", formatGordoArri)

        worksheet.set_margins(left=0.55, right=0.47, top=0.59, bottom=0.59)
        worksheet.set_print_scale(47)
        worksheet.set_header('', {'margin': 0.00})
        worksheet.set_footer('', {'margin': 0.00})
        worksheet.set_paper(9)
        #worksheet.set_header('&L&G', {'image_left': 'logo.jpg'})
        worksheet.protect()
        workbook.close()

        return("ok")
    else:
        #print("[Error] Reduzca el número de preguntas u opciones de respuesta")
        return("Reduzca el número de preguntas u opciones de respuestas")