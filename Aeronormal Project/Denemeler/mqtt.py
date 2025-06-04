import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import scrolledtext

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kontrol Cihazı (Sunucu)")
        self.root.geometry("600x500")
        self.root.config(bg="#2c3e50")

        self.text_area = scrolledtext.ScrolledText(self.root, height=15, width=70, wrap=tk.WORD, bg="#ecf0f1", font=("Arial", 12))
        self.text_area.pack(pady=10)

        self.button_frame = tk.Frame(self.root, bg="#2c3e50")
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Sunucuyu Başlat", command=self.start_server, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.start_button.grid(row=0, column=0, padx=10, pady=5)

        self.stop_button = tk.Button(self.button_frame, text="Bağlantıyı Durdur", command=self.stop_server, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.stop_button.grid(row=0, column=1, padx=10, pady=5)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.root.update()

    def on_connect(self, client, userdata, flags, rc):
        self.log_message("Sunucu MQTT Broker'a bağlandı")
        client.subscribe("drone/messages")

    def on_message(self, client, userdata, msg):
        self.log_message(f"Gelen mesaj: {msg.payload.decode()}")

    def start_server(self):
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()
        self.log_message("Sunucu başlatıldı. MQTT Broker'a bağlanılıyor...")

    def stop_server(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.log_message("Sunucu durduruldu.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()