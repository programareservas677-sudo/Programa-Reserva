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
 
    elif correo.endswith("programareservas677@gmail.com"):
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
            # El PIN ya expiró
            del pins[correo]
 
    # Generar un nuevo PIN
    pin = str(secrets.randbelow(1000000)).zfill(6)
 
    # Guardar PIN durante 5 minutos
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
        "Este código tiene una duración de 5 minutos.\n"
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
 
 
@app.route("/verificar-pin", methods=["POST"])
def verificar_pin():
 
    datos = request.get_json()
 
    correo = datos.get("correo", "").strip().lower()
    pin_ingresado = datos.get("pin", "").strip()
 
    datos_pin = pins.get(correo)
 
    if not datos_pin:
        return jsonify({
            "valido": False,
            "mensaje": "No existe un código pendiente para este correo."
        })
 
    # Comprobar si expiró
    if datetime.now() > datos_pin["expira"]:
 
        del pins[correo]
 
        return jsonify({
            "valido": False,
            "mensaje": "El código ha expirado. Solicite uno nuevo."
        })
 
    # Comprobar PIN
    if pin_ingresado != datos_pin["pin"]:
 
        return jsonify({
            "valido": False,
            "mensaje": "El código ingresado es incorrecto."
        })
 
    # PIN correcto
    del pins[correo]
 
    return jsonify({
        "valido": True,
        "mensaje": "Correo verificado correctamente."
    })
 
 
if __name__ == "__main__":
    app.run(debug=True)
 