import tkinter as tk
from tkinter import filedialog
import pygame

# Pygame başlatma
pygame.mixer.init()

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Music Player")
        self.root.geometry("300x200")

        # Müzik dosyası yolu
        self.music_file = None

        # Kullanıcı arayüzü elemanları
        self.load_button = tk.Button(self.root, text="Load Music", command=self.load_music)
        self.load_button.pack(pady=10)

        self.play_button = tk.Button(self.root, text="Play", command=self.play_music)
        self.play_button.pack(pady=10)

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_music)
        self.pause_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_music)
        self.stop_button.pack(pady=10)

    def load_music(self):
        self.music_file = filedialog.askopenfilename()
        if self.music_file:
            pygame.mixer.music.load(self.music_file)

    def play_music(self):
        if self.music_file:
            pygame.mixer.music.play()

    def pause_music(self):
        if self.music_file:
            pygame.mixer.music.pause()

    def stop_music(self):
        if self.music_file:
            pygame.mixer.music.stop()

# Tkinter ana döngüsü
root = tk.Tk()
app = MusicPlayer(root)
root.mainloop()