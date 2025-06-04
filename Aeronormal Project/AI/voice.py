import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import speech_recognition as sr
from gtts import gTTS
import playsound
import threading
import os
import webbrowser
from time import strftime

class VoiceCommandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ses Tanıma ve Komut Sistemi")
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.start_button = ttk.Button(self.main_frame, text="Dinlemeye Başla", command=self.start_listening)
        self.start_button.grid(row=0, column=0, pady=10)
        
        self.stop_button = ttk.Button(self.main_frame, text="Dinlemeyi Durdur", command=self.stop_listening, state='disabled')
        self.stop_button.grid(row=0, column=1, pady=10)
        
        self.history_button = ttk.Button(self.main_frame, text="Geçmişi Görüntüle", command=self.show_history)
        self.history_button.grid(row=0, column=2, pady=10)
        
        self.help_button = ttk.Button(self.main_frame, text="Yardım", command=self.show_help)
        self.help_button.grid(row=0, column=3, pady=10)
        
        self.result_label = ttk.Label(self.main_frame, text="Sonuç: -")
        self.result_label.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.history = []
        self.profiles = {"default": {"greeting": "Merhaba, nasıl yardımcı olabilirim?", "commands": {}}}
        self.current_profile = "default"

        self.load_profiles()

    def load_profiles(self):
       
        pass

    def start_listening(self):
        self.listening = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.listening_thread = threading.Thread(target=self.listen)
        self.listening_thread.start()

    def stop_listening(self):
        self.listening = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                print("Dinliyor...")
                audio = self.recognizer.listen(source)
                try:
                    command = self.recognizer.recognize_google(audio, language='tr-TR')
                    print(f"Algılanan komut: {command}")
                    self.result_label.config(text=f"Sonuç: {command}")
                    self.history.append(command)
                    self.execute_command(command)
                except sr.UnknownValueError:
                    print("Ses anlaşılamadı.")
                except sr.RequestError as e:
                    print(f"Google API hatası: {e}")

    def execute_command(self, command):
        lower_command = command.lower()
        if "merhaba" in lower_command:
            self.speak(self.profiles[self.current_profile]["greeting"])
        elif "saati söyle" in lower_command:
            self.speak(f"Şu anda saat {strftime('%H:%M')}")
        elif "dosya aç" in lower_command:
            self.open_file()
        elif "web araması yap" in lower_command:
            self.web_search(command)
        else:
            self.speak("Bu komutu anlayamadım.")

    def speak(self, text):
        tts = gTTS(text=text, lang='tr')
        filename = "temp.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            os.system(f'open "{file_path}"')

    def web_search(self, command):
        search_query = command.replace("web araması yap", "").strip()
        if search_query:
            webbrowser.open(f"https://www.google.com/search?q={search_query}")

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Komut Geçmişi")
        history_frame = ttk.Frame(history_window, padding="10")
        history_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        history_listbox = tk.Listbox(history_frame, height=10)
        history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        for i, command in enumerate(self.history):
            history_listbox.insert(tk.END, f"{i+1}. Komut: {command}")

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Komut Yardım Menüsü")
        help_frame = ttk.Frame(help_window, padding="10")
        help_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        help_text = """
        Kullanabileceğiniz komutlar:
        - "Merhaba": Selamlama yanıtı alırsınız.
        - "Saati söyle": Geçerli saati söyler.
        - "Dosya aç": Dosya açma penceresi açılır.
        - "Web araması yap [arama terimi]": Belirtilen terimi Google'da arar.
        """
        
        help_label = ttk.Label(help_frame, text=help_text)
        help_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceCommandApp(root)
    root.mainloop()