"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { obtenerMetricas } from "@/app/fetcher";

export default function Home() {
  const [metricas, setMetricas] = useState<DataProps | null>(null);

  useEffect(() => {
    obtenerMetricas().then((data) => {
      setMetricas(data);
    });
  }, []);

  const handleDownloadCSV = () => {
    if (!metricas) return;

    const csvContent = convertToCSV(metricas);
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "metricas.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col w-full">
      <div
        className="w-full h-[400px] bg-cover bg-center"
        style={{
          backgroundImage: "url('banner.png')",
        }}
      ></div>
      <div className="w-full bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold mb-4 text-left">Fuerza Aérea Colombiana</h1>
          <h2 className="text-2xl mb-6 text-left text-sky-700">
            Caracterización de señales de radiofrecuencia de enlaces satelitales
          </h2>
          <ComponenteTabla data={metricas} />
          <span className="bg-blue-500 text-white flex items-center w-32 text-center h-16 justify-center mx-auto rounded transition duration-300 ease-in-out delay-200 hover:bg-blue-700">
            <Link href={"subir_archivo"}>Comenzar de nuevo</Link>
          </span>
          <button
            onClick={handleDownloadCSV}
            className="bg-green-500 text-white flex items-center w-32 text-center justify-center mx-auto rounded mt-4 transition duration-300 ease-in-out delay-200 hover:bg-green-700"
          >
            Descargar cálculos
          </button>
        </div>
      </div>
    </div>
  );
}

interface DataProps {
  "Frecuencia Central": string;
  "Amplitud Máxima": string;
  "Potencia Máxima": string;
  "Ancho de Banda": string;
}

const ComponenteTabla: React.FC<{ data: DataProps | null }> = ({ data }) => {
  if (!data) {
    return <p>Cargando métricas...</p>;
  }

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="w-full overflow-x-auto">
        <h1 className="text-center text-2xl font-bold mb-4">Métricas</h1>
        <table className="table-auto w-full bg-white shadow-md rounded-lg border-collapse">
          <thead>
            <tr className="bg-blue-500 text-white">
              <th className="px-4 py-2">Clave</th>
              <th className="px-4 py-2">Valor</th>
            </tr>
          </thead>
          <tbody>
            {Object.keys(data).map((key) => (
              <tr key={key} className="border-t">
                <td className="px-4 py-2 text-gray-700">{key}</td>
                <td className="px-4 py-2 text-gray-900">{data[key as keyof DataProps]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function convertToCSV(data: DataProps): string {
  const csvRows = [
    ["Clave", "Valor"],
    ...Object.entries(data),
  ];
  const csvContent = csvRows.map((row) => row.join(",")).join("\n");
  return csvContent;
}
