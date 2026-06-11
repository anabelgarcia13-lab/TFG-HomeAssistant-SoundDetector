import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import queue
import time
import csv
import sounddevice as sd
from scipy.io.wavfile import write, read

#configuración
SAMPLE_RATE = 16000
BUFFER_DURATION = 1  #segundos
THRESHOLD = 0.02

TARGET_SOUNDS = [
    "Glass",
    "Clink",
    "Bang",
    "Chink",
    "Knock",
    "Impact"
]

#cargar modelo YAMNet
print("Cargando YAMNet...")
model = hub.load("https://tfhub.dev/google/yamnet/1")

class_map_path = model.class_map_path().numpy()

class_names = []

for i, name in enumerate(class_names):
    if "glass" in name.lower():
        print(i, name)

keywords = ["glass", "break", "shatter", "smash", "crash", "impact"]

for keyword in keywords:
    print(f"\n--- {keyword} ---")
    for i, name in enumerate(class_names):
        if keyword.lower() in name.lower():
            print(i, name)

glass_classes = [name for name in class_names if "glass" in name.lower()]
print(glass_classes)

with open(class_map_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        class_names.append(row["display_name"])

print("Modelo cargado")

#recibe el audio del micrófono y lo almacena
audio_queue = queue.Queue()

def save_buffer_to_wav(buffer, filename="audio.wav"):
    # Convertir a int16
    audio_int16 = np.int16(buffer * 32767)
    write(filename, SAMPLE_RATE, audio_int16)


def load_wav(filename):
    sr, audio = read(filename)

    # Convertir a float32
    audio = audio.astype(np.float32)

    # Si es int16, normalizar
    if np.max(np.abs(audio)) > 1:
        audio /= 32768.0

    # Si es estéreo, quedarse con un canal
    if len(audio.shape) > 1:
        audio = audio[:,0]

    return audio

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    #si entran varios canales, nos quedamos solo con el primero
    if indata.shape[1] > 1:
        audio_queue.put(indata[:, 0:1].copy())
    else:
        audio_queue.put(indata.copy())

#se envía el audio a YAMNet y se clasifica en las categorías detectadas
def detect_sound(audio):
    scores, embeddings, spectrogram = model(audio)
    scores = scores.numpy()
    mean_scores = np.mean(scores, axis=0)

    results = []

    for i, score in enumerate(mean_scores):
        results.append((class_names[i], score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:10]


#procesar continuamente el audio capturado
def process_audio():
    #crear buffer de audio
    buffer = np.zeros(int(SAMPLE_RATE * BUFFER_DURATION))

    while True:
        #obtener la cola de audio
        data = audio_queue.get()
        data = np.squeeze(data)

        #desplazar el buffer eliminando las muestras más antiguas para hacer espacio a las nuevas
        buffer = np.roll(buffer, -len(data))
        buffer[-len(data):] = data

        #mostrar estadísticas de la señal
        print(
            f"min={np.min(buffer):.4f} "
            f"max={np.max(buffer):.4f} "
            f"mean={np.mean(np.abs(buffer)):.4f}"
        )

        #clasificar el audio
        save_buffer_to_wav(buffer)

        audio = load_wav("audio.wav")

        results = detect_sound(audio)

        print("-----")
        #mostrar las 20 primeras clases detectadas

        for label, score in results:
            if label in ["Glass", "Chink, clink", "Shatter", "Smash, crash", "Breaking"]:
                print(f"{label}: {score:.4f}")

        #for label, score in results[:20]:
         #   print(f"{label}: {score:.2f}")

          #  if label in TARGET_SOUNDS:
           #         print(f"ALERTA: {label} ({score:.2f})")

        time.sleep(0.01)

#main
print(" Escuchando 24/7...")

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    callback=audio_callback,
    blocksize=int(SAMPLE_RATE * 0.5),
    device=1
):
    process_audio()




#guardar audio en ficheros .wav y aumentar el intervalo
#crear diagrama de cómo es el proceso para ponerlo como imagen en la memoria