import random
import time
import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from sklearn.ensemble import IsolationForest

class Drone:
    def __init__(self, id, interface):
        self.id = id
        self.connection_status = True
        self.interface = interface
    
    def send_data(self, data):
        if self.connection_status:
            self.interface.log_message(f"Drone {self.id} sending data: {data}")
        else:
            self.interface.log_message(f"Drone {self.id} connection lost.")
    
    def reconnect(self):
        self.interface.log_message(f"Drone {self.id} attempting to reconnect...")
        time.sleep(1)
        self.connection_status = True
        self.interface.log_message(f"Drone {self.id} reconnected.")

class SIHA:
    def __init__(self, id, interface):
        self.id = id
        self.connection_status = True
        self.interface = interface
    
    def send_data(self, data):
        if self.connection_status:
            self.interface.log_message(f"SIHA {self.id} sending data: {data}")
        else:
            self.interface.log_message(f"SIHA {self.id} connection lost.")
    
    def reconnect(self):
        self.interface.log_message(f"SIHA {self.id} attempting to reconnect...")
        time.sleep(1)
        self.connection_status = True
        self.interface.log_message(f"SIHA {self.id} reconnected.")

class SimulationInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone ve SİHA İletişim Sistemi AI")
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(self.main_frame, state='disabled', width=80, height=20)
        self.log_text.grid(row=0, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(self.main_frame, text="Simülasyonu Başlat", command=self.start_simulation)
        self.start_button.grid(row=1, column=0, pady=10, sticky=tk.E)
        
        self.stop_button = ttk.Button(self.main_frame, text="Simülasyonu Durdur", command=self.stop_simulation, state='disabled')
        self.stop_button.grid(row=1, column=1, pady=10, sticky=tk.W)
        
        self.drones = []
        self.sihas = []
        self.simulation_running = False

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, self.main_frame)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, pady=20)
        
        self.data_points = []
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.anomalies = []
    
    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
    
    def start_simulation(self):
        self.simulation_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.log_message("Simülasyon Başlıyor...")
        
        self.drones = [Drone(i, self) for i in range(1, 3)]
        self.sihas = [SIHA(i, self) for i in range(1, 3)]
        
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.start()
    
    def stop_simulation(self):
        self.simulation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.log_message("Simülasyon Durduruldu.")
    
    def run_simulation(self):
        for _ in range(10):
            if not self.simulation_running:
                break
            
            data = random.randint(100, 999)
            for drone in self.drones:
                drone.send_data(data)
            
            for siha in self.sihas:
                siha.send_data(data)
            
            # Simüle edilmiş bağlantı kesilmesi
            if random.choice([True, False]):
                drone = random.choice(self.drones)
                drone.connection_status = False
                drone.reconnect()
            
            if random.choice([True, False]):
                siha = random.choice(self.sihas)
                siha.connection_status = False
                siha.reconnect()
            
            self.data_points.append(data)
            self.update_graph()
            
            self.root.update()
            time.sleep(2)
        
        self.detect_anomalies()

    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.data_points, label='Veri Akışı')
        self.ax.scatter(range(len(self.data_points)), self.data_points, c=['red' if i in self.anomalies else 'blue' for i in range(len(self.data_points))], label='Anomalies', s=10)
        self.ax.set_title('Drone ve SİHA Veri Akışı')
        self.ax.set_xlabel('Zaman')
        self.ax.set_ylabel('Veri Değeri')
        self.ax.legend()
        self.canvas.draw()

    def detect_anomalies(self):
        if len(self.data_points) >= 10:
            data_array = np.array(self.data_points).reshape(-1, 1)
            self.anomaly_detector.fit(data_array)
            predictions = self.anomaly_detector.predict(data_array)
            self.anomalies = [i for i, pred in enumerate(predictions) if pred == -1]
            self.update_graph()
            self.log_message(f"Detected anomalies at indices: {self.anomalies}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationInterface(root)
    root.mainloop()