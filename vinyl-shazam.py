import requests
import pyaudio
import wave
import asyncio
import os
import datetime
from shazamio import Shazam, Serialize

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "/tmp/recording.wav"
TRACK_TITLE_FILENAME = "/tmp/track-title.txt"
HOME_ASSISTANT_ALEXA_WEBHOOK_URL = "https://assistant.home.internal/api/webhook/-cQrazrThINR-8JIO0dGhurYl"
INPUT_DEVICE_INDEX = 6

# check Date
now = datetime.datetime.now()
hour = now.hour

if hour not in range(18, 22):
  quit()

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK,
                input_device_index=INPUT_DEVICE_INDEX)
print("Recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
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

# calling Shazam and Alexa
async def main():
  print("Calling Shazam")
  shazam = Shazam()
  out = await shazam.recognize_song(WAVE_OUTPUT_FILENAME)

  serialized = Serialize.full_track(out)

  if serialized.track is not None:
    trackTitle = serialized.track.title + ' di ' + serialized.track.subtitle
    print("Found " + trackTitle)

    previousTrackTitle = ""

    if os.path.exists(TRACK_TITLE_FILENAME):
        f = open(TRACK_TITLE_FILENAME, "r")
        previousTrackTitle = f.read()

    if trackTitle != previousTrackTitle:
        print("Sending to Alexa")
        requests.post(HOME_ASSISTANT_ALEXA_WEBHOOK_URL, json={"title": trackTitle}, verify=False)

        f = open(TRACK_TITLE_FILENAME, "w")
        f.write(trackTitle)
        f.close()

        print("Done")
    else:
        print("Quitting because the song was already announced")
  else:
    print("Quitting because the song was not recognized")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())