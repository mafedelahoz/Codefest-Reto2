import Link from "next/link";

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
          <p>

          </p>
          <div>
    </div>
          <span className="bg-blue-500 text-white flex items-center w-36 justify-center mx-auto h-14 text-center rounded">
            <Link href={"subir_archivo"}>Comenzar</Link>
          </span>
        </div>
      </div>
    </div>
  )
}
