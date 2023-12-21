import sounddevice as sd
import numpy as np
import requests
from io import BytesIO
import time

# Adres URL strumienia radiowego
stream_url = "https://msmn2.co/proxy/mp3high11/stream"

# Pobranie strumienia audio
response = requests.get(stream_url, stream=True)
audio_stream = BytesIO(response.content)

# Odczytanie danych audio
audio_data, sample_rate = sd.read(audio_stream)

# Odtworzenie strumienia audio
sd.play(audio_data, sample_rate)
sd.wait()

# Poczekaj, aż użytkownik zdecyduje się zakończyć program
time.sleep(30)  # Na przykład, odtwarzaj przez 30 sekund
