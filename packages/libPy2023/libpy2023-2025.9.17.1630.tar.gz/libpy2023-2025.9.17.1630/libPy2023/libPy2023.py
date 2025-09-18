## -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd
import os
import sys
try:
    from config import USER_EMAIL_GMAIL,USER_PASS_GMAIL,USER_CLB , PASS_CLB
except ImportError:
    USER_EMAIL_GMAIL = None
    USER_PASS_GMAIL = None
    USER_CLB = None
    PASS_CLB = None
    
if os.name=="nt":
    from win32com import client


import keyboard

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import re


def is_file_ready(filepath):
    """Verifica si el archivo está listo para ser usado."""
    try:
        with open(filepath, 'r+'):
            return True
    except IOError:
        return False

def printxy(*args, sep=" ", end="\n", texto=sys.stdout, flush=False, row=None, column=None):
    """
    Print mejorado que mantiene compatibilidad con el estándar,
    pero permite además especificar fila (row) y columna (column).
    
    row    -> Fila (1 = primera línea de la consola)
    column -> Columna (1 = inicio de la línea)
    """
    text = sep.join(str(a) for a in args)

    # Si se especifica fila y columna
    if row is not None and column is not None:
        texto.write(f"\033[{row};{column}H")
    # Si solo se especifica columna (fila actual)
    elif column is not None:
        texto.write(f"\033[{column}G")

    texto.write(text + end)

    if flush:
        texto.flush()

_print = print   # guardamos el original
print = printxy  # sustituimos por el personalizado



#
#def print_there(x:int, y:int, text:str="")->None:
#     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
#     sys.stdout.flush()
#
#def printxy(fila:int=10, columna:int=10, texto:str=""):
#     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (fila, columna, texto))
#     sys.stdout.flush()
#
def ClearCrt():
    """
    ClearCrt : Limp la pantalla de Consola símil a cls o Clear en otros idiomas.
    """
    if os.name in {"ce", "nt", "dos"}:
        os.system ("cls")
    else:
        os.system ("clear")
    return None

def CleanText(xTexto:str):
    """
    CleanText:
        Permite Eliminar caracteres especiales de un texto, como caracteres de control, colores, etc.

    Keyword arguments:
        xTexto: Texto con caracteres especiales o de control.
    return:
        Texto limpio sin caracteres de control.
    """
    # Lista de Códigos Scape y control a buscar y remplazar por nada.
    Secuencias_a_Remplazar_nada=[Color.ForeColor,
       Color.BackColor,
       Color.ForeColor256,
       Color.BackColor256,
       Color.Blanco,
       Color.LBlanco,
       Color.Rojo,
       Color.LRojo,
       Color.Verde,
       Color.LVerde,
       Color.Negro,
       Color.Amarillo,
       Color.LAmarillo,
       Color.Azul,
       Color.LAzul,
       Color.Cyan,
       Color.LCyan,
       Color.Bold,
       Color.Subrayado,
       Color.Invert,
       Color.Fin,
       Color.BRED,
       Color.BBLUE,
       "\x1b[1;36m",
       "\x1b[1;32m",
       "<br>",
       "</br>"]

    #for i in Secuencias_a_Remplazar_nada:
    #    xTexto=xTexto.replace(i,"")
    # Escapa las secuencias para regex y únelas con |
    patron = "|".join(re.escape(str(i)) for i in Secuencias_a_Remplazar_nada if i is not None)
    xTexto = re.sub(patron, "", xTexto)    
    return xTexto

class Color:
    ForeColor256 = "\x1b[38;5;"
    BackColor256 = "\x1b[48;5;"
    ForeColor = "\x1b[38;5;"
    BackColor = "\x1b[48;5;"
    Blanco    = "\x1b[37m"
    LBlanco   = "\x1b[97m"
    Rojo      = "\x1b[31m"
    LRojo     = "\x1b[91m"
    Verde     = "\x1b[32m"
    LVerde    = "\x1b[92m"
    Negro     = "\x1b[30m"
    Amarillo  = "\x1b[33m"
    LAmarillo = "\x1b[93m"
    Azul      = "\x1b[34m"
    LAzul     = "\x1b[94m"
    Bold      = "\x1b[1m"
    Subrayado = "\x1b[4m"
    Invert    = "\x1b[1;31;47m"
    Fin       = "\x1b[0m"
    # Colores en negrita (bold)
    BRojo  = "\x1b[1;31m"
    BVerde = "\x1b[1;32m"
    BAzul  = "\x1b[1;34m"
    #por compatibilidad con versiones anteriores
    BRED   = BRojo
    BGREEN = BVerde
    BBLUE  = BAzul
    Cyan    = "\x1b[36m"
    LCyan   = "\x1b[96m"
    BCyan   = "\x1b[1;36m"
    BCyan   = "\x1b[1;36m"

