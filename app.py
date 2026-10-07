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
 
    # Generar PIN
    pin = str(secrets.randbelow(1000000)).zfill(6)
 
    # Guardar PIN durante 10 minutos
    pins[correo] = {
        "pin": pin,
        "expira": datetime.now() + timedelta(minutes=10),
        "tipo": tipo
    }
 
    # Crear correo
    mensaje = EmailMessage()
    mensaje["Subject"] = "Código de verificación - Reserva de Sala"
    mensaje["From"] = os.getenv("SMTP_USER")
    mensaje["To"] = correo
 
    mensaje.set_content(
        f"Su código de verificación es: {pin}\n\n"
        "Este código tiene una duración de 10 minutos."
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
 
        return jsonify({
            "valido": False,
            "mensaje": "No se pudo enviar el código de verificación."
        })
 
    return jsonify({
        "valido": True,
        "tipo": tipo,
        "mensaje": "El código de verificación fue enviado a su correo."
    })
 
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)