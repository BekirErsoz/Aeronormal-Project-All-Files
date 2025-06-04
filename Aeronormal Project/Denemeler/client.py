import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import threading
import time

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone (İstemci)")
        self.root.geometry("600x400")

        self.text_area = scrolledtext.ScrolledText(self.root, height=15, width=70, wrap=tk.WORD, bg="light green")
        self.text_area.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Bağlantıyı Başlat", command=self.start_client)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Bağlantıyı Durdur", command=self.stop_client)
        self.stop_button.pack(pady=10)

        self.client = None
        self.client_thread = None
        self.is_running = False

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.root.update()

    def send_messages(self):
        while self.is_running:
            try:
                message = "Drone'dan veri gönderiliyor"
                self.client.send(message.encode('utf-8'))
                response = self.client.recv(4096).decode('utf-8')
                self.log_message(f"Sunucudan yanıt: {response}")
                time.sleep(2)  # 2 saniyede bir veri gönderimi
            except Exception as e:
                self.log_message(f"Sunucu hatası: {e}")
                break

    def start_client(self):
        if self.is_running:
            return
        self.is_running = True
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(("127.0.0.1", 9999))
            self.log_message("Sunucuya bağlanıldı.")
            self.client_thread = threading.Thread(target=self.send_messages)
            self.client_thread.start()
        except Exception as e:
            self.log_message(f"Bağlantı hatası: {e}")
            self.is_running = False

    def stop_client(self):
        self.is_running = False
        if self.client:
            self.client.close()
            self.log_message("Bağlantı durduruldu.")
        if self.client_thread:
            self.client_thread.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()