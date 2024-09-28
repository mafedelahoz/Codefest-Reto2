from fastapi import FastAPI, File, UploadFile
import aiofiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    print("Hola '/'")
    return {"Hello": "World"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    print("Se accedió a la ruta raíz '/'")
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = "uploads/csv"
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        return {"message": "Archivo subido exitosamente"}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/metricas")
async def metricas():
    file_path = "uploads/csv"
    if not os.path.exists(file_path):
        return {"error": "Archivo no encontrado."}

    try:
        data = pd.read_csv(file_path, delimiter=';', skiprows=52)
        data = data[['Frequency [Hz]', 'Magnitude [dBm]']]
        data['Frequency [Hz]'] = pd.to_numeric(data['Frequency [Hz]'].str.replace(',', '.', regex=False))
        data['Magnitude [dBm]'] = pd.to_numeric(data['Magnitude [dBm]'].str.replace(',', '.', regex=False))
        
        frequency_data = data['Frequency [Hz]']
        power_data = data['Magnitude [dBm]']

        frecuencia_central = frequency_data.mean()  # Frecuencia Central como promedio
        amplitud_maxima = power_data.max()           # Amplitud máxima
        potencia_maxima = np.power(amplitud_maxima, 3)

        threshold = potencia_maxima / 2
        bw_indices = np.where(power_data >= threshold)[0]
        ancho_de_banda = frequency_data[bw_indices[-1]] - frequency_data[bw_indices[0]] if len(bw_indices) > 1 else 0

        return {
            "Frecuencia Central": f"{frecuencia_central:.2f} Hz",
            "Amplitud Máxima": f"{amplitud_maxima:.2f} dB",
            "Potencia Máxima": f"{potencia_maxima:.2f} dB^2",
            "Ancho de Banda": f"{ancho_de_banda:.2f} Hz"
            }
    except Exception as e:
        return {"error": str(e)}