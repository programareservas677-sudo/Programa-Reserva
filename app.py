from flask import Flask, render_template, request, jsonify
import secrets
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv
 
load_dotenv()
 
app = Flask(__name__)
 
# PIN temporales
pins = {}
 
 
@app.route("/")
def inicio():
    return render_template("index.html")
 
 
@app.route("/validar-correo", methods=["POST"])
def validar_correo():
    datos = request.get_json()
    correo = datos.get("correo", "").strip().lower()
 
    if correo.endswith("@itcr.ac.cr"):
        tipo = "profesor o administrativo"
 
    elif correo.endswith("@estudiantec.cr"):
        tipo = "estudiante"
 
    else:
        return jsonify({
            "valido": False,
            "mensaje": "Debe utilizar un correo institucional del TEC."
        })
 
    # Comprobar si ya existe un PIN vigente
    pin_existente = pins.get(correo)
 
    if pin_existente:
        if datetime.now() < pin_existente["expira"]:
            segundos_restantes = int(
                (pin_existente["expira"] - datetime.now()).total_seconds()
            )
 
            return jsonify({
                "valido": True,
                "tipo": tipo,
                "nuevo_pin": False,
                "segundos_restantes": segundos_restantes,
                "mensaje": "Ya se envió un código. Debe esperar a que expire antes de solicitar uno nuevo."
            })
 
        else:
            # El PIN ya expiró, así que se puede generar uno nuevo
            del pins[correo]
 
    # Generar un nuevo PIN
    pin = str(secrets.randbelow(1000000)).zfill(6)
 
    # Guardar PIN durante 10 minutos
    pins[correo] = {
        "pin": pin,
        "expira": datetime.now() + timedelta(minutes=5),
        "tipo": tipo
    }
 
    # Crear correo
    mensaje = EmailMessage()
    mensaje["Subject"] = "Código de verificación - Reserva de Sala"
    mensaje["From"] = os.getenv("SMTP_USER")
    mensaje["To"] = correo
 
    mensaje.set_content(
        f"Su código de verificación es: {pin}\n\n"
        "Este código tiene una duración de 10 minutos.\n"
        "No solicite otro código mientras este código esté vigente."
    )
 
    try:
        with smtplib.SMTP(
            os.getenv("SMTP_SERVER"),
            int(os.getenv("SMTP_PORT"))
        ) as servidor:
 
            servidor.starttls()
 
            servidor.login(
                os.getenv("SMTP_USER"),
                os.getenv("SMTP_PASSWORD")
            )
 
            servidor.send_message(mensaje)
 
    except Exception as error:
        print("Error enviando correo:", error)
 
        # Si no se pudo enviar, eliminar el PIN generado
        if correo in pins:
            del pins[correo]
 
        return jsonify({
            "valido": False,
            "mensaje": "No se pudo enviar el código de verificación."
        })
 
    return jsonify({
        "valido": True,
        "tipo": tipo,
        "nuevo_pin": True,
        "segundos_restantes": 300,
        "mensaje": "El código de verificación fue enviado a su correo. Tiene 5 minutos para utilizarlo."
    })