let correoActual = "";
 
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
 
    } else {
 
        mostrarMensaje(resultado.mensaje, false);
    }
 
});
 
 
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