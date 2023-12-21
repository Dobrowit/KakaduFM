import pyaudio
import requests
from io import BytesIO
import time

# Adres URL strumienia radiowego
stream_url = "https://msmn2.co/proxy/mp3high11/stream"

# Pobranie strumienia audio
response = requests.get(stream_url, stream=True)
audio_stream = BytesIO(response.content)

# Konfiguracja parametrów audio
chunk_size = 1024
sample_format = pyaudio.paInt16
channels = 2
sample_rate = 44100

# Inicjalizacja obiektu PyAudio
p = pyaudio.PyAudio()

# Otwarcie strumienia audio
stream = p.open(format=sample_format,
                channels=channels,
                rate=sample_rate,
                output=True)

# Odczytanie i odtworzenie strumienia audio
data = audio_stream.read(chunk_size)
while data:
    stream.write(data)
    data = audio_stream.read(chunk_size)

# Zakończenie strumienia i obiektu PyAudio
stream.stop_stream()
stream.close()
p.terminate()

# Poczekaj, aż użytkownik zdecyduje się zakończyć program
time.sleep(30)  # Na przykład, odtwarzaj przez 30 sekund
