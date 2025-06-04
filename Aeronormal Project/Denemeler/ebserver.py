import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kontrol Cihazı (Sunucu)")
        self.root.geometry("600x500")
        self.root.config(bg="lightgray")

        self.text_area = scrolledtext.ScrolledText(self.root, height=15, width=70, wrap=tk.WORD, bg="white", font=("Arial", 10))
        self.text_area.pack(pady=10)

        self.button_frame = tk.Frame(self.root, bg="lightgray")
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Sunucuyu Başlat", command=self.start_server, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(self.button_frame, text="Bağlantıyı Durdur", command=self.stop_server, bg="red", fg="white", font=("Arial", 12, "bold"))
        self.stop_button.grid(row=0, column=1, padx=10)

        self.server = None
        self.server_thread = None
        self.is_running = False

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.root.update()

    def handle_client(self, client_socket):
        while self.is_running:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                self.log_message(f"Gelen mesaj: {message}")
                client_socket.send("Mesaj alındı".encode('utf-8'))
            except Exception as e:
                self.log_message(f"İstemci hatası: {e}")
                break
        client_socket.close()

    def start_server(self):
        if self.is_running:
            return
        self.is_running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 9999))
        self.server.listen(5)
        self.log_message("Sunucu başlatıldı. Bağlantı bekleniyor...")

        def accept_clients():
            while self.is_running:
                try:
                    client_socket, addr = self.server.accept()
                    self.log_message(f"Bağlantı kabul edildi: {addr}")
                    client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_handler.start()
                except Exception as e:
                    self.log_message(f"Sunucu hatası: {e}")
                    break

        self.server_thread = threading.Thread(target=accept_clients)
        self.server_thread.start()

    def stop_server(self):
        self.is_running = False
        if self.server:
            self.server.close()
            self.log_message("Sunucu durduruldu.")
        if self.server_thread:
            self.server_thread.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()