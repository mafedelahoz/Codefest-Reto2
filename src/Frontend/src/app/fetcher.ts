

/* Funcion que hace fetch al endpoint de subir archivo */
export async function subirArchivo(file: FormData) {
    const data = await fetch('http://127.0.0.1:8000/subir_archivo', {
        method: 'POST',
        body: file
    });
    return data;
}
/* Funcion que hace fetch al endpoint de obtener metricas del archivo subido */
export async function obtenerMetricas() {
    const data = await fetch('http://127.0.0.1:8000/metricas');
    return data.json();
}

/* Funcion que hace fetch al endpoint de obtener el archivo subido */
export async function obtenerGrafico() {
    const response = await fetch('http://127.0.0.1:8000/visualizar-grafico');

    if (!response.ok) {
      throw new Error("Error al obtener el gráfico");
    }

    const blob = await response.blob(); 
    return blob;
  }