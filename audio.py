import tkinter as tk
from tkinter import filedialog
import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


class AudioEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Editor")

        self.record_button = tk.Button(root, text="Grabar", command=self.record_audio)
        self.record_button.pack()

        self.play_button = tk.Button(root, text="Reproducir", command=self.play_audio)
        self.play_button.pack()

        self.trim_button = tk.Button(root, text="Eliminar Silencio", command=self.remove_silence)
        self.trim_button.pack()



        self.canvas = tk.Canvas(root, width=800, height=200)
        self.canvas.pack()

        self.figure, self.ax = plt.subplots()
        self.canvas_fig = FigureCanvasTkAgg(self.figure, master=self.canvas)
        self.canvas_fig.get_tk_widget().pack()

        self.filename = "output.wav"
        self.audio = None
        self.start = None
        self.end = None
        self.selection_rect = None

    def record_audio(self):
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100
        duration = 5

        p = pyaudio.PyAudio()

        print("Recording...")

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []

        for _ in range(0, int(fs / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        print("Recording finished.")

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.load_audio()

    def play_audio(self):
        wf = wave.open(self.filename, 'rb')

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        chunk = 1024
        data = wf.readframes(chunk)

        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def remove_silence(self):
        audio = AudioSegment.from_wav(self.filename)
        non_silence = detect_nonsilent(audio, min_silence_len=500, silence_thresh=audio.dBFS - 16)
        start_trim = non_silence[0][0]
        end_trim = non_silence[-1][1]
        trimmed_audio = audio[start_trim:end_trim]
        trimmed_audio.export(self.filename, format='wav')

        self.load_audio()

    def load_audio(self):
        self.audio = AudioSegment.from_wav(self.filename)
        samples = np.array(self.audio.get_array_of_samples())
        self.plot_waveform(samples)

    def plot_waveform(self, samples):
        self.ax.clear()
        self.ax.plot(samples)
        self.canvas_fig.draw()

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEditor(root)
    root.mainloop()
