import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import queue
import time
import csv
import sounddevice as sd
from scipy.io.wavfile import write
import json

JSON_FILE = r"C:\TFG\shared\sound_detector.json"

def guardar_resultado(sound, confidence):

    datos = {
        "sound": sound,
        "confidence": float(confidence),
        "timestamp": time.time()
    }

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)


#configuración
SAMPLE_RATE = 16000
BUFFER_DURATION = 3  #segundos
BLOCK_DURATION = 0.5
THRESHOLD = 0.02

EVENTS = {
    "Silence": [
        "silence"
    ],

    "Speech": [
        "speech",
        "narration",
        "monologue",
        "conversation",
        "child speech",
        "whispering"
    ],

    "Glass Break": [
        "glass",
        "shatter",
        "smash",
        "break",
        "crash",
        "clink"
    ],

    "Doorbell": [
        "doorbell",
        "ding-dong",
        "ding",
        "bell",
        "chime",
        "ringtone",
        "knock",
        "bang"
    ],

    "Dog Bark": [
        "dog",
        "bark",
        "whimper",
        "yip"
    ],

    "Baby Cry": [
        "baby cry",
        "crying",
        "sobbing",
        "wail"
    ],

    "Alarm": [
        "alarm",
        "siren",
        "buzzer"
    ]
}

print(EVENTS.keys())


#cargar modelo YAMNet
print("Cargando YAMNet...")
model = hub.load("https://tfhub.dev/google/yamnet/1")

class_map_path = model.class_map_path().numpy()

blocksize = int(SAMPLE_RATE * BLOCK_DURATION)


class_names = []

with open(class_map_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        class_names.append(row["display_name"])

print("Modelo cargado")

#recibe el audio del micrófono y lo almacena
audio_queue = queue.Queue()

sd.query_devices()

def save_buffer_to_wav(buffer, filename="audio.wav"):
    # Convertir a int16
    audio_int16 = np.int16(buffer * 32767)
    write(filename, SAMPLE_RATE, audio_int16)


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
    scores, embeddings, spectogram = model(audio)
    scores = scores.numpy()
    mean_scores = 0.5*np.mean(scores, axis=0) + 0.5*np.max(scores, axis=0)

    results = []

    for i, score in enumerate(mean_scores):
        results.append((class_names[i], score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


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
        audio = buffer.astype(np.float32)

        results = detect_sound(audio)

        event_scores = {}

        for event, words in EVENTS.items():

            best_score = 0

            for label, value in results:
                if any(w in label.lower() for w in words):
                    best_score = max(best_score, value)

            event_scores[event] = best_score


        print("-----")

        print("\nEventos detectados")

        for e, s in event_scores.items():
            print(f"{e}: {s:.4f}")

        best_event = max(event_scores, key=event_scores.get)

        if event_scores[best_event] > THRESHOLD:
            guardar_resultado(best_event, event_scores[best_event])
        else:
            guardar_resultado(results[0][0], results[0][1])


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

