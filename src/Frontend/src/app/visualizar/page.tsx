"use client";
import Link from "next/link";
import { obtenerGrafico } from "../fetcher";
import { useEffect, useState } from "react";

export default function Home() {
  const [imagen, setImagen] = useState("");
  const [imageBlob, setImageBlob] = useState<Blob | null>(null);

  useEffect(() => {
    obtenerGrafico().then((data) => {
      const blob = new Blob([data], { type: "image/png" });
      const imageUrl = URL.createObjectURL(blob);
      setImagen(imageUrl);
      setImageBlob(blob); // Guardamos el Blob para usarlo en la descarga
    });
  }, []);

  // Función para descargar la imagen
  const handleDownload = () => {
    if (imageBlob) {
      const url = URL.createObjectURL(imageBlob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "grafico.png"); // Nombre del archivo a descargar
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link); // Removemos el enlace después de la descarga
    }
  };

  return (
    <div className="flex flex-col w-full">
      <div
        className="w-full h-[400px] bg-cover bg-center"
        style={{
          backgroundImage:
            "url('banner.png')",
        }}
      ></div>
      <div className="w-full bg-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold mb-4 text-left">Fuerza Aérea Colombiana</h1>
          <h2 className="text-2xl mb-6 text-left text-sky-700">
            Caracterización de señales de radiofrecuencia de enlaces satelitales
          </h2>
          
          {imagen ? (
            <img src={imagen} alt="Gráfico generado" />
          ) : (
            <p>Cargando gráfico...</p>
          )}

          <span className="bg-blue-500 text-white flex items-center w-32 text-center justify-center mx-auto h-14 rounded transition duration-300 ease-in-out delay-200 hover:bg-blue-700">
            <Link href={"subir_archivo"}>Comenzar de nuevo</Link>
          </span>

          <button
            onClick={handleDownload}
            className="bg-green-500 text-white flex items-center w-32 text-center justify-center mx-auto h-14 rounded mt-4 transition duration-300 ease-in-out delay-200 hover:bg-green-700"
          >
            Descargar gráficos
          </button>
        </div>
      </div>
    </div>
  );
}
