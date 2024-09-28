import type { NextApiRequest, NextApiResponse } from 'next';
import formidable, { File } from 'formidable';
import fs from 'fs';
import path from 'path';

export const config = {
  api: {
    bodyParser: false, // Desactiva el bodyParser para manejar 'formidable'
  },
};

const uploadCsv = async (
  req: NextApiRequest,
  res: NextApiResponse
) => {
  const form = new formidable.IncomingForm();

  form.parse(req, async function (err, fields, files) {
    if (err) {
      console.error(err);
      res.status(500).send('Error al analizar el archivo');
      return;
    }

    // Verifica si 'files.file' está definido
    if (!files.file) {
      res.status(400).send('No se ha subido ningún archivo');
      return;
    }

    // Maneja el caso donde 'files.file' es un array
    let file: File;
    if (Array.isArray(files.file)) {
      file = files.file[0]; // Toma el primer archivo si hay múltiples
    } else {
      file = files.file;
    }

    const tempFilePath = file.filepath;

    // Ruta de destino
    const destinationDir = path.join(process.cwd(), 'src', 'docs');
    const destinationFilePath = path.join(destinationDir, 'data.csv');

    // Crea el directorio si no existe
    fs.mkdirSync(destinationDir, { recursive: true });

    // Mueve el archivo al destino
    fs.copyFile(tempFilePath, destinationFilePath, (err) => {
      if (err) {
        console.error(err);
        res.status(500).send('Error al guardar el archivo');
        return;
      }

      res.status(200).send('Archivo subido exitosamente');
    });
  });
};

export default uploadCsv;