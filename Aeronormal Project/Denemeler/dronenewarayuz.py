import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import paramiko
from cryptography.fernet import Fernet
import os

# GUI için Fonksiyonlar
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def encrypt_data(data, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

def send_data(url, data):
    response = requests.post(url, json=data)
    return response

def receive_data(url):
    response = requests.get(url)
    return response

def execute_command_on_server(host, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        ssh.close()
        return output
    except paramiko.SSHException as e:
        return f"SSH Error: {e}"

# GUI penceresi oluşturma
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Veri Yönetim Arayüzü")
        self.root.geometry("700x500")
        self.root.configure(bg='#2c3e50')

        # Stil oluşturma
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TButton', padding=6, relief="flat", background='#e74c3c', foreground='black', font=("Helvetica", 12, "bold"))
        self.style.configure('TLabel', background='#2c3e50', foreground="white", font=("Helvetica", 12))

        # Sekmeler oluşturma
        self.tab_control = ttk.Notebook(root)
        self.encryption_tab = ttk.Frame(self.tab_control)
        self.network_tab = ttk.Frame(self.tab_control)
        self.ssh_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.encryption_tab, text="Şifreleme")
        self.tab_control.add(self.network_tab, text="Ağ İletişimi")
        self.tab_control.add(self.ssh_tab, text="SSH Komutları")
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        # Şifreleme Tabı
        self.create_encryption_tab()

        # Ağ İletişimi Tabı
        self.create_network_tab()

        # SSH Tabı
        self.create_ssh_tab()

    def create_encryption_tab(self):
        ttk.Label(self.encryption_tab, text="Şifrele ve Çöz:", font=("Helvetica", 14, "bold")).pack(pady=10)

        frame = ttk.Frame(self.encryption_tab, padding="10")
        frame.pack(padx=10, pady=10, fill="x", expand=True)
        
        ttk.Label(frame, text="Veri:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")
        self.data_entry = ttk.Entry(frame, width=60, font=("Helvetica", 12))
        self.data_entry.grid(row=0, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Şifrele", command=self.encrypt).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Çöz", command=self.decrypt).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Sonuç:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.result_text = scrolledtext.ScrolledText(frame, height=10, width=80, wrap=tk.WORD, font=("Helvetica", 12), bg='#ecf0f1')
        self.result_text.grid(row=2, column=1, pady=5)

    def create_network_tab(self):
        ttk.Label(self.network_tab, text="Sunucu URL:", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        frame = ttk.Frame(self.network_tab, padding="10")
        frame.pack(padx=10, pady=10, fill="x", expand=True)
        
        ttk.Label(frame, text="URL:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(frame, width=60, font=("Helvetica", 12))
        self.url_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Veri Gönder:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.send_data_entry = ttk.Entry(frame, width=60, font=("Helvetica", 12))
        self.send_data_entry.grid(row=1, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Veri Gönder", command=self.send_data).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Veri Al", command=self.receive_data).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Yanıt:", font=("Helvetica", 12)).grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.response_text = scrolledtext.ScrolledText(frame, height=10, width=80, wrap=tk.WORD, font=("Helvetica", 12), bg='#ecf0f1')
        self.response_text.grid(row=3, column=1, pady=5)
        
    def create_ssh_tab(self):
        ttk.Label(self.ssh_tab, text="SSH Komutları:", font=("Helvetica", 14, "bold")).pack(pady=10)
    
        frame = ttk.Frame(self.ssh_tab, padding="10")
        frame.pack(padx=10, pady=10, fill="x", expand=True)

        ttk.Label(frame, text="Sunucu IP:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w")
        self.ssh_ip_entry = ttk.Entry(frame, width=60, font=("Helvetica", 12))
        self.ssh_ip_entry.grid(row=0, column=1, pady=5)
    
        ttk.Label(frame, text="Port:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.ssh_port_entry = ttk.Entry(frame, width=60, font=("Helvetica", 12))
        self.ssh_port_entry.grid(row=1, column=1, pady=5)
    
        ttk.Label(frame, text="Kullanıcı Adı:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.ssh_user_entry = ttk.Entry(frame, width=60, font=("Helvetica", 12))
        self.ssh_user_entry.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Şifre:", font=("Helvetica", 12)).grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.ssh_password_entry = ttk.Entry(frame, show="*", width=60, font=("Helvetica", 12))
        self.ssh_password_entry.grid(row=3, column=1, pady=5)

        ttk.Label(frame, text="Komut:", font=("Helvetica", 12)).grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.ssh_command_entry = ttk.Entry(frame, width=60, font=("Helvetica", 12))
        self.ssh_command_entry.grid(row=4, column=1, pady=5)

        ttk.Button(frame, text="Komut Çalıştır", command=self.execute_ssh_command).grid(row=5, column=0, columnspan=2, pady=10)
        self.ssh_output_text = scrolledtext.ScrolledText(frame, height=10, width=80, wrap=tk.WORD, font=("Helvetica", 12), bg='#ecf0f1')
        self.ssh_output_text.grid(row=6, column=0, columnspan=2, pady=10)

    def encrypt(self):
        key = load_key()
        data = self.data_entry.get()
        encrypted_data = encrypt_data(data, key)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, encrypted_data.decode())

    def decrypt(self):
        key = load_key()
        encrypted_data = self.result_text.get(1.0, tk.END).strip()
        decrypted_data = decrypt_data(encrypted_data.encode(), key)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, decrypted_data)

    def send_data(self):
        url = self.url_entry.get()
        data = self.send_data_entry.get()
        response = send_data(url, {'data': data})
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, response.text)

    def receive_data(self):
        url = self.url_entry.get()
        response = receive_data(url)
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, response.text)

    def execute_ssh_command(self):
        host = self.ssh_ip_entry.get()
        port = int(self.ssh_port_entry.get())
        username = self.ssh_user_entry.get()
        password = self.ssh_password_entry.get()
        command = self.ssh_command_entry.get()
        output = execute_command_on_server(host, port, username, password, command)
        self.ssh_output_text.delete(1.0, tk.END)
        self.ssh_output_text.insert(tk.END, output)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
