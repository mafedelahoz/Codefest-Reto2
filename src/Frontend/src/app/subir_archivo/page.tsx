import Link from "next/link";
import CsvUploader from "../CsvUploader";

export default function Home() {
  return (
    <div className="flex flex-col w-full">
      <div
        className="w-full h-[400px] bg-cover bg-center"
        style={{ backgroundImage: "url('banner.png')" }}
      ></div>
      <div className="w-full bg-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold mb-4 text-left">Fuerza aerea colombiana</h1>
          <h2 className="text-2xl mb-6 text-left text-sky-700">
            Caracterización de señales de radiofrecuencia de enlaces satelitales
          </h2>
          <CsvUploader />
          <h2 className="text-center font-semibold mt-8">Opciones de visualización</h2>
          <div className="flex justify-center space-x-4">
            <span className="bg-blue-500 mt-3 text-white flex items-center w-32 text-center justify-center h-14 rounded transition duration-300 ease-in-out delay-200 hover:bg-blue-700">
              <Link href={"calcular"}>Calcular</Link>
            </span>
            <span className="bg-blue-500 text-white flex items-center w-32 text-center justify-center h-14 rounded mt-3 transition duration-300 ease-in-out delay-200 hover:bg-blue-700">
              <Link href={"visualizar"}>Visualizar</Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

