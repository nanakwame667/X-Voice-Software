import os
import subprocess
import time
import wave

import pyaudio
from audio_detector.base.detector import AudioClassifier
from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
classifier = AudioClassifier()
classifier.load("C:/Users/NANAKAY/Desktop/Desktop/Folders/Flask_Project/audio_detector/base/models/model.pkl")
app.config['WAVE_UPLOADS'] = "C:/Users/NANAKAY/Desktop/Desktop/Folders/Flask_Project/static/waves/"

chunk = 1024
FORMAT = pyaudio.paInt16
channels = 1
sample_rate = 44100
record_seconds = 3


@app.route("/", methods=['GET', 'POST'])
def home():

    return render_template("home.html", prediction=None)


@app.route('/record', methods=['POST'])
def recorder():
    filename = f"recorded{time.time()}.wav"
    file_path = os.path.join(app.config['WAVE_UPLOADS'], filename)

    if request.method == 'POST':
        p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)
    frames = []
    print("Recording...")
    for i in range(int(44100 / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(file_path, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()
    # prediction

    print('predicting')
    result = classifier.predict(file_path)
    data = 'Youth' if result[0] == 1 else 'Adult' if result[0] == 2 else 'Senior' if result[0] == 3 else None
    print(f'predicted: {data}')

    return render_template("home.html", prediction=data)

if __name__ == "__main__":
    app.run(debug=True)
