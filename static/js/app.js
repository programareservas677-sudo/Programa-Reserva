let correoActual = "";
let temporizador = null;
 
document.getElementById("reservaForm").addEventListener("submit", async function(event) {
 
    event.preventDefault();
 
    const correo = document.getElementById("correo").value.trim().toLowerCase();
 
    const esAdministrador =
        correo === "programareservas677@gmail.com";
 
    const esTEC =
        correo.endsWith("@itcr.ac.cr");
 
    const esEstudiante =
        correo.endsWith("@estudiantec.cr");
 
    if (!esAdministrador && !esTEC && !esEstudiante) {
 
        mostrarMensaje(
            "No se puede ingresar. Debe utilizar un correo institucional del TEC.",
            false
        );
 
        return;
    }
 
    try {
 
        const respuesta = await fetch("/validar-correo", {
 
            method: "POST",
 
            headers: {
                "Content-Type": "application/json"
            },
 
            body: JSON.stringify({
                correo: correo
            })
        });
 
        const resultado = await respuesta.json();
 
        if (resultado.valido) {
 
            correoActual = correo;
 
            document.getElementById("verificacion").style.display = "block";
 
            document.getElementById("correo").disabled = true;
 
            mostrarMensaje(
                resultado.mensaje,
                true
            );
 
            iniciarTemporizador(
                resultado.segundos_restantes
            );
 
        } else {
 
            mostrarMensaje(
                resultado.mensaje,
                false
            );
        }
 
    } catch (error) {
 
        console.error(error);
 
        mostrarMensaje(
            "No se pudo conectar con el servidor.",
            false
        );
    }
 
});
 
document.getElementById("verificarPin").addEventListener("click", async function() {
 
    const pin =
        document.getElementById("pin").value.trim();
 
    if (!/^\d{6}$/.test(pin)) {
 
        mostrarMensaje(
            "Ingrese un código de 6 dígitos.",
            false
        );
 
        return;
    }
 
    try {
 
        const respuesta = await fetch("/verificar-pin", {
 
            method: "POST",
 
            headers: {
                "Content-Type": "application/json"
            },
 
            body: JSON.stringify({
                correo: correoActual,
                pin: pin
            })
        });
 
        const resultado = await respuesta.json();
 
        if (resultado.valido) {
 
            mostrarMensaje(
                resultado.mensaje,
                true
            );
 
            document.getElementById("pin").disabled = true;
 
            document.getElementById("verificarPin").disabled = true;
 
            if (temporizador !== null) {
                clearInterval(temporizador);
                temporizador = null;
            }
 
            setTimeout(function() {
                window.location.href = "/calendario";
            }, 700);
 
        } else {
 
            mostrarMensaje(
                resultado.mensaje,
                false
            );
        }
 
    } catch (error) {
 
        console.error(error);
 
        mostrarMensaje(
            "No se pudo conectar con el servidor.",
            false
        );
    }
 
});
 
function iniciarTemporizador(segundos) {
 
    if (temporizador !== null) {
        clearInterval(temporizador);
    }
 
    let tiempo = segundos;
 
    mostrarTiempo(tiempo);
 
    temporizador = setInterval(function() {
 
        tiempo--;
 
        mostrarTiempo(tiempo);
 
        if (tiempo <= 0) {
 
            clearInterval(temporizador);
 
            temporizador = null;
 
            mostrarMensaje(
                "El código ha expirado. Ahora puede solicitar un nuevo código.",
                false
            );
 
            document.getElementById("correo").disabled = false;
        }
 
    }, 1000);
}
 
function mostrarTiempo(segundos) {
 
    const minutos =
        Math.floor(segundos / 60);
 
    const segundosRestantes =
        segundos % 60;
 
    const elemento =
        document.getElementById("tiempoPIN");
 
    if (elemento) {
 
        elemento.textContent =
            "Tiempo restante: " +
            minutos +
            ":" +
            segundosRestantes
                .toString()
                .padStart(2, "0");
    }
}
 
function mostrarMensaje(mensaje, correcto) {
 
    const elemento =
        document.getElementById("mensajeSistema");
 
    if (elemento) {
 
        elemento.textContent =
            mensaje;
 
        elemento.style.color =
            correcto
                ? "green"
                : "red";
    }
}
 