from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json


app = Flask(__name__)

#Configuracion de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)

#Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

#Crear la tabla si no existe
with app.app_context():
    db.create_all()

#Funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
    #obtener todos los registros ed la base de datos
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log = []

#Funcion para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #Guardar el mensaje en la base de datos
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#Token de verificacion para la configuracion
TOKEN_ANDERCODE = "ANDERCODE"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401

def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]

                #Guardar Log en la BD
                agregar_mensajes_log(json.dumps(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                    
                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)

                    #Guardar Log en la BD
                    agregar_mensajes_log(json.dumps(messages))

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})

def enviar_mensajes_whatsapp(texto,number):
    texto = texto.lower()

    if "hola" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, ¿Cómo estás? Bienvenido a \nFondo Complementario Previsional Cerrado de Cesantia de los Servidores Publicos de Carrera de la EPMAPS / Fondo EPMAPS."
            }
        }
    elif "1" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "En el Año 1993 por iniciativa de una funcionaria, un grupo de supervisores de la Empresa Municipal de Alcantarillado y Agua Potable (EMAAP)" 
                "deciden formar un Fondo, en el que el ahorro mensual se convierta en un respaldo económico para su cesantía, la que se constituyó como Asociación de Profesionales."
                "En el año 2004, el Fondo pasa al control de la Superintendencia de Bancos mediante Resolución No. SBS-2004-740 del 16 de septiembre del 2004."
                "Nuestra Razón de existir:"
                "Fomentar el ahorro a largo plazo con los mejores beneficios en pro del bienestar familiar y una cesantía segura."
                "Dónde queremos llegar:"
                "Ser la principal opción financiera con enfoque social para los partícipes, reconocidos por nuestra solidez operativa y económica, manteniendo un crecimiento sostenible en el tiempo."
            }
        }
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "-0.18956183952662675",
                "longitude": "-78.49060506769608",
                "name": "Fondo Complementario Previsional Cerrado de Cesantia de los Servidores Publicos de Carrera de la EPMAPS / Fondo EPMAPS",
                "address": "ITALIA N31-40 VANCOUVER EDIFICIO ARTES MEDICAS 4to piso Oficina b"
            }
        }
    elif "3" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "un asesor se pondra en contacto contigo muy pronto"
            }
        }
    # elif "4" in texto:
    #     data={
    #         "messaging_product": "whatsapp",
    #         "recipient_type": "individual",
    #         "to": number,
    #         "type": "audio",
    #         "audio": {
    #             "link": "https://filesamples.com/samples/audio/mp3/sample1.mp3"
    #         }
    #     }
    # elif "5" in texto:
    #     data = {
    #         "messaging_product": "whatsapp",
    #         "to": number,
    #         "text": {
    #             "preview_url": True,
    #             "body": "Introduccion al curso! https://pazminojativa.com/wp-content/uploads/2023/09/video.mp4"
    #         }
    #     }
    elif "lista" in texto:#6
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Sobre nuestros servicio"
            }
        }
    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "📅 Horario de Atención : Lunes a Viernes. \n🕜 Horario : 8:30 am a 5:00 pm"
            }
        }
    elif "0" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi pagina https://fondocesantiaepmaps.com/ para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información sobre el Fondo de cesantía EPMAPS. ❔\n2️⃣. Ubicación de la EPMAPS. 📍\n3️⃣.Hablar con un asesor. 🙋‍♂️\n4️⃣. Horario de Atención. \n5️⃣. Servicios\n0️⃣. Regresar al Menú. 🕜"
            }

        }
    elif "boton" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type":"button",
                "body": {
                    "text": "¿Confirmas tu registro?"
                },
                "footer": {
                    "text": "Selecciona una de las opciones"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply":{
                                "id":"btnsi",
                                "title":"Si"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btnno",
                                "title":"No"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btntalvez",
                                "title":"Tal Vez"
                            }
                        }
                    ]
                }
            }
        }
    elif "btnsi" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muchas Gracias por Aceptar."
            }
        }
    elif "btnno" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Es una Lastima."
            }
        }
    elif "btntalvez" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Estare a la espera."
            }
        }
    elif "5" in texto:##lista
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Selecciona uno de nuestros servicios"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte con mas información"
                },
                "action":{
                    "button":"Servicios",
                    "sections":[
                        {
                            "title":"Servicios",#Compra y Venta
                            "rows":[
                                {
                                    "id":"btnconvenio",
                                    "title" : "Convenio",
                                    "description": "Compra los mejores articulos de tecnologia"
                                },
                                {
                                    "id":"btncesantia",
                                    "title" : "Cesantía",
                                    "description": "Vende lo que ya no estes usando"
                                },
                                {
                                    "id":"btndescuento",
                                    "title" : "Descuento",
                                    "description": "Vende lo que ya no estes usando"
                                },
                                {
                                    "id":"btncredito",
                                    "title" : "Crédito",
                                    "description": "Vende lo que ya no estes usando"
                                }
                            ]
                        }
                        # ,{
                        #     "title":"Distribución y Entrega",
                        #     "rows":[
                        #         {
                        #             "id":"btndireccion",
                        #             "title" : "Local",
                        #             "description": "Puedes visitar nuestro local."
                        #         },
                        #         {
                        #             "id":"btnentrega",
                        #             "title" : "Entrega",
                        #             "description": "La entrega se realiza todos los dias."
                        #         }
                        #     ]
                        # }
                    ]
                }
            }
        }
    elif "btnconvenio" in texto:
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Selecciona un convenio"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte con mas información"
                },
                "action":{
                    "button":"Servicios",
                    "sections":[
                        {
                            "title":"Servicios",#Compra y Venta
                            "rows":[
                                {
                                    "id":"btnchevrolet",
                                    "title" : "Chevrolet",
                                    "description": "Descuento de 2.5"+"%"+" en la compra de vehículos nuevos de la marca CHEVROLET. El descuento se aplicará sobre el precio de venta al público incluido IVA, de acuerdo con la lista de precios adjunta a este"
                                },
                                {
                                    "id":"btnbyd",
                                    "title" : "BYD",
                                    "description": "Hasta el 10"+"%"+" de descuento en repuestos, accesorios"
                                },
                                {
                                    "id":"btndescuento",
                                    "title" : "Megavision",
                                    #"description": "Vende lo que ya no estes usando"
                                },
                                {
                                    "id":"btncredito",
                                    "title" : "Impacto inmobiliario",
                                    #"description": "Vende lo que ya no estes usando"
                                },
                                {
                                    "id":"btncredito",
                                    "title" : "MAT computer",
                                    #"description": "Vende lo que ya no estes usando"
                                },
                                {
                                    "id":"btncredito",
                                    "title" : "Skybiz travel",
                                    #"description": "Vende lo que ya no estes usando"
                                },
                                {
                                    "id":"btncredito",
                                    "title" : "TopCars",
                                    #"description": "Vende lo que ya no estes usando"
                                },
                                {
                                    "id":"btncredito",
                                    "title" : "Tecnologico Superior Cordillera",
                                    #"description": "Vende lo que ya no estes usando"
                                }
                            ]
                        }                       
                        
                    ]
                }
            }
        }
    elif "btncesantia" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Excelente elección."
            }
        }
    elif "btndescuento" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Excelente elección."
            }
        }
    elif "btncredito" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Excelente elección."
            }
        }
    else:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi pagina https://fondocesantiaepmaps.com/ para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información sobre el Fondo de cesantía EPMAPS. ❔\n2️⃣. Ubicación de la EPMAPS. 📍\n3️⃣.Hablar con un asesor. 🙋‍♂️\n4️⃣. Horario de Atención. \n5️⃣. Servicios\n0️⃣. Regresar al Menú. 🕜"
            }
        }

    #Convertir el diccionaria a formato JSON
    data=json.dumps(data)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAATBEDmeu0sBO9Jwuc8pdBDRkYdii3yAywCsgHiVJnddmrGR9haGkW4TlRmS4l1UnWNkUOEYbG4xDZCyZBuZBvGlSRhI78VRHwiz8S4CDaZBWIJk6EaN6kHxp9FZBljNKGXeyLyLzbuYZB0e7SaFmc7jb1EDG3iZAZB9rifq7Vl9epnvdPOMkUmEZCndH2R7xLjxk5w3wnjIMtKdnbyT1T7Gl2GNhZBlYZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v21.0/529278420272954/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)