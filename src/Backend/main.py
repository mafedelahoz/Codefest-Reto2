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
    
@app.delete("/delete-csv")
async def delete_csv():
    file_path = "uploads/csv"
    
    if not os.path.exists(file_path):
        return {"error": "Archivo no encontrado."}

    try:
        os.remove(file_path)
        return {"message": "Archivo eliminado exitosamente."}
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

        # Métricas principales
        frecuencia_central = frequency_data.mean()  # Frecuencia Central
        amplitud_maxima = power_data.max()           # Amplitud máxima
        potencia_maxima = np.power(amplitud_maxima, 3)

        # Ancho de banda basado en un umbral
        threshold = potencia_maxima / 2
        bw_indices = np.where(power_data >= threshold)[0]
        ancho_de_banda = frequency_data[bw_indices[-1]] - frequency_data[bw_indices[0]] if len(bw_indices) > 1 else 0

        response['Frecuencia Central'] = f"{frecuencia_central:.2f} Hz"
        response["Amplitud Máxima"] = f"{amplitud_maxima:.2f} dB"
        response["Potencia Máxima"] = f"{potencia_maxima:.2f} dB^2"
        response["Ancho de Banda"] = f"{ancho_de_banda:.2f} Hz"
        
        # FFT y otras métricas derivadas
        fft_result = np.fft.fft(power_data)
        fft_magnitude = np.abs(fft_result)
        fft_frequency = np.fft.fftfreq(len(power_data), frequency_data[1] - frequency_data[0])

        # Potencia de la señal y ruido (RMS)
        signal_band = (fft_frequency > 400) & (fft_frequency < 500)
        # Estimar la potencia de la señal: usando la potencia máxima o RMS dentro de la banda de la señal
        if np.any(signal_band):  # Check if any values in signal_band are True
            signal_power_rms = np.sqrt(np.mean(np.square(fft_magnitude[signal_band])))
        else:
            signal_power_rms = fft_magnitude.max() #Si no se detecta señal, se toma el valor máximo de la magnitud de la FFT

        noise_band = ~signal_band
        noise_power_rms = np.sqrt(np.mean(np.square(fft_magnitude[noise_band])))
        snr_db = 10 * np.log10(signal_power_rms / noise_power_rms)

        response["Potencia de la Señal (RMS)"] = f"{signal_power_rms:.2f}"
        response["Potencia del Ruido (RMS)"] = f"{noise_power_rms:.2f}"
        response["Relación Señal-Ruido (SNR)"] = f"{snr_db:.2f} dB"

        # Forma de la señal
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

        # Frecuencias espurias
        umbral_espurias = 0.2 * signal_power_rms
        espurias_indices = np.where((fft_magnitude > umbral_espurias) & (~signal_band))[0]
        espurias_frecuencias = fft_frequency[espurias_indices]
        response["Frecuencias Espurias Detectadas"] = espurias_frecuencias.tolist()
        response["Número de Frecuencias Espurias"] = len(espurias_frecuencias)

        # Frecuencias armónicas
        frecuencia_fundamental = 435e6  # 435 MHz
        num_armonicas = 5
        frecuencias_armonicas = [n * frecuencia_fundamental for n in range(1, num_armonicas + 1)]
        response["Frecuencias Armónicas Calculadas"] = [f"{f / 1e6:.2f} MHz" for f in frecuencias_armonicas]

        # Definir el umbral para identificar interferencias
        threshold = np.mean(fft_magnitude) + 3 * np.std(fft_magnitude)  # Ejemplo: promedio + 3 desviaciones estándar, este umbral fue definido para el caso de estudio

        # Identificar picos que superen el umbral
        interference_indices = np.where(fft_magnitude > threshold)[0]
        interference_frequencies = fft_frequency[interference_indices]
        interference_magnitudes = fft_magnitude[interference_indices]

        # Mostrar las frecuencias e intensidades de las interferencias detectadas
        response["Interferencias Detectadas"] = [f"Frecuencia: {f:.2f} Hz, Magnitud: {m:.2f}" for f, m in zip(interference_frequencies, interference_magnitudes)]

        from scipy.signal import find_peaks

        #Encontrar picos en la magnitud de la FFT y sus frecuencias correspondientes, se establece un umbral de 0.2 para detectar picos significativos
        peaks, _ = find_peaks(fft_magnitude, height=0.01 * fft_magnitude.max()) #Se establece un umbral del 1% de la magnitud máxima de la FFT para detectar picos significativos
        peak_frequencies = fft_frequency[peaks]
        peak_magnitudes = fft_magnitude[peaks]
        #Mostrar los picos detectados
        response["Picos Detectados"] = [f"Frecuencia: {f:.2f} Hz, Magnitud: {m:.2f}" for f, m in zip(peak_frequencies, peak_magnitudes)]

        # Potencias máximas y RMS
        valor_maximo = np.max(power_data)
        valor_rms = np.sqrt(np.mean(np.square(power_data)))
        crest_factor = valor_maximo / valor_rms

        response["Valor Máximo de Potencia"] = f"{valor_maximo:.2f} dB"
        response["Valor RMS de Potencia"] = f"{valor_rms:.2f} dB"
        response["Crest Factor"] = f"{crest_factor:.2f}"

        # PRF (Frecuencia de repetición de pulso)
        from scipy.signal import find_peaks
        peaks_indices, _ = find_peaks(power_data, height=0)  # Detectar picos
        peak_times = peaks_indices
        if len(peak_times) > 1:
            pulse_intervals = np.diff(peak_times)
            average_prt = np.mean(pulse_intervals)
            prf = 1 / average_prt
        else:
            prf = 0
        response["PRF (Frecuencia de Repetición de Pulso)"] = f"{prf:.2f} Hz"

        # Calcular la frecuencia de lso canales y la relación señal a interferencia
        # Definir las frecuencias de los canales adyacentes
        frecuencia_canal_adyacente_1 = 434e6  # Frecuencia del canal adyacente 1
        frecuencia_canal_adyacente_2 = 436e6  # Frecuencia del canal adyacente 2

        # Calcular la relación señal a interferencia
        snir_1 = signal_power_rms / (noise_power_rms + np.max(power_data[frequency_data == frecuencia_canal_adyacente_1]))
        snir_2 = signal_power_rms / (noise_power_rms + np.max(power_data[frequency_data == frecuencia_canal_adyacente_2]))
        # Mostrar los resultados
        response["Relación Señal a Interferencia para Canal Adyacente 1"] = f"{snir_1:.2f}"
        response["Relación Señal a Interferencia para Canal Adyacente 2"] = f"{snir_2:.2f}"

        
        # Definir ancho de banda ocupado por las señales satelitales detectadas
        bandwidth = 10e6  # Ancho de banda de 10 MHz para señales satelitales
        # Calcular la cantidad de canales que pueden ser acomodados en el ancho de banda
        num_channels = int(ancho_de_banda / bandwidth)
        # Mostrar los resultados
        response["Número de Frecuencias Espurias"] = num_channels
        # Definir el ancho de banda de un canal de comunicación
        channel_bandwidth = 200e3  # Ancho de banda de un canal de comunicación de 200 kHz
        # Calcular la cantidad de canales que pueden ser acomodados en el ancho de banda
        num_channels = int(ancho_de_banda / channel_bandwidth)

        # Mostrar los resultados
        response["Ancho de Banda Ocupado por las Señales Satelitales"] = f"{ancho_de_banda / 1e6:.2f} MHz"
        response["Número de Canales que Pueden Ser Acomodados"] = num_channels

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