import csv
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import hilbert
# Lector de las tablas de encabezado del archivo CSV
def read_csv_header(file_path):
    header_data_1 = {}
    header_data_2 = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            if len(row) == 0 or not row[0]:  
                break
            key_1 = row[0]
            value_1 = row[1] if len(row) > 1 else None
            key_2 = row[4] if len(row) > 4 else None
            value_2 = row[5] if len(row) > 5 else None
            header_data_1[key_1] = value_1
            if key_2:
                header_data_2[key_2] = value_2
    return header_data_1, header_data_2

# Lector de los registros de datos del archivo CSV
def read_csv_data(file_path):
    header_data_1, header_data_2 = read_csv_header(file_path)
    data_records = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        header_processed = False
        for row in reader:
            if not header_processed:
                if len(row) == 0 or not row[0]:
                    header_processed = True
                continue
            cleaned_row = [value for value in row if value]  # Eliminar valores vacíos
            if cleaned_row:  # Añadir solo si la fila no está vacía después de limpiar
                data_records.append(cleaned_row)
    return header_data_1, header_data_2, data_records

def detect_modulation(data, sample_rate):
    # Análisis más detallado de AM y FM
    # ... (código para análisis de envolvente, espectro, etc.)

    # Por ahora, una implementación simplificada:
    if np.std(data) / np.mean(data) > 1:  # Alta varianza sugiere AM
        return "AM"
    elif np.std(np.diff(data)) > np.std(data):  # Alta varianza en la derivada sugiere FM
        return "FM"
    else:
        return "Desconocida"
def detect_prf(data, sample_rate):
    # Calcular la autocorrelación
    autocorr = np.correlate(data, data, mode='full')
    autocorr = autocorr[len(autocorr)//2:]  # Tomar solo la mitad positiva

    # Encontrar el primer pico significativo después del pico en cero
    peaks = np.where(np.r_[True, autocorr[1:] < autocorr[:-1], True])[0]
    if len(peaks) > 1:
        prf = sample_rate / (peaks[1] - peaks[0])
        return prf
    else:
        return None

def occupied_bandwidth_analysis(data, sample_rate, threshold=0.1):
    # Calcular la FFT
    yf = fft(data)
    xf = fftfreq(len(data), 1/sample_rate)

    # Encontrar el ancho de banda donde la potencia es mayor al umbral
    power_spectrum = np.abs(yf)**2
    occupied_bandwidth = np.sum(power_spectrum > threshold * np.max(power_spectrum)) / sample_rate
    return occupied_bandwidth
def frequency_drift(data, sample_rate):
    # Utilizar la transformada de Hilbert para estimar la frecuencia instantánea
    analytic_signal = hilbert(data)
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))
    instantaneous_frequency = (np.diff(instantaneous_phase) / (2.0*np.pi)) * sample_rate

    # Analizar la variación de la frecuencia instantánea
    # ... (código para calcular la desviación estándar, pendiente, etc.)
    return # Valor que representa el drift de frecuencia

import matplotlib.pyplot as plt

def temporal_spectrum_analysis(data, sample_rate, window_size=256):
    # Calcular el espectrograma
    freqs, times, Sxx = signal.spectrogram(data, fs=sample_rate, window='hann', nperseg=window_size)
    plt.pcolormesh(times, freqs, 10*np.log10(Sxx), shading='gouraud')
    plt.ylabel('Frecuencia [Hz]')
    plt.xlabel('Tiempo [seg]')
    plt.show()
# Convertir los registros a formato numérico
def convert_records_to_numeric(data_records):
    numeric_records = []
    for record in data_records:
        numeric_record = []
        for value in record:
            try:
                numeric_value = float(value.replace(',', '.'))
                numeric_record.append(numeric_value)
            except ValueError:
                continue
        if numeric_record:
            numeric_records.append(numeric_record)
    return numeric_records


def detect_interferences(data, sample_rate, threshold=0.1):
    # Calcular la FFT (Transformada de Fourier)
    yf = fft(data)
    xf = fftfreq(len(data), 1/sample_rate)

    # Encontrar los índices de los picos más altos
    peak_indices = np.argsort(np.abs(yf))[1:-1]
    peak_frequencies = xf[peak_indices]

    # Identificar los picos que superan el umbral como interferencias
    interference_frequencies = peak_frequencies[np.abs(yf[peak_indices]) > threshold]

    return interference_frequencies

