let fechaCalendario = new Date();
let reservas = [];
 
async function cargarReservas() {
    const respuesta = await fetch("/reservas");
 
    if (!respuesta.ok) {
        return;
    }
 
    reservas = await respuesta.json();
 
    mostrarCalendario();
}
 
function mostrarCalendario() {
    const contenedor = document.getElementById("diasCalendario");
 
    contenedor.innerHTML = "";
 
    const año = fechaCalendario.getFullYear();
    const mes = fechaCalendario.getMonth();
 
    const nombresMeses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    ];
 
    document.getElementById("tituloMes").textContent =
        nombresMeses[mes] + " " + año;
 
    const primerDia = new Date(año, mes, 1);
 
    let diaSemana = primerDia.getDay();
 
    diaSemana = diaSemana === 0 ? 6 : diaSemana - 1;
 
    const cantidadDias =
        new Date(año, mes + 1, 0).getDate();
 
    for (let i = 0; i < diaSemana; i++) {
        const espacio = document.createElement("div");
 
        espacio.className = "dia vacio";
 
        contenedor.appendChild(espacio);
    }
 
    for (let dia = 1; dia <= cantidadDias; dia++) {
 
        const elemento = document.createElement("button");
 
        elemento.type = "button";
        elemento.className = "dia";
 
        const fecha =
            `${año}-${String(mes + 1).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;
 
        elemento.textContent = dia;
 
        const tieneReserva = reservas.some(function(reserva) {
            return reserva.fecha === fecha;
        });
 
        if (tieneReserva) {
            elemento.classList.add("dia-ocupado");
        }
 
        elemento.addEventListener("click", function() {
            seleccionarFecha(fecha);
        });
 
        contenedor.appendChild(elemento);
    }
}
 
function seleccionarFecha(fecha) {
    document.getElementById("fecha").value = fecha;
 
    mostrarReservasDelDia(fecha);
}
 
function mostrarReservasDelDia(fecha) {
 
    const reservasDia = reservas.filter(function(reserva) {
        return reserva.fecha === fecha;
    });
 
    console.log("Reservas del día:", reservasDia);
}
 
document
    .getElementById("mesAnterior")
    .addEventListener("click", function() {
 
        fechaCalendario.setMonth(
            fechaCalendario.getMonth() - 1
        );
 
        mostrarCalendario();
    });
 
document
    .getElementById("mesSiguiente")
    .addEventListener("click", function() {
 
        fechaCalendario.setMonth(
            fechaCalendario.getMonth() + 1
        );
 
        mostrarCalendario();
    });
 
document
    .getElementById("formReserva")
    .addEventListener("submit", async function(event) {
 
        event.preventDefault();
 
        const fecha =
            document.getElementById("fecha").value;
 
        const horaInicio =
            document.getElementById("horaInicio").value;
 
        const horaFin =
            document.getElementById("horaFin").value;
 
        const descripcion =
            document.getElementById("descripcion").value.trim();
 
        const respuesta = await fetch("/crear-reserva", {
 
            method: "POST",
 
            headers: {
                "Content-Type": "application/json"
            },
 
            body: JSON.stringify({
                fecha: fecha,
                hora_inicio: horaInicio,
                hora_fin: horaFin,
                descripcion: descripcion
            })
        });
 
        const resultado = await respuesta.json();
 
        const mensaje =
            document.getElementById("mensajeReserva");
 
        mensaje.textContent = resultado.mensaje;
 
        mensaje.style.color =
            resultado.valido ? "green" : "red";
 
        if (resultado.valido) {
 
            document
                .getElementById("formReserva")
                .reset();
 
            await cargarReservas();
        }
    });
 
cargarReservas();
 