import tkinter as tk
from tkinter import messagebox
import requests

# Halka açık IP adresini alma fonksiyonu
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip_data = response.json()
        return ip_data['ip']
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to get IP address: {e}")
        return None

# Düğmeye basıldığında IP adresini alıp ekranda gösterme fonksiyonu
def show_ip():
    current_ip = get_public_ip()
    if current_ip:
        ip_label.config(text=f"Current Public IP Address: {current_ip}", fg="green")

# Tkinter GUI oluşturma
root = tk.Tk()
root.title("Public IP Address Checker")
root.geometry("400x200")
root.configure(bg="#f0f0f0")

# Başlık etiketi
title_label = tk.Label(root, text="Public IP Address Checker", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

# IP adresini gösteren etiket
ip_label = tk.Label(root, text="Click the button to get your public IP address.", font=("Helvetica", 12), bg="#f0f0f0")
ip_label.pack(pady=20)

# IP adresini alma düğmesi
check_ip_button = tk.Button(root, text="Get IP Address", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                            activebackground="#45a049", padx=10, pady=5, command=show_ip)
check_ip_button.pack(pady=20)

# Ana döngü
root.mainloop()
