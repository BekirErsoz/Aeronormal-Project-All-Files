import tkinter as tk
from tkinter import scrolledtext
import subprocess

class NetworkManager:
    def __init__(self):
        self.connections = []

    def add_connection(self, connection):
        self.connections.append(connection)

    def manage_connections(self):
        for conn in self.connections:
            if not conn.is_active():
                self.reconnect(conn)

    def reconnect(self, connection):
        connection.connect()

class Connection:
    def __init__(self, name):
        self.name = name
        self.active = False

    def connect(self):
        self.active = True
        print(f"{self.name} connected.")

    def is_active(self):
        return self.active

def list_network_devices():
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    devices = []
    for line in lines:
        if 'Internet Address' in line:
            continue
        parts = line.split()
        if len(parts) >= 3:
            devices.append({
                'Internet Address': parts[0],
                'Physical Address': parts[1],
                'Type': parts[2]
            })
    
    return devices

class NetworkSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Manager Simülasyonu")
        self.root.geometry("800x600")
        self.root.config(bg="#34495e")

        self.network_manager = NetworkManager()

        self.text_area = scrolledtext.ScrolledText(self.root, height=15, width=90, wrap=tk.WORD, bg="#ecf0f1", font=("Arial", 12))
        self.text_area.pack(pady=10)

        self.button_frame = tk.Frame(self.root, bg="#34495e")
        self.button_frame.pack(pady=10)

        self.add_connection_button = tk.Button(self.button_frame, text="Bağlantı Ekle", command=self.add_connection, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.add_connection_button.grid(row=0, column=0, padx=10, pady=5)

        self.manage_connections_button = tk.Button(self.button_frame, text="Bağlantıları Yönet", command=self.manage_connections, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.manage_connections_button.grid(row=0, column=1, padx=10, pady=5)

        self.list_devices_button = tk.Button(self.button_frame, text="Ağ Cihazlarını Listele", command=self.display_network_devices, bg="#27ae60", fg="white", font=("Arial", 14, "bold"), activebackground="#2ecc71", width=20, height=2)
        self.list_devices_button.grid(row=0, column=2, padx=10, pady=5)

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.root.update()

    def add_connection(self):
        connection_name = f"Bağlantı {len(self.network_manager.connections) + 1}"
        connection = Connection(connection_name)
        self.network_manager.add_connection(connection)
        self.log_message(f"{connection_name} eklendi.")

    def manage_connections(self):
        self.network_manager.manage_connections()
        for conn in self.network_manager.connections:
            if conn.is_active():
                self.log_message(f"{conn.name} aktif.")

    def display_network_devices(self):
        devices = list_network_devices()
        self.log_message(f"{'Internet Address':<20}{'Physical Address':<20}{'Type':<10}")
        self.log_message("-" * 50)
        for device in devices:
            self.log_message(f"{device['Internet Address']:<20}{device['Physical Address']:<20}{device['Type']:<10}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkSimulatorApp(root)
    root.mainloop()