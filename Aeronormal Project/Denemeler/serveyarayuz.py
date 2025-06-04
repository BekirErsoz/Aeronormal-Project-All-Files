import tkinter as tk
from tkinter import messagebox
import requests
import json

class APIClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flask API Client")
        self.root.geometry("400x300")
        self.root.configure(bg="#f0f0f0")

        self.create_widgets()

    def create_widgets(self):
        # Başlık etiketi
        self.title_label = tk.Label(self.root, text="Flask API Client", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        # Veri gönderme için etiket ve giriş alanı
        self.data_label = tk.Label(self.root, text="Enter text to send:", font=("Helvetica", 12), bg="#f0f0f0")
        self.data_label.pack(pady=5)
        
        self.data_entry = tk.Entry(self.root, width=50)
        self.data_entry.pack(pady=5)

        # POST isteği için buton
        self.post_button = tk.Button(self.root, text="Send POST Request", command=self.send_post_request)
        self.post_button.pack(pady=10)

        # GET isteği için buton
        self.get_button = tk.Button(self.root, text="Send GET Request", command=self.send_get_request)
        self.get_button.pack(pady=10)

        # Sonuçları göstermek için etiket
        self.result_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg="#f0f0f0")
        self.result_label.pack(pady=20)

    def send_post_request(self):
        data = self.data_entry.get()
        try:
            response = requests.post("http://127.0.0.1:5001/api/", json={"encrypted_message": data})
            response.raise_for_status()
            result = response.json()
            self.result_label.config(text=f"POST Response: {json.dumps(result, indent=2)}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to send POST request: {e}")

    def send_get_request(self):
        try:
            response = requests.get("http://127.0.0.1:5001/api/")
            response.raise_for_status()
            result = response.json()
            self.result_label.config(text=f"GET Response: {json.dumps(result, indent=2)}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to send GET request: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = APIClientApp(root)
    root.mainloop()
