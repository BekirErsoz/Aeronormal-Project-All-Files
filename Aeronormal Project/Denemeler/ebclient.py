import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone (İstemci)")
        self.root.geometry("600x500")
        self.root.config(bg="lightgray")

        self.text_area = scrolledtext.ScrolledText(self.root, height=15, width=70, wrap=tk.WORD, bg="white", font=("Arial", 10))
        self.text_area.pack(pady=10)

        self.message_entry = tk.Entry(self.root, width=50, font=("Arial", 12))
        self.message_entry.pack(pady=10)

        self.button_frame = tk.Frame(self.root, bg="lightgray")
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Bağlantıyı Başlat", command=self.start_client, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(self.button_frame, text="Bağlantıyı Durdur", command=self.stop_client, bg="red", fg="white", font=("Arial", 12, "bold"))
        self.stop_button.grid(row=0, column=1, padx=10)

        self.send_button = tk.Button(self.button_frame, text="Mesaj Gönder", command=self.send_message, bg="blue", fg="white", font=("Arial", 12, "bold"))
        self.send_button.grid(row=0, column=2, padx=10)

        self.client = None
        self.client_thread = None
        self.is_running = False

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.root.update()

    def send_message(self):
        message = self.message_entry.get()
        if self.is_running and message:
            self.client.send(message.encode('utf-8'))
            self.log_message(f"Gönderilen mesaj: {message}")

    def receive_messages(self):
        while self.is_running:
            try:
                response = self.client.recv(4096).decode('utf-8')
                self.log_message(f"Sunucudan yanıt: {response}")
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
            self.client_thread = threading.Thread(target=self.receive_messages)
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