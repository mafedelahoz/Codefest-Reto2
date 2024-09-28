from fastapi import FastAPI, File, UploadFile
import aiofiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from io import BytesIO

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
        response = {}
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

        response['Frecuencia Central'] = f"{frecuencia_central:.2f} Hz"
        response["Amplitud Máxima"] = f"{amplitud_maxima:.2f} dB"
        response["Potencia Máxima"] = f"{potencia_maxima:.2f} dB^2"
        response["Ancho de Banda"] = f"{ancho_de_banda:.2f} Hz"
        
        fft_result = np.fft.fft(power_data)
        fft_magnitude = np.abs(fft_result)
        fft_frequency = np.fft.fftfreq(len(power_data), frequency_data[1] - frequency_data[0])

        signal_band = (fft_frequency > 400) & (fft_frequency < 500)
        if np.any(signal_band):  # Check if any values in signal_band are True
            signal_power_rms = np.sqrt(np.mean(np.square(fft_magnitude[signal_band])))
        else:
            signal_power_rms = 0  # Or some other appropriate value

        noise_band = ~signal_band
        noise_power_rms = np.sqrt(np.mean(np.square(fft_magnitude[noise_band])))
        snr_db = 10 * np.log10(signal_power_rms / noise_power_rms)

        response["Potencia de la Señal (RMS)"] = f"{signal_power_rms:.2f}"
        response["Potencia del Ruido (RMS)"] = f"{noise_power_rms:.2f}"
        response["Relación Señal-Ruido (SNR)"] = f"{snr_db:.2f} dB"

        if ancho_de_banda < 10 and snr_db > 20:
            forma = "Pico estrecho y dominante"
        elif ancho_de_banda > 10 and snr_db > 20:
            forma = "Ancha y clara"
        elif snr_db < 10:
            forma = "Señal ruidosa"
        elif len(np.where(fft_magnitude[signal_band] > noise_power_rms * 2)[0]) > 1:
            forma = "Múltiples picos"
        else:
            forma = "Difusa o indefinida"

        response["Forma de la Señal"] = forma

        return response
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/visualizar-grafico")
async def visualizar_grafico():
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

        # Generar el gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(frequency_data, power_data)
        plt.title('Gráfico de Frecuencia vs Potencia')
        plt.xlabel('Frecuencia [Hz]')
        plt.ylabel('Potencia [dBm]')
        plt.grid(True)

        # Guardar el gráfico en un objeto BytesIO
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Devolver el gráfico como una imagen
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}