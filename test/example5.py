import subprocess

stream_url = "https://msmn2.co/proxy/mp3high11/stream"

# Wywołanie ffprobe i pobranie wyników jako ciąg bajtów
result = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,channels,channel_layout,sample_rate", "-of", "default=noprint_wrappers=1", stream_url],
    capture_output=True
)

# Dekodowanie wyników do postaci łańcucha tekstowego (UTF-8)
output = result.stdout.decode("utf-8")

# Wyświetlenie informacji o formacie strumienia
print(output)
