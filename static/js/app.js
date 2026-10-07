let correoActual = "";
let temporizador = null;
 
document.getElementById("reservaForm").addEventListener("submit", async function(event) {
    event.preventDefault();
 
    const correo = document.getElementById("correo").value.trim();
 
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
 
        mostrarMensaje(resultado.mensaje, true);
 
        iniciarTemporizador(resultado.segundos_restantes);
 
    } else {
 
        mostrarMensaje(resultado.mensaje, false);
    }
});
 
 
document.getElementById("verificarPin").addEventListener("click", async function() {
 
    const pin = document.getElementById("pin").value.trim();
 
    if (pin.length !== 6) {
        mostrarMensaje("Ingrese un código de 6 dígitos.", false);
        return;
    }
 
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
 
        mostrarMensaje(resultado.mensaje, true);
 
        document.getElementById("pin").disabled = true;
        document.getElementById("verificarPin").disabled = true;
 
        if (temporizador) {
            clearInterval(temporizador);
        }
 
    } else {
 
        mostrarMensaje(resultado.mensaje, false);
    }
});
 
 
function iniciarTemporizador(segundos) {
 
    if (temporizador) {
        clearInterval(temporizador);
    }
 
    let tiempo = segundos;
 
    mostrarTiempo(tiempo);
 
    temporizador = setInterval(function() {
 
        tiempo--;
 
        mostrarTiempo(tiempo);
 
        if (tiempo <= 0) {
 
            clearInterval(temporizador);
 
            mostrarMensaje(
                "El código ha expirado. Ahora puede solicitar un nuevo código.",
                false
            );
 
            document.getElementById("correo").disabled = false;
        }
 
    }, 1000);
}
 
 
function mostrarTiempo(segundos) {
 
    const minutos = Math.floor(segundos / 60);
    const segundosRestantes = segundos % 60;
 
    let elemento = document.getElementById("tiempoPIN");
 
    if (!elemento) {
 
        elemento = document.createElement("p");
        elemento.id = "tiempoPIN";
 
        document.getElementById("verificacion").appendChild(elemento);
    }
 
    elemento.textContent =
        "Tiempo restante: " +
        minutos +
        ":" +
        segundosRestantes.toString().padStart(2, "0");
}
 
 
function mostrarMensaje(mensaje, correcto) {
 
    let elemento = document.getElementById("mensajeSistema");
 
    if (!elemento) {
 
        elemento = document.createElement("p");
        elemento.id = "mensajeSistema";
 
        document.querySelector(".contenedor").appendChild(elemento);
    }
 
    elemento.textContent = mensaje;
 
    if (correcto) {
        elemento.style.color = "green";
    } else {
        elemento.style.color = "red";
    }
}