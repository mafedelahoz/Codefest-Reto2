"use client";
import { useState } from 'react';
import { openDB } from 'idb';
import axios from 'axios';

// Abrir la base de datos IndexedDB
const dbPromise = openDB('csv-store', 1, {
  upgrade(db) {
    if (!db.objectStoreNames.contains('files')) {
      db.createObjectStore('files');
    }
  },
});

// Funciones para almacenar y recuperar el archivo CSV en IndexedDB
const storeCSV = async (file: File) => {
  const db = await dbPromise;
  await db.put('files', file, 'csv-file');
};

export const resetCSV = async () => {
  const db = await dbPromise;
  await db.delete('files', 'csv-file');
};

export const getCSV = async () => {
  const db = await dbPromise;
  return await db.get('files', 'csv-file');
};

const CsvUploader: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [csvData, setCsvData] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Por favor, selecciona un archivo primero.');
      return;
    }

    try {
      // Guardar el archivo en IndexedDB
      await storeCSV(file);

      // Crear un FormData para enviar el archivo
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('http://localhost:8000/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        alert('¡Archivo enviado exitosamente al servidor!');
      } else {
        alert('Error al enviar el archivo.');
      }

      alert('¡Archivo guardado exitosamente en el almacenamiento local y subido al servidor!');
    } catch (error) {
      console.error(error);
      alert('Error al guardar el archivo.');
    }
  };

  // Función para recuperar el archivo desde IndexedDB
  const handleLoadFromStorage = async () => {
    try {
      const storedFile = await getCSV();
      if (storedFile) {
        setCsvData(storedFile);
        alert('¡Archivo recuperado del almacenamiento local!');
      } else {
        alert('No se encontró ningún archivo guardado.');
      }
    } catch (error) {
      console.error(error);
      alert('Error al cargar el archivo desde el almacenamiento.');
    }
  };

  const handleResetStorage = async () => {
    try {
      await resetCSV();
      setCsvData(null);
      alert('¡Archivo eliminado del almacenamiento local!');
    } catch (error) {
      console.error(error);
      alert('Error al eliminar el archivo del almacenamiento.');
    }
  };

  return (
    <div>
      <input type="file" accept=".csv" onChange={handleFileChange} className="block w-80 p-2 text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-200 transition duration-300 ease-in-out delay-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-5 mx-auto" />
      <h2 className='font-semibold text-8 text-center'>Opciones de carga de archivo</h2>
      <div className="flex justify-center space-x-4">
  <button
    className="bg-red-500 text-white flex items-center w-32 text-center justify-center h-14 rounded transition duration-300 ease-in-out delay-200 hover:bg-red-700"
    onClick={handleUpload}
  >
    Guardar y Subir CSV
  </button>
  <button
    className="bg-red-500 text-white flex items-center w-32 text-center justify-center h-14 rounded transition duration-300 ease-in-out delay-200 hover:bg-red-700"
    onClick={handleLoadFromStorage}
  >
    Cargar CSV desde Local
  </button>
  <button
    className="bg-red-500 text-white flex items-center w-32 text-center justify-center h-14 rounded transition duration-300 ease-in-out delay-200 hover:bg-red-700"
    onClick={handleResetStorage}
  >
    Reset CSV desde Local
  </button>
</div>

      {csvData && (
        <div>
          <h3 className='text-center'>Archivo cargado:</h3>
          <p className='text-center'>{csvData.name}</p>
        </div>
      )}
    </div>
  );
};

export default CsvUploader;
