# Vinyl Song Announcer

Python + Shazam + Alexa (via Home Assistant) to recognize the song currently playing on the turntable and announce its title

The flow is as follows:

* Every 30 seconds a 10 second WAV audio clip is recorded with PyAudio
* The WAV file is passed to the Shazam API which will return the information of the recognized song
* If the song has not been recognized or has already been announced, the program exits otherwise it sends a webhook to Home Assistant with the song title which will then forward it to Alexa for the announcement (only from 18 to 22)
* Done!

## How to

Add the following rule inside your crontab

```
* * * * * /home/vinyl-shazam/frequent-cron.sh "/usr/local/bin/python3.10 /home/vinyl-shazam/vinyl-shazam.py" 30 2 >> /tmp/vinyl-shazam.log
```

## Home Assistant Automation

<img width="1264" alt="image" src="https://user-images.githubusercontent.com/1665768/230989430-5db0e7b3-3d63-4116-9193-db85bbf3b346.png">
