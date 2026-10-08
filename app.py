from flask import Flask, render_template, request, jsonify, session
import secrets
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
 
load_dotenv()
 
app = Flask(__name__)
app.secret_key = "clave-reservas-tec"
 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
 
db = SQLAlchemy(app)
 
pins = {}
 
 
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fin = db.Column(db.String(5), nullable=False)
    descripcion = db.Column(db.String(300), nullable=False)
 
 
with app.app_context():
    db.create_all()
 
 
@app.route("/")
def inicio():
    return render_template("index.html")
 
 
@app.route("/validar-correo", methods=["POST"])
def validar_correo():
 
    datos = request.get_json()
    correo = datos.get("correo", "").strip().lower()
 
    if correo == "programareservas677@gmail.com":
        tipo = "administrador"
    elif correo.endswith("@itcr.ac.cr"):
        tipo = "profesor o administrativo"
    elif correo.endswith("@estudiantec.cr"):
        tipo = "estudiante"
    else:
        return jsonify({
            "valido": False,
            "mensaje": "No se puede ingresar. Debe utilizar un correo institucional del TEC."
        })
 
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
 
        del pins[correo]
 
    pin = str(secrets.randbelow(1000000)).zfill(6)
 
    pins[correo] = {
        "pin": pin,
        "expira": datetime.now() + timedelta(minutes=5),
        "tipo": tipo
    }
 
    mensaje = EmailMessage()
 
    mensaje["Subject"] = "Código de verificación - Reserva de Sala"
    mensaje["From"] = os.getenv("SMTP_USER")
    mensaje["To"] = correo
 
    mensaje.set_content(
        f"Su código de verificación es: {pin}\n\n"
        "Este código tiene una duración de 5 minutos.\n\n"
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
 
    if datetime.now() > datos_pin["expira"]:
 
        del pins[correo]
 
        return jsonify({
            "valido": False,
            "mensaje": "El código ha expirado. Solicite uno nuevo."
        })
 
    if pin_ingresado != datos_pin["pin"]:
        return jsonify({
            "valido": False,
            "mensaje": "El código ingresado es incorrecto."
        })
 
    tipo = datos_pin["tipo"]
 
    del pins[correo]
 
    session["correo"] = correo
    session["tipo"] = tipo
    session["verificado"] = True
 
    return jsonify({
        "valido": True,
        "tipo": tipo,
        "mensaje": "Correo verificado correctamente."
    })
 
 
@app.route("/verificar")
def pagina_verificacion():
    return render_template("verificar.html")
 
 
@app.route("/calendario")
def calendario():
 
    if not session.get("verificado"):
        return jsonify({
            "error": "Debe verificar su correo antes de ingresar."
        }), 401
 
    return render_template("calendario.html")
 
 
@app.route("/reservas", methods=["GET"])
def obtener_reservas():
 
    if not session.get("verificado"):
        return jsonify({
            "error": "No autorizado."
        }), 401
 
    reservas = Reserva.query.all()
 
    resultado = []
 
    for reserva in reservas:
 
        resultado.append({
            "id": reserva.id,
            "fecha": reserva.fecha.isoformat(),
            "hora_inicio": reserva.hora_inicio,
            "hora_fin": reserva.hora_fin,
            "descripcion": reserva.descripcion
        })
 
    return jsonify(resultado)
 
 
@app.route("/crear-reserva", methods=["POST"])
def crear_reserva():
 
    if not session.get("verificado"):
        return jsonify({
            "valido": False,
            "mensaje": "Debe verificar su correo antes de realizar una reserva."
        }), 401
 
    datos = request.get_json()
 
    fecha_texto = datos.get("fecha", "").strip()
    hora_inicio = datos.get("hora_inicio", "").strip()
    hora_fin = datos.get("hora_fin", "").strip()
    descripcion = datos.get("descripcion", "").strip()
 
    if not fecha_texto or not hora_inicio or not hora_fin or not descripcion:
        return jsonify({
            "valido": False,
            "mensaje": "Complete todos los campos."
        })
 
    try:
 
        fecha = datetime.strptime(
            fecha_texto,
            "%Y-%m-%d"
        ).date()
 
    except ValueError:
 
        return jsonify({
            "valido": False,
            "mensaje": "La fecha no es válida."
        })
 
    try:
 
        inicio = datetime.strptime(
            hora_inicio,
            "%H:%M"
        ).time()
 
        fin = datetime.strptime(
            hora_fin,
            "%H:%M"
        ).time()
 
    except ValueError:
 
        return jsonify({
            "valido": False,
            "mensaje": "La hora no es válida."
        })
 
    hora_minima = datetime.strptime(
        "07:00",
        "%H:%M"
    ).time()
 
    hora_maxima = datetime.strptime(
        "16:20",
        "%H:%M"
    ).time()
 
    if inicio < hora_minima or fin > hora_maxima:
 
        return jsonify({
            "valido": False,
            "mensaje": "Las reservas solamente pueden realizarse entre 7:00 a. m. y 4:20 p. m."
        })
 
    if inicio >= fin:
 
        return jsonify({
            "valido": False,
            "mensaje": "La hora de finalización debe ser posterior a la hora de inicio."
        })
 
    reservas = Reserva.query.filter_by(
        fecha=fecha
    ).all()
 
    for reserva in reservas:
 
        reserva_inicio = datetime.strptime(
            reserva.hora_inicio,
            "%H:%M"
        ).time()
 
        reserva_fin = datetime.strptime(
            reserva.hora_fin,
            "%H:%M"
        ).time()
 
        if inicio < reserva_fin and fin > reserva_inicio:
 
            return jsonify({
                "valido": False,
                "mensaje": "Ese horario ya está reservado."
            })
 
    nueva_reserva = Reserva(
        correo=session["correo"],
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        descripcion=descripcion
    )
 
    db.session.add(nueva_reserva)
    db.session.commit()
 
    return jsonify({
        "valido": True,
        "mensaje": "Reserva realizada correctamente.",
        "reserva": {
            "id": nueva_reserva.id,
            "fecha": nueva_reserva.fecha.isoformat(),
            "hora_inicio": nueva_reserva.hora_inicio,
            "hora_fin": nueva_reserva.hora_fin,
            "descripcion": nueva_reserva.descripcion
        }
    })
 
 
if __name__ == "__main__":
    app.run(debug=True)
 