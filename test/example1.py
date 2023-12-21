from pydub import AudioSegment
from pydub.playback import play
import requests
from io import BytesIO
import time

# Adres URL strumienia radiowego
stream_url = "https://msmn2.co/proxy/mp3high11/stream"

# Pobranie strumienia audio
response = requests.get(stream_url, stream=True)
audio_stream = BytesIO(response.content)

# Konwersja strumienia audio na format obsługiwany przez pydub
audio = AudioSegment.from_file(audio_stream)

# Odtwarzanie strumienia
play(audio)

# Poczekaj, aż użytkownik zdecyduje się zakończyć program
time.sleep(30)  # Na przykład, odtwarzaj przez 30 sekund
