import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import scrolledtext

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone (İstemci)")
        self.root.geometry("600x500")
        self.root.config(bg="#34495e")

        self.text_area = scrolledtext.ScrolledText(self.root, height=15, width=70, wrap=tk.WORD, bg="#ecf0f1", font=("Arial", 12))
        self.text_area.pack(pady=10)

        self.message_entry = tk.Entry(self.root, width=50, font=("Arial", 14))
        self.message_entry.pack(pady=10)

        self.button_frame = tk.Frame(self.root, bg="#34495e")
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Bağlantıyı Başlat", command=self.start_client, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.start_button.grid(row=0, column=0, padx=10, pady=5)

        self.stop_button = tk.Button(self.button_frame, text="Bağlantıyı Durdur", command=self.stop_client, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.stop_button.grid(row=0, column=1, padx=10, pady=5)

        self.send_button = tk.Button(self.button_frame, text="Mesaj Gönder", command=self.send_message, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.send_button.grid(row=0, column=2, padx=10, pady=5)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.root.update()

    def on_connect(self, client, userdata, flags, rc):
        self.log_message("İstemci MQTT Broker'a bağlandı")
        client.subscribe("server/messages")

    def on_message(self, client, userdata, msg):
        self.log_message(f"Sunucudan gelen mesaj: {msg.payload.decode()}")

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.client.publish("drone/messages", message)
            self.log_message(f"Gönderilen mesaj: {message}")

    def start_client(self):
        self.client.connect("broker.hivemq.com", 1883, 60)
        self.client.loop_start()
        self.log_message("İstemci başlatıldı. MQTT Broker'a bağlanılıyor...")

    def stop_client(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.log_message("İstemci durduruldu.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()