# Calcular características y parámetros de la señal
def calculate_signal_parameters(data, sample_rate):
    min_frequency = np.min(data)
    max_frequency = np.max(data)
    center_frequency = (max_frequency + min_frequency) / 2
    bandwidth = max_frequency - min_frequency
    amplitude = np.max(data)
    power = np.sum(np.square(data)) / len(data)
    noise_level = np.mean(data)
    snr = amplitude / noise_level
    crest_factor = amplitude / np.sqrt(np.mean(np.square(data)))

    # Interferencias: Presencia de otras señales que interfieren en la banda de la señal.
    interferences = "Implementar detección de interferencias"

    # Modulación: Determinar el tipo de modulación utilizada.
    modulation = "Implementar detección de modulación"

    # Picos espectrales: Puntos donde la amplitud es máxima dentro del ancho de banda.
    spectral_peaks = np.sort(data)[-5:]

    # Análisis de ancho de banda de ocupación: Análisis de la cantidad de espectro utilizado por la señal.
    occupied_bandwidth_analysis = bandwidth

    # Frecuencia de repetición de pulso (PRF): Frecuencia de repetición de pulsos en señales moduladas en pulsos.
    prf = "Implementar detección de PRF"

    # Análisis de canal adyacente: Evaluación de la interferencia en canales adyacentes.
    adjacent_channel_analysis = "Implementar análisis de canal adyacente"

    # Drift de frecuencia: Cambios en la frecuencia central de la señal a lo largo del tiempo.
    frequency_drift = "Implementar detección de drift de frecuencia"

    # Tiempo de ocupación: Tiempo durante el cual la señal está presente en el espectro.
    occupancy_time = len(data) / sample_rate

    # Análisis de espectro temporal: Cómo varía el espectro a lo largo del tiempo.
    temporal_spectrum_analysis = "Implementar análisis de espectro temporal"

    # Medición de potencia de canal: Potencia total de la señal dentro de un ancho de banda de canal específico.
    channel_power_measurement = power

    return {
        'min_frequency': min_frequency,
        'max_frequency': max_frequency,
        'center_frequency': center_frequency,
        'bandwidth': bandwidth,
        'amplitude': amplitude,
        'power': power,
        'noise_level': noise_level,
        'snr': snr,
        'crest_factor': crest_factor,
        'interferences': interferences,
        'modulation': modulation,
        'spectral_peaks': spectral_peaks,
        'occupied_bandwidth_analysis': occupied_bandwidth_analysis,
        'prf': prf,
        'adjacent_channel_analysis': adjacent_channel_analysis,
        'frequency_drift': frequency_drift,
        'occupancy_time': occupancy_time,
        'temporal_spectrum_analysis': temporal_spectrum_analysis,
        'channel_power_measurement': channel_power_measurement
    }

# Generar un reporte de las características y parámetros de la señal
def generate_signal_report(parameters):
    report = "Reporte de Características y Parámetros de la Señal\n"
    report += "===============================================\n\n"
    for key, value in parameters.items():
        report += f"{key.replace('_', ' ').capitalize()}: {value}\n"
    return report

# Ejemplo de uso
file_path = 'Codefest csv.csv'
header_data_1, header_data_2, data_records = read_csv_data(file_path)

print("Tabla 1:")
for key, value in header_data_1.items():
    print(f"{key}: {value}")

print("\nTabla 2:")
for key, value in header_data_2.items():
    print(f"{key}: {value}")

# Convertir registros a formato numérico
numeric_records = convert_records_to_numeric(data_records)

# Combinar todos los registros en un solo array
combined_data = np.concatenate(numeric_records)

# Asumiendo un Span de 1MHz
sample_rate = 1e6  # 1 MHz

parameters = calculate_signal_parameters(combined_data, sample_rate)
report = generate_signal_report(parameters)
print(f"\nReporte del conjunto completo de datos:\n{report}")