import tkinter as tk
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
import requests
import json
import os

# Şifreleme anahtarı oluşturma ve yükleme
def generate_key():
    """Yeni bir şifreleme anahtarı oluşturur ve dosyaya kaydeder."""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """Mevcut şifreleme anahtarını dosyadan yükler."""
    return open("secret.key", "rb").read()

# Anahtar oluşturma veya yükleme işlemi
try:
    key = load_key()
except FileNotFoundError:
    generate_key()
    key = load_key()

fernet = Fernet(key)

# Şifreleme fonksiyonu
def encrypt_data():
    """Kullanıcıdan alınan veriyi şifreler ve ekranda gösterir."""
    user_input = entry.get()
    if user_input:
        encrypted_message = fernet.encrypt(user_input.encode()).decode()
        result_label.config(text=f"Encrypted Message: {encrypted_message}", foreground="green")
    else:
        messagebox.showwarning("Input Error", "Please enter some text to encrypt.")

# Halka açık IP adresini alma fonksiyonu
def get_public_ip():
    """Kullanıcının halka açık IP adresini API üzerinden alır."""
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip_data = response.json()
        return ip_data['ip']
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to get IP address: {e}")
        return None

# Düğmeye basıldığında IP adresini alıp ekranda gösterme fonksiyonu
def show_ip():
    """Halka açık IP adresini alır ve ekranda gösterir."""
    current_ip = get_public_ip()
    if current_ip:
        ip_label.config(text=f"Current Public IP Address: {current_ip}", foreground="green")

# API istemcisi işlevleri
class APIClientApp:
    def __init__(self, tab):
        self.tab = tab
        self.create_widgets()

    def create_widgets(self):
        """API istemcisi için gerekli arayüz bileşenlerini oluşturur."""
        # Başlık etiketi
        self.title_label = tk.Label(self.tab, text="Flask API Client", font=("Helvetica", 18, "bold"), bg="#2b2b2b", fg="#ffffff")
        self.title_label.pack(pady=20)

        # Veri gönderme için etiket ve giriş alanı
        self.data_label = tk.Label(self.tab, text="Enter text to send:", font=("Helvetica", 12), bg="#2b2b2b", fg="#ffffff")
        self.data_label.pack(pady=5)
        
        self.data_entry = tk.Entry(self.tab, width=50, font=("Helvetica", 12), bd=2, relief="solid")
        self.data_entry.pack(pady=5)

        # POST isteği için buton
        self.post_button = tk.Button(self.tab, text="Send POST Request", command=self.send_post_request, font=("Helvetica", 12, "bold"), bg="#007acc", fg="#ffffff", relief="raised", bd=2)
        self.post_button.pack(pady=10)

        # GET isteği için buton
        self.get_button = tk.Button(self.tab, text="Send GET Request", command=self.send_get_request, font=("Helvetica", 12, "bold"), bg="#007acc", fg="#ffffff", relief="raised", bd=2)
        self.get_button.pack(pady=10)

        # Sonuçları göstermek için etiket
        self.result_label = tk.Label(self.tab, text="", font=("Helvetica", 12), bg="#2b2b2b", fg="#ffffff")
        self.result_label.pack(pady=20)

    def send_post_request(self):
        """POST isteği gönderir ve yanıtı ekranda gösterir."""
        data = self.data_entry.get()
        try:
            response = requests.post("http://127.0.0.1:5001/api/", json={"encrypted_message": data})
            response.raise_for_status()
            result = response.json()
            self.result_label.config(text=f"POST Response: {json.dumps(result, indent=2)}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to send POST request: {e}")

    def send_get_request(self):
        """GET isteği gönderir ve yanıtı ekranda gösterir."""
        try:
            response = requests.get("http://127.0.0.1:5001/api/")
            response.raise_for_status()
            result = response.json()
            self.result_label.config(text=f"GET Response: {json.dumps(result, indent=2)}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to send GET request: {e}")

# Tkinter GUI oluşturma
root = tk.Tk()
root.title("Tool Suite")
root.geometry("600x500")
root.configure(bg="#1e1e1e")

# Sekmeler oluşturma
tab_control = ttk.Notebook(root)
encryption_tab = ttk.Frame(tab_control, style="TFrame")
ip_tab = ttk.Frame(tab_control, style="TFrame")
api_tab = ttk.Frame(tab_control, style="TFrame")

tab_control.add(encryption_tab, text="Encryption")
tab_control.add(ip_tab, text="IP Checker")
tab_control.add(api_tab, text="API Client")
tab_control.pack(expand=1, fill="both", padx=10, pady=10)

# Stil ayarları
style = ttk.Style()
style.theme_use("clam")
style.configure('TFrame', background="#2b2b2b")
style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=10, background="#007acc", foreground="#ffffff", relief="raised")
style.configure('TLabel', background="#2b2b2b", foreground="#ffffff", font=('Helvetica', 12))

# Şifreleme Tabı
def create_encryption_tab():
    """Şifreleme sekmesini oluşturur."""
    ttk.Label(encryption_tab, text="Data Encryption Tool", font=("Helvetica", 18, "bold"), background="#2b2b2b", foreground="#ffffff").pack(pady=20)
    
    frame = ttk.Frame(encryption_tab, padding="10")
    frame.pack(padx=10, pady=10, fill="x", expand=True)
    
    ttk.Label(frame, text="Enter text to encrypt:", font=("Helvetica", 12), background="#2b2b2b", foreground="#ffffff").grid(row=0, column=0, sticky="w")
    
    global entry
    entry = tk.Entry(frame, width=40, font=("Helvetica", 12), bd=2, relief="solid")
    entry.grid(row=0, column=1, pady=5)
    
    ttk.Button(frame, text="Encrypt", command=encrypt_data, style="TButton").grid(row=1, column=0, columnspan=2, pady=20)
    
    global result_label
    result_label = ttk.Label(frame, text="", font=("Helvetica", 12), background="#2b2b2b", foreground="#ffffff")
    result_label.grid(row=2, column=0, columnspan=2, pady=10)

# IP Checker Tabı
def create_ip_tab():
    """IP kontrol sekmesini oluşturur."""
    ttk.Label(ip_tab, text="Public IP Address Checker", font=("Helvetica", 18, "bold"), background="#2b2b2b", foreground="#ffffff").pack(pady=20)
    
    frame = ttk.Frame(ip_tab, padding="10")
    frame.pack(padx=10, pady=10, fill="x", expand=True)
    
    global ip_label
    ip_label = ttk.Label(frame, text="Click the button to get your public IP address.", font=("Helvetica", 12), background="#2b2b2b", foreground="#ffffff")
    ip_label.pack(pady=20)
    
    ttk.Button(frame, text="Get IP Address", command=show_ip, style="TButton").pack(pady=20)

# API Client Tabı
api_client_app = APIClientApp(api_tab)

# Sekmeleri oluştur
create_encryption_tab()
create_ip_tab()

# Ana döngü
root.mainloop()
