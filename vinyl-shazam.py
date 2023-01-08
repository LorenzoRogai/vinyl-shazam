import requests
import pyaudio
import wave
import asyncio
import os
import sox
from shazamio import Shazam, Serialize

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recording.wav"
WAVE_CLEANED_OUTPUT_FILENAME = "recording_cleaned.wav"
HOME_ASSISTANT_ALEXA_WEBHOOK_URL = "https://assistant.home.internal/api/webhook/-cQrazrThINR-8JIO0dGhurYl"

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print("Recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow = False)
    frames.append(data)
print("Finished recording")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

# removing Noise
print("Removing noise")
import sox
tfm = sox.Transformer()
tfm.noisered(profile_path='noise.prof', amount=0.21)
tfm.build(WAVE_OUTPUT_FILENAME, WAVE_CLEANED_OUTPUT_FILENAME)

# calling Shazam and Alexa
async def main():
  print("Calling Shazam")
  shazam = Shazam()
  out = await shazam.recognize_song(WAVE_CLEANED_OUTPUT_FILENAME)

  serialized = Serialize.full_track(out)

  trackTitle = serialized.track.title + ' - ' + serialized.track.subtitle
  print("Found " + trackTitle)

  print("Sending to Alexa")
  requests.post(HOME_ASSISTANT_ALEXA_WEBHOOK_URL, json={"title": trackTitle}, verify = False)

  print("Done")

  os.unlink(WAVE_OUTPUT_FILENAME)
  os.unlink(WAVE_CLEANED_OUTPUT_FILENAME)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())