IsOK  = Color.Azul+"\u2611"+Color.Fin
IsBad = Color.Rojo+"\u2612"+Color.Fin

def cColor(texto:str="", color:str= Color.LAzul) -> str:
    return f"{color}{texto}{Color.Fin}"

def DiaSemana():
    Ahora = datetime.now()
    dias = {
    0: "Domingo",
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado"}
    return dias.get(int(Ahora.strftime("%w")))

_PRUEBA = True if not (DiaSemana() =="Martes" or DiaSemana()=="Lunes" )==-1 else False
_TIPOEJECUCION=cColor("TEST" if _PRUEBA else "PRODUCTIVO",Color.BVerde)

class logs:
    """ logs: Esta clase permite mantener un log de eventos qeu se muestran en pantalla y 
              se graban en un archivo de logs
        logs(NombreArchivo) --> NobreArchivo es el archivo donde se guardara el log.
        log.texto(xTexto)   -->

    """
    def __init__(self,NombreArchivo:str, xlog:bool=True):
        self.FileName=NombreArchivo
        self.ObjetoLogs=""
        self.ObjetoLogs=open(file=self.FileName, mode="w", encoding="utf-8")
        self.xlog = xlog

    def Texto(self, x_texto:str="", clean_string:bool=True)-> str:
        """
        Texto: Escribe texto en pantalla y opcionalmente en el archivo de log.
        
        Args:
            x_texto: Texto a mostrar y escribir
            clean_string: Si True, limpia caracteres especiales antes de escribir al archivo
        """
        print(x_texto, end="")
        if self.xlog:
            # Primero limpia el texto de caracteres especiales
            x_texto=CleanText(x_texto) if clean_string else x_texto 
            self.ObjetoLogs.write(x_texto)

    def fin(self):
        self.ObjetoLogs.close()

    def Fin(self):
        self.ObjetoLogs.close()

class ProgressBar:
    def __init__(self,x,y,Total=None):
        self.x=x
        self.y=y
        self.Inicio=True
        self.Ancho=40
        self.Mensaje=""
        self.Total=100 if Total is None else Total

    def Box(self,Texto=""):
        self.Mensaje=Texto
        self.Ancho=len(CleanText(self.Mensaje))
        print( cColor('╭'+'─'*self.Ancho+'╮',Color.LAzul),row=self.x  ,column=self.y)
        #print_there(row=self.x  ,self.y ,Color.ForeColor+Color.LAzul+'╭'+'─'*self.Ancho+'╮'+Color.Fin)
        print(cColor('│'+cColor(self.Mensaje.center(self.Ancho," "),Color.LAmarillo)+'│',Color.LAzul),row=self.x+1  ,column=self.y )
        #print_there(self.x+1,self.y ,Color.ForeColor+Color.LAzul+'│'+Color.ForeColor+Color.LAmarillo+self.Mensaje.center(self.Ancho," ")+Color.ForeColor+Color.LAzul+'│'+Color.Fin)
        print(cColor('│'+self.Ancho*" "+'│', Color.LAzul) ,row=self.x+2 , column=self.y )
        #print_there(self.x+2,self.y ,Color.ForeColor+Color.LAzul+'│'+Color.ForeColor+Color.LAmarillo+self.Ancho*" "+Color.ForeColor+Color.LAzul+'│'+Color.Fin)
        print(cColor('╰'+'─'*self.Ancho+'╯', Color.LAzul),row=self.x+3  ,column=self.y )
        #print_there(self.x+3,self.y ,Color.ForeColor+Color.LAzul+'╰'+'─'*self.Ancho+'╯'+Color.Fin)

    def Avance(self,Valor=0):
        Valor=round(Valor)
        xDelta=0 if len(self.Mensaje)==0 else 2

        if self.Inicio:
            self.Inicio=False
            print(cColor("├"+"─"*(self.Ancho-6)+"┤",Color.Blanco),row=self.x+2,column=self.y+xDelta)

        if Valor>=0 and Valor<=100:
            avance=round((self.Ancho-6)*Valor/100)
            print( cColor("■"*avance,Color.Verde),row=self.x+xDelta,column=self.y+2)
            print( cColor(Valor,Color.Rojo)+"%",row=self.x+xDelta,column=self.y+round(self.Ancho-3))

    def __str__(self):
        return  f"\n\npos({self.x},{self.y}) | Mensaje: {self.Mensaje} | Ancho: {self.Ancho }"

class Table:
    def __init__(self,xDF,xTipo=0) -> None:
        self.xDataFrame=xDF
        self.xTipo=xTipo
        self.xBox=[["╭","─","┬","╮","│","├","┼","┤","╰","┴","╯"],
                   ["+","-","+","+","|","+","+","+","+","+","+"],
                   ["╔","═","╦","╗","║","╠","╬","╣","╚","╩","╝"]]
        self.xSalida=""
        self.LineaFinal=""

    def Head(self):
        # Reset output each time Head is called to avoid accumulation
        self.xSalida = ""
        Linea1 = Linea2 = Linea3 = Linea4 = ""

        # handle empty dataframe
        if self.xDataFrame is None or len(self.xDataFrame.columns) == 0:
            return ""

        df = self.xDataFrame
        cols = list(df.columns)

        Linea1 = self.xBox[self.xTipo][0]
        Linea2 = self.xBox[self.xTipo][4]
        Linea3 = self.xBox[self.xTipo][5]
        Linea4 = self.xBox[self.xTipo][8]

        for idx, col in enumerate(cols):
            ancho = self.xLargo(df, col)
            Linea1 += ancho * self.xBox[self.xTipo][1]
            Linea2 += str(col).center(ancho, " ")
            Linea3 += ancho * self.xBox[self.xTipo][1]
            Linea4 += ancho * self.xBox[self.xTipo][1]

            last = (idx == len(cols) - 1)
            if last:
                Linea1 += self.xBox[self.xTipo][3] + "\n"
                Linea2 += self.xBox[self.xTipo][4] + "\n"
                Linea3 += self.xBox[self.xTipo][7]
                Linea4 += self.xBox[self.xTipo][10]
            else:
                Linea1 += self.xBox[self.xTipo][2]
                Linea2 += self.xBox[self.xTipo][4]
                Linea3 += self.xBox[self.xTipo][6]
                Linea4 += self.xBox[self.xTipo][9]

        self.xSalida += Linea1 + Linea2 + Linea3
        self.LineaFinal = Linea4
        return self.xSalida

    def xLargo2(self,xDF,xCol):
        # deprecated helper kept for compatibility
        mi_max = len(xCol)
        if xDF is None or len(xDF) == 0:
            return mi_max
        for x in range(len(xDF)):
            try:
                val = xDF.iat[x, xDF.columns.get_loc(xCol)]
            except Exception:
                continue
            if isinstance(val, str):
                mi_max = max(mi_max, len(val))
        return mi_max

    # Borrar xLargo2
    def xLargo(self,xDF,xCol):
        mi_max = len(xCol)
        if xDF is None or len(xDF) == 0:
            return mi_max

        col_idx = xDF.columns.get_loc(xCol)
        for i in range(len(xDF)):
            try:
                val = xDF.iat[i, col_idx]
            except Exception:
                continue
            
            x_mi_largo=0
            if pd.isna(val):
                x_mi_largo = 4
            elif isinstance(val, float) or isinstance(val, int):
                x_mi_largo = len(str(val))
            elif isinstance(val, str):
                x_mi_largo = len(val)
            elif isinstance(val, datetime):
                x_mi_largo = len(val.strftime('%Y-%m-%d'))
            else:
                x_mi_largo = len(str(val))

            if x_mi_largo > mi_max:
                mi_max = xMiLargo

        return mi_max

    def footer(self):
        return self.LineaFinal

    def Body(self):
        #Lista=list(self.xDataFrame.columns)
        #df=self.xDataFrame
        LineaBody=""
        ### Recorre el data frame por Fila
        df = self.xDataFrame
        if df is None or len(df) == 0:
            return ""

        for i in range(len(df)):
            LineaBody += self.xBox[self.xTipo][4]
            for x_idx, col in enumerate(df.columns):
                try:
                    val = df.iat[i, x_idx]
                except Exception:
                    val = ""

                ancho = self.xLargo(df, col)

                # Format value according to its type
                if isinstance(val, (int,)) or str(type(val)).endswith("numpy.int64'>"):
                    s = str(val)
                    fill = max(len(s), len(col))
                    xCadena = s.rjust(fill, " ")
                elif isinstance(val, (bool,)) or str(type(val)).endswith("numpy.bool_'>"):
                    xCadena = str(val).center(ancho, " ")
                else:
                    s = "" if pd.isna(val) else str(val)
                    fill = max(len(s), len(col), ancho)
                    xCadena = s.ljust(fill, " ")[:ancho]

                LineaBody += xCadena
                LineaBody += self.xBox[self.xTipo][4]

            if i < len(df) - 1:
                LineaBody += "\n"
        return LineaBody

    def View(self) -> str:
        Final=self.Head()+"\n"+self.Body()+"\n"+self.footer()
        return Final #self.xSalida

def PrintError(e,connextion=""):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fName = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(f"\n\nError en Linea : {cColor(exc_tb.tb_lineno,Color.BRojo)} en {cColor(fName,Color.BRojo)}")
    print(cColor(exc_type,Color.BRojo))
    print(f"Error Inesperado: {cColor(str(sys.exc_info()[0])+"\n"+\
    str(e)+"\n"+\
    str(EnvironmentError),Color.BRojo)}")
    #print(Color.FAIL+"No se puede conectar a la base de datos"+Color.Fin)
    if not connextion=="":
        connextion.close()

class Cronometro:
    """
    Cronometro: Temporizador
    """
    def __init__(self):
        self.Iniciar=datetime.now()
        self.Actual=0
        self.DeltaTiempo=0
        #self.Ahora=self.Iniciar

    def Delta(self):
        self.Actual=datetime.now()
        self.DeltaTiempo=self.Actual-self.Iniciar
        #return f"{self.DeltaTiempo: %H:%M:%S}"
        return self.DeltaTiempo

    def Reset(self):
        self.Iniciar=datetime.now()

    def Termino(self):
        return f"[ {self.Delta()} ]  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    def now(self):
        return datetime.now()

    def Ahora(self):
        return datetime.now()

    def Inicio(self):
        return f"{self.Iniciar::%d/%m/%y %H:%M:%S}"

    def Año(self):
        return self.Iniciar.year

    def Mes(self):
        return self.Iniciar.month

    def Dia(self):
        return self.Iniciar.day

    def __str__(self):
        #return f"Delta Time {self.Iniciar}"   #=datetime.now()
        return f"{self.Iniciar::%d/%m/%y %H:%M:%S}"

def ImportarHojasXLSX(Ruta,Archivo,Hoja,Encabezados=0,AgregaOrigen=True,Mensajes=False):
    """
    ImportarHojasXLSX: Permite importar Hojas de Calculo en Pandas.\n
        Ruta        : Ruta de Archivo Excel a Importar.
        Archivo     : Excel del que se importara la hoja.
        Hoja        : Hoja de la que se extraeran los datos.
        Encabezados : Fila donde están los encabezados, Cero sin encabezados.
        AgregaOrigen: Agrega dos columnas con información desde donde se obtuvieron los datos.
    \n
                Retorna un DataFrame.
    """
    Ahora=Cronometro()
    if Mensajes:
        print(f"Lectura de Archivo Excel {cColor(Archivo,Color.LAzul)}\nHoja {cColor(Hoja,Color.Azul)}",end="\t- ")
    df = pd.read_excel(Ruta+"/"+Archivo, sheet_name=Hoja,header=Encabezados,engine='openpyxl')
    if AgregaOrigen:
        df['Archivo']=Archivo
        df['Hoja']=Hoja
        if Mensajes:
            print(f"N° Filas Filtradas :{cColor(len(df))}\tDelta: {cColor(Ahora.Delta())}")
    return df

if os.name=="nt":
    def EnviarCorreoAdjunto(destinatario='lcorales', Titulo="@Python - Correos Automáticos", copy=None, mensaje=None, adjunto=None, html=False):
        #### NOTA:
        ####      Recordar que tanto los destinatarios como los en copia se separan con ;
        ####      Este proceso funciona sin problemas para enviar desde Outlook sin pasar credenciales (talvez solo si esta uno logeado)
        olook = client.Dispatch("Outlook.Application")
        mail = olook.CreateItem(0)
        mail.To = destinatario
        mail.Subject = Titulo
        mail.Importance= 2

        if not copy is None:
            mail.CC = copy

        if html:
            if not mensaje is None:
                mail.HTMLBody = mensaje
        else:
            if not mensaje is None:
                mail.Body = mensaje

        if not adjunto is None:
            mail.Attachments.Add(adjunto)

        mail.Send()

def emailSender(xTo ,Asunto="TEST", xBody="Hola Mundo",xServer="Outlook",adjunto=""):
    """
    emailSender : Permite enviar correos con adjuntos si se requiere.
    @parameters :
        xTo     : Destinatario(s), si es mas de uno se debe separar con ';'
        Asunto  : Texto del Asunto o referencia del mensaje.
        xBody   : Texto del cuerpo principal del Mensaje, texto plano o HTML
        xServer : Servicio de correo que se utilizara, ya sea "Outlook" o "gmail"
        adjunto : Archivo en cualquier formato que se enviara como adjunto.
    """
    xTo=xTo.split(";")
    for addr_to in xTo:
        addr_from  = USER_EMAIL_GMAIL  if xServer=="gmail" else USER_CLB
        smtp_server='smtp.gmail.com'   if xServer=="gmail" else 'smtp-mail.outlook.com' 
        #'smtp.office365.com' # #'smtp.office365.com' # # #'smtp-mail.outlook.com'
        
        smtp_port   = 587  #25

        smtp_user   = USER_EMAIL_GMAIL if xServer=="gmail" else USER_CLB
        smtp_pass   = USER_PASS_GMAIL  if xServer=="gmail" else PASS_CLB

        # Construct email
        msg = MIMEMultipart('alternative')
        msg['To'] = addr_to
        msg['From'] = addr_from
        msg['Subject'] = Asunto

        # Record the MIME types of both parts - text/plain and text/html.
        #part1 = MIMEText(text, 'plain')
        part2 = MIMEText(xBody, 'html')
        if not adjunto=="":
            xFile1 = MIMEBase('application', "octet-stream")
    
            xFile1.set_payload(open(adjunto, "rb").read())
            encoders.encode_base64(xFile1)
            xFile=os.path.basename(adjunto)
            xFile1.add_header('Content-Disposition', f"attachment; filename={xFile}")
            msg.attach(xFile1)

        msg.attach(part2)

        # Send the message via an SMTP server
        try:

            s = smtplib.SMTP(host=smtp_server, port=smtp_port)

            # only TLSv1 or higher
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3

            s.ehlo()
            if s.starttls(context=context)[0] != 220:
                return False # cancel if connection is not encrypted
            s.ehlo()
            s.login(smtp_user,smtp_pass)
            s.sendmail(addr_from, addr_to, msg.as_string())
            s.quit()

        except Exception as e:
            print("Error Inesperado: ", sys.exc_info()[0])
            print(e)
            print(EnvironmentError)
            print("ERROR ----> Se produjo un Error al tratar de enviar el correo, cheque, la configuración smtp.")
            ErroresCorreos=1

def Box(Texto=""):
    xAncho=len(CleanText( Texto))
    color_borde=Color.ForeColor256+Color.Azul
    color_texto=Color.ForeColor256+Color.Blanco+Color.Bold
    print(cColor('╭'+'─'*xAncho+'╮',color_borde))
    print(cColor('│',color_borde)+cColor(Texto.center(xAncho," "),color_texto)+cColor('│',color_borde))
    print(cColor('╰'+'─'*xAncho+'╯',color_borde))
    return None

def toVars(xNumero):
    """
    toVars  : Permite crear cadena de sustitución para consultas SQL con %s\n
    xNumero : Cantidad de %s que se crearan.
    """
    xPassVariables="%s,"*xNumero
    xPassVariables=xPassVariables[:-1]
    return xPassVariables

def GenerateQuery(xdf,TABLENAME,Tipo="REPLACE"):
    """
    GenerateQuery() -> Permite Generar la Clausula Query\n
    xdf             -> DataFrame que se usara\n
    Tipo            -> Puede ser Insert o Replace
    """
    Mis_Campos=df2colstr(xdf) # Obtiene un String con las columnas de la Tabla
    xPassVariables=toVars(len(xdf.columns)) # crea la cadena %s de remplazo según la cantidad de campos
    Consulta=f"{Tipo.upper()} INTO {TABLENAME}({Mis_Campos}) VALUES ({xPassVariables});"
    return Consulta

def MessageBox(Texto="Falta el Mensaje", opciones="SN"):
    """
    Requisito previo : pip install keyboard
    MessageBox -> Muestra un mensaje en la pantalla y espera a que se presionen algunas de las 
        teclas indicadas.\n
        Texto    : Mensaje a desplegar\n
        Opciones : las teclas que se espera que presionen
    """
    xTeclas=list(opciones)
    xkey=""
    for xOpcion in xTeclas:

        xkey+=f"{Color.ForeColor256+Color.Rojo} {xOpcion} {Color.Fin} / "
    xkey=xkey[:-2]
    print(f"\n{Color.ForeColor256+Color.Verde}{Texto}{Color.Fin}  {xkey}\n")
    # Espera hasta que se presione unas de las teclas indicado en Opciones, da lo mismo 
    # si es mayúscula o minúscula
    while True:
        tecla=keyboard.read_key().upper()
        if tecla in opciones:
            break
    return tecla