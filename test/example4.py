import pyglet
import requests
from io import BytesIO
import time

# Adres URL strumienia radiowego
stream_url = "https://msmn2.co/proxy/mp3high11/stream"

# Pobranie strumienia audio
response = requests.get(stream_url, stream=True)
audio_stream = BytesIO(response.content)

# Konfiguracja obiektu pyglet
player = pyglet.media.Player()
source = pyglet.media.load(audio_stream, streaming=True)
player.queue(source)

# Odtwarzanie strumienia audio
player.play()

# Poczekaj, aż użytkownik zdecyduje się zakończyć program
time.sleep(30)  # Na przykład, odtwarzaj przez 30 sekund

# Zakończenie odtwarzania
player.pause()
pyglet.app.exit()
