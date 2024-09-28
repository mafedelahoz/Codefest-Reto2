export async function subirArchivo(file: FormData) {
    const data = await fetch('http://127.0.0.1:8000/subir_archivo', {
        method: 'POST',
        body: file
    });
    return data;
}

export async function obtenerMetricas() {
    const data = await fetch('http://127.0.0.1:8000/metricas');
    return data.json();
}