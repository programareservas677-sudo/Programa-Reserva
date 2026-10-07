document.getElementById("reservaForm").addEventListener("submit", async function(event) {
    event.preventDefault();
 
    const correo = document.getElementById("correo").value;
 
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
        alert("Correo válido: " + resultado.tipo);
    } else {
        alert(resultado.mensaje);
    }
});