import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

# Anahtar oluşturma ve yükleme
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

# Anahtar oluşturma veya yükleme
try:
    key = load_key()
except FileNotFoundError:
    generate_key()
    key = load_key()

fernet = Fernet(key)

# Şifreleme işlemi
def encrypt_data():
    user_input = entry.get()
    if user_input:
        encrypted_message = fernet.encrypt(user_input.encode()).decode()
        result_label.config(text=f"Encrypted Message: {encrypted_message}", fg="green")
    else:
        messagebox.showwarning("Input Error", "Please enter some text to encrypt.")

# Tkinter GUI oluşturma
root = tk.Tk()
root.title("Data Encryption Tool")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Başlık etiketi
title_label = tk.Label(root, text="Data Encryption Tool", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

# Giriş alanı etiketi ve giriş kutusu
input_label = tk.Label(root, text="Enter text to encrypt:", font=("Helvetica", 12), bg="#f0f0f0")
input_label.pack(pady=5)
entry = tk.Entry(root, width=40, font=("Helvetica", 12), borderwidth=2, relief="groove")
entry.pack(pady=5)

# Şifreleme düğmesi
encrypt_button = tk.Button(root, text="Encrypt", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                           activebackground="#45a049", padx=10, pady=5, command=encrypt_data)
encrypt_button.pack(pady=20)

# Sonuç etiketi
result_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f0f0")
result_label.pack(pady=10)

# Ana döngü
root.mainloop()
