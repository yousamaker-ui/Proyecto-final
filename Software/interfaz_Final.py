import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np

from scipy.signal import find_peaks
from scipy.signal import butter, filtfilt
from scipy.signal import stft

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import winsound

# FUNCIONES


def calcular_mdf_stft(signal, fs):

    signal = signal - np.mean(signal)

    N = len(signal)

    if N < 8:
        return 0

    nperseg = min(256, N)
    noverlap = nperseg // 2

    freqs, tiempos, Zxx = stft(
        signal,
        fs=fs,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        boundary=None
    )

    potencia = np.abs(Zxx) ** 2

    potencia_promedio = np.mean(potencia, axis=1)

    # quitar frecuencia 0 Hz
    freqs = freqs[1:]
    potencia_promedio = potencia_promedio[1:]

    potencia_total = np.sum(potencia_promedio)

    if potencia_total == 0:
        return 0

    potencia_acumulada = np.cumsum(potencia_promedio)

    idx = np.where(
        potencia_acumulada >= potencia_total / 2
    )[0][0]

    return freqs[idx]


def filtrar_ecg(ecg, fs):

    low = 5 / (fs / 2)
    high = 20 / (fs / 2)

    b, a = butter(4, [low, high], btype="band")

    return filtfilt(b, a, ecg)



# CARGAR ARCHIVOS


root_tmp = tk.Tk()
root_tmp.withdraw()

print("Seleccione EMG")

emg_file = filedialog.askopenfilename(
    title="Seleccione archivo EMG",
    filetypes=[("Archivos CSV", "*.csv")]
)

print("Seleccione ECG")

ecg_file = filedialog.askopenfilename(
    title="Seleccione archivo ECG",
    filetypes=[("Archivos CSV", "*.csv")]
)


# LEER ARCHIVOS


emg_df = pd.read_csv(emg_file)
ecg_df = pd.read_csv(ecg_file)

t_emg = emg_df.iloc[:, 0].values / 1000
emg = emg_df.iloc[:, 1].values

t_ecg = ecg_df.iloc[:, 0].values / 1000
ecg = ecg_df.iloc[:, 1].values

Fs_emg = 1 / np.mean(np.diff(t_emg))
Fs_ecg = 1 / np.mean(np.diff(t_ecg))

print("Fs EMG =", Fs_emg)
print("Fs ECG =", Fs_ecg)


# FILTRAR ECG


ecg_filtrado = filtrar_ecg(ecg, Fs_ecg)


ventana = tk.Tk()
ventana.title("Monitor de Fatiga Neuromuscular con STFT")


fig = Figure(figsize=(10, 7))

ax1 = fig.add_subplot(411)
ax2 = fig.add_subplot(412)
ax3 = fig.add_subplot(413)
ax4 = fig.add_subplot(414)

canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


frame = tk.Frame(ventana)
frame.pack(fill=tk.X)

lbl_mdf = tk.Label(
    frame,
    text="MDF STFT: -- Hz",
    font=("Arial", 14)
)
lbl_mdf.pack()

lbl_bpm = tk.Label(
    frame,
    text="BPM: --",
    font=("Arial", 14)
)
lbl_bpm.pack()

lbl_caida = tk.Label(
    frame,
    text="Caída MDF: -- %",
    font=("Arial", 14)
)
lbl_caida.pack()

lbl_estado = tk.Label(
    frame,
    text="NORMAL",
    bg="green",
    fg="white",
    font=("Arial", 20, "bold")
)
lbl_estado.pack(fill=tk.X, pady=10)


bloque_emg = int(Fs_emg)
bloque_ecg = int(Fs_ecg)

indice_emg = 0
indice_ecg = 0

mdf_hist = []
tiempo_mdf = []

bpm_hist = []
tiempo_bpm = []

MDF_ref = None
BPM_ref = None

alarma_activada = False


def actualizar():

    global indice_emg
    global indice_ecg
    global MDF_ref
    global BPM_ref
    global alarma_activada

    if indice_emg + bloque_emg >= len(emg):
        return

    if indice_ecg + bloque_ecg >= len(ecg_filtrado):
        return

   
    # BLOQUE ACTUAL
    

    emg_seg = emg[indice_emg:indice_emg + bloque_emg]
    ecg_seg = ecg_filtrado[indice_ecg:indice_ecg + bloque_ecg]

    tiempo_actual = t_emg[indice_emg]

   
    # MDF CON STFT
    

    mdf = calcular_mdf_stft(emg_seg, Fs_emg)

    mdf_hist.append(mdf)
    tiempo_mdf.append(tiempo_actual)

   
    # BPM
    

    peaks, _ = find_peaks(
        ecg_seg,
        distance=int(0.4 * Fs_ecg),
        prominence=np.std(ecg_seg)
    )

    bpm = 0

    if len(peaks) >= 2:
        rr = np.diff(peaks) / Fs_ecg
        bpm = np.mean(60 / rr)

    bpm_hist.append(bpm)
    tiempo_bpm.append(tiempo_actual)

    
    # REFERENCIAS
    

    if len(mdf_hist) == 5:
        MDF_ref = np.mean(mdf_hist)

    if len(bpm_hist) == 5:
        BPM_ref = np.mean(bpm_hist)

    
    # FATIGA
    

    caida = 0

    if MDF_ref is not None and MDF_ref != 0:
        caida = (MDF_ref - mdf) / MDF_ref * 100

    fatiga = False

    if MDF_ref is not None and BPM_ref is not None:

        if caida > 20 and bpm > BPM_ref + 10:
            fatiga = True

    
    # ALERTA
    

    if fatiga:

        lbl_estado.config(
            text="¡FATIGA MUSCULAR DETECTADA!",
            bg="red"
        )

        if not alarma_activada:
            winsound.Beep(1500, 1000)
            alarma_activada = True

    else:

        lbl_estado.config(
            text="NORMAL",
            bg="green"
        )

        alarma_activada = False

    
    # LABELS
   

    lbl_mdf.config(
        text=f"MDF STFT: {mdf:.2f} Hz"
    )

    lbl_bpm.config(
        text=f"BPM: {bpm:.1f}"
    )

    lbl_caida.config(
        text=f"Caída MDF: {caida:.1f} %"
    )

  

    ax1.clear()
    ax1.plot(
        t_emg[:indice_emg + bloque_emg],
        emg[:indice_emg + bloque_emg]
    )
    ax1.set_title("EMG")
    ax1.set_ylabel("ADC")

    ax2.clear()
    ax2.plot(
        t_ecg[:indice_ecg + bloque_ecg],
        ecg[:indice_ecg + bloque_ecg]
    )
    ax2.set_title("ECG")
    ax2.set_ylabel("ADC")

    ax3.clear()
    ax3.plot(
        tiempo_mdf,
        mdf_hist,
        "b"
    )
    ax3.set_title("MDF calculada con STFT")
    ax3.set_ylabel("Hz")

    ax4.clear()
    ax4.plot(
        tiempo_bpm,
        bpm_hist,
        "r"
    )
    ax4.set_title("BPM")
    ax4.set_ylabel("Lat/min")
    ax4.set_xlabel("Tiempo (s)")

    fig.tight_layout()
    canvas.draw()

    indice_emg += bloque_emg
    indice_ecg += bloque_ecg

    ventana.after(
        1000,
        actualizar
    )



actualizar()

ventana.mainloop()