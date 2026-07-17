document.getElementById('btnCrear').addEventListener('click', () => lanzarProceso('/crear_app'));
document.getElementById('btnExplorar').addEventListener('click', () => lanzarProceso('/explorar_app'));
document.getElementById('btnRevisar').addEventListener('click', () => lanzarProceso('/revisar_app'));
document.getElementById('btnCorregir').addEventListener('click', () => lanzarProceso('/corregir_app'));

// BOTÓN DE DESTRUCCIÓN DE DATOS LOCAL (RAM)
document.getElementById('btnBorrarTodo').addEventListener('click', () => {
    document.getElementById('appDescripcion').value = "";
    document.getElementById('sugerenciasPanel').innerText = "Las guías maestras, análisis de exploración y explicaciones completas de tus códigos aparecerán aquí...";
    for (let i = 1; i <= 5; i++) {
        document.getElementById(`code${i}`).value = "";
    }
    window.gc && window.gc();
});

async function lanzarProceso(endpoint) {
    const desc = document.getElementById('appDescripcion').value;
    const btnCrear = document.getElementById('btnCrear');
    const btnExplorar = document.getElementById('btnExplorar');
    const btnRevisar = document.getElementById('btnRevisar');
    const btnCorregir = document.getElementById('btnCorregir');

    if (!desc.trim() && (endpoint === '/crear_app' || endpoint === '/explorar_app')) {
        return alert("Por favor, introduce tus ideas o descripción técnica en la caja superior primero.");
    }

    // Bloqueamos los 4 botones de acción para proteger el flujo secuencial de datos
    [btnCrear, btnExplorar, btnRevisar, btnCorregir].forEach(b => b.disabled = true);
    document.getElementById('sugerenciasPanel').innerText = "Abriendo hilos de procesamiento y conectando de forma segura con la IA en tiempo real...";

    try {
        const payload = { descripcion: desc };
        for (let i = 1; i <= 5; i++) {
            payload[`nombre${i}`] = document.getElementById(`name${i}`).value;
            payload[`codigo${i}`] = document.getElementById(`code${i}`).value;
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let streamAcumulado = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            streamAcumulado += decoder.decode(value, { stream: true });
            procesarStreamMultiArchivo(streamAcumulado);
        }
    } catch (error) {
        alert("La transmisión con el núcleo de procesamiento local fue interrumpida.");
    } finally {
        [btnCrear, btnExplorar, btnRevisar, btnCorregir].forEach(b => b.disabled = false);
    }
}

function procesarStreamMultiArchivo(texto) {
    // 1. Procesar Sugerencias, Consultoría o Informes de Exploración
    const inicioSuj = texto.indexOf(":::INICIO_SUGERENCIAS:::");
    const finSuj = texto.indexOf(":::FIN_SUGERENCIAS:::");
    if (inicioSuj !== -1) {
        const corteFin = (finSuj !== -1) ? finSuj : texto.length;
        document.getElementById('sugerenciasPanel').innerText = texto.substring(inicioSuj + 24, corteFin).trim();
    }

    // 2. Procesar e Inyectar códigos en los 5 paneles si el endpoint los genera
    let posicionActual = 0;
    let contadorPaneles = 1;

    while (texto.indexOf(":::INICIO_ARCHIVO:::", posicionActual) !== -1 && contadorPaneles <= 5) {
        const inicioM = texto.indexOf(":::INICIO_ARCHIVO:::", posicionActual);
        const saltoLinea = texto.indexOf("\n", inicioM);
        const finM = texto.indexOf(":::FIN_ARCHIVO:::", inicioM);

        if (saltoLinea !== -1 && saltoLinea > inicioM) {
            const encabezado = texto.substring(inicioM + 20, saltoLinea).trim();
            const finBloque = (finM !== -1) ? finM : texto.length;
            const codigoLimpio = texto.substring(saltoLinea + 1, finBloque).trim();

            const inputNombre = document.getElementById(`name${contadorPaneles}`);
            const areaCodigo = document.getElementById(`code${contadorPaneles}`);

            if (areaCodigo) {
                if (encabezado && inputNombre.value.trim() === "") {
                    inputNombre.value = encabezado;
                }
                areaCodigo.value = codigoLimpio;
            }
        }
        posicionActual = (finM !== -1) ? finM + 17 : texto.length;
        contadorPaneles++;
    }
}
