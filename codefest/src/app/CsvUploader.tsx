"use client";
import React, { useState } from 'react';
import axios from 'axios';

const CsvUploader: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Por favor, selecciona un archivo primero.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post('/api/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      alert('¡Archivo subido exitosamente!');
    } catch (error) {
      console.error(error);
      alert('Error al subir el archivo.');
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".csv"
        onChange={handleFileChange}
      />
      <button onClick={handleUpload}>Subir CSV</button>
    </div>
  );
};

export default CsvUploader;