import tkinter as tk
from tkinter import ttk
import random
import time
import os
import matplotlib
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras import Input
import numpy as np
import pandas as pd
import hashlib  # Blockchain for data security

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Deprecation uyarısını kapat
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash='0')

    def create_block(self, data='Genesis Block', previous_hash='0'):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'data': data,
            'previous_hash': previous_hash,
            'hash': self.hash_block(data, previous_hash)
        }
        self.chain.append(block)
        return block

    def hash_block(self, data, previous_hash):
        return hashlib.sha256(f"{data}{previous_hash}{time.time()}".encode()).hexdigest()

    def get_last_block(self):
        return self.chain[-1] if self.chain else None

    def add_block(self, data):
        last_block = self.get_last_block()
        self.create_block(data, last_block['hash'])

    def get_chain(self):
        return self.chain

class BatteryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("AeronPro BMS")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')  # Dark background color

        self.battery_level = tk.StringVar()
        self.battery_health = tk.StringVar()
        self.battery_temperature = tk.StringVar()
        self.battery_warning = tk.StringVar()
        self.temperature_warning = tk.StringVar()
        self.critical_warning = tk.StringVar()
        self.remaining_time = tk.StringVar()
        self.energy_saving_message = tk.StringVar()
        self.temperature_management_message = tk.StringVar()
        self.charging = tk.BooleanVar(value=False)
        self.performance_mode = tk.BooleanVar(value=False)
        self.battery_level_int = tk.IntVar(value=100)
        self.battery_level_color = tk.StringVar(value='green')
        self.battery_temperature_color = tk.StringVar(value='green')

        self.battery_levels = []
        self.battery_temperatures = []
        self.times = []
        self.start_time = time.time()

        self.scaler = StandardScaler()
        self.model = self.build_model()
        self.initialize_model()

        self.blockchain = Blockchain()  # Blockchain for data security

        self.setup_ui()
        self.update_ui()

    def build_model(self):
        model = Sequential()
        model.add(Input(shape=(1, 1)))
        model.add(LSTM(100, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(100, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(50))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def initialize_model(self):
        # Initialize model with dummy data to prevent shape issues during predictions
        dummy_data = np.array([[0]])
        dummy_data = self.scaler.fit_transform(dummy_data)
        dummy_data = dummy_data.reshape((dummy_data.shape[0], 1, 1))
        self.model.predict(dummy_data)

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", font=('Helvetica', 14), padding=10, background='#2980b9', foreground='white')
        style.configure("TLabel", font=('Helvetica', 14), background='#2c3e50', foreground='white')
        style.configure("Info.TLabelframe", font=('Helvetica', 14, 'bold'), background='#2c3e50', foreground='white')
        style.configure("Graph.TLabelframe", font=('Helvetica', 14, 'bold'), background='#2c3e50', foreground='white')
        style.configure("Header.TFrame", background='#34495e')
        style.configure("Header.TLabel", background='#34495e', foreground='white')
        style.configure("Control.TFrame", background='#2c3e50')
        style.configure("Warning.TLabel", font=('Helvetica', 14), background='#2c3e50', foreground='red')

        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

        header_label = ttk.Label(header_frame, text="AERONAI Battery Management System", font=('Helvetica', 24, 'bold'), style="Header.TLabel")
        header_label.pack(pady=10)

        info_frame = ttk.LabelFrame(self.root, text="Battery Information", style="Info.TLabelframe")
        info_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.create_label(info_frame, self.battery_level, 0)
        self.create_label(info_frame, self.battery_health, 1)
        self.create_label(info_frame, self.battery_temperature, 2)
        self.create_warning_label(info_frame, self.battery_warning, 3)
        self.create_warning_label(info_frame, self.temperature_warning, 4)
        self.create_warning_label(info_frame, self.critical_warning, 5)
        self.create_label(info_frame, self.remaining_time, 6)
        self.create_warning_label(info_frame, self.energy_saving_message, 7)
        self.create_warning_label(info_frame, self.temperature_management_message, 8)

        control_frame = ttk.Frame(self.root, style="Control.TFrame")
        control_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.charge_button = ttk.Button(control_frame, text="Start Charging", command=self.toggle_charging, style='TButton')
        self.charge_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.mode_button = ttk.Button(control_frame, text="Switch to Performance Mode", command=self.toggle_mode, style='TButton')
        self.mode_button.pack(side=tk.LEFT, padx=10, pady=10)

        graph_frame = ttk.LabelFrame(self.root, text="Battery Statistics", style="Graph.TLabelframe")
        graph_frame.grid(row=1, column=2, rowspan=2, padx=20, pady=10, sticky="nsew")

        fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        plt.ion()
        self.apply_macbook_style()

        self.history_frame = ttk.LabelFrame(self.root, text="History", style="Graph.TLabelframe")
        self.history_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.history_text = tk.Text(self.history_frame, height=10, bg='#2c3e50', fg='white', font=('Helvetica', 12))
        self.history_text.pack(fill=tk.BOTH, expand=True)

        blockchain_frame = ttk.LabelFrame(self.root, text="Blockchain Data", style="Graph.TLabelframe")
        blockchain_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.blockchain_text = tk.Text(blockchain_frame, height=10, bg='#2c3e50', fg='white', font=('Helvetica', 12))
        self.blockchain_text.pack(fill=tk.BOTH, expand=True)

    def create_label(self, parent, var, row):
        label = ttk.Label(parent, textvariable=var, font=('Helvetica', 14), style="Info.TLabel")
        label.grid(column=0, row=row, padx=10, pady=5, sticky="w")
        return label

    def create_warning_label(self, parent, var, row):
        label = ttk.Label(parent, textvariable=var, font=('Helvetica', 14), style="Warning.TLabel")
        label.grid(column=0, row=row, padx=10, pady=5, sticky="w")
        return label

    def update_battery_health(self, level):
        if level > 75:
            return "New"
        elif level > 50:
            return "Good"
        elif level > 25:
            return "Weak"
        else:
            return "Very Weak"

    def manage_temperature(self, temperature):
        if temperature > 60:
            return "Cooling system activated."
        return ""

    def simulate_battery(self):
        drain_rate = 1 if self.performance_mode.get() else 2
        charge_rate = 10 if self.performance_mode.get() else 5

        if not self.charging.get():
            level = max(0, self.battery_level_int.get() - random.randint(1, drain_rate * 10))
        else:
            level = min(100, self.battery_level_int.get() + random.randint(5, charge_rate))

        temperature = random.randint(20, 80)
        
        self.battery_level.set(f"AERON Battery Level: {level}%")
        self.battery_health.set(f"AERON Battery Health: {self.update_battery_health(level)}")
        self.battery_temperature.set(f"AERON Battery Temperature: {temperature}°C")
        
        if level < 20:
            self.battery_level_color.set('red')
        elif level < 50:
            self.battery_level_color.set('orange')
        else:
            self.battery_level_color.set('green')
        
        if temperature > 60:
            self.battery_temperature_color.set('red')
        elif temperature > 40:
            self.battery_temperature_color.set('orange')
        else:
            self.battery_temperature_color.set('green')

        if level < 20:
            self.battery_warning.set("Battery level low! Return the drone.")
        else:
            self.battery_warning.set("")

        if temperature > 60:
            self.temperature_warning.set("Battery overheating! Land safely.")
        else:
            self.temperature_warning.set("")

        if level < 10:
            self.critical_warning.set("Critical battery level! Land immediately.")
        else:
            self.critical_warning.set("")

        self.remaining_time.set(f"Estimated Remaining Time: {level * 2} minutes")

        self.update_graph_data(level, temperature)
        self.optimize_settings(level, temperature)

        # Geçmiş verileri kaydet ve göster
        self.log_history(level, temperature)

        # Blockchain'e veri ekleme
        self.blockchain.add_block(f"Level: {level}% | Temperature: {temperature}°C")
        self.update_blockchain_data()

    def update_graph_data(self, level, temperature):
        self.battery_levels.append(level)
        self.battery_temperatures.append(temperature)
        self.times.append(time.time() - self.start_time)

        self.ax.clear()
        self.ax.plot(self.times, self.battery_levels, label='Battery Level', color='#007AFF')
        self.ax.plot(self.times, self.battery_temperatures, label='Battery Temperature', color='#FF3B30')

        self.ax.set_xlabel('Time (s)', color='white')
        self.ax.set_ylabel('Value', color='white')
        self.ax.spines['top'].set_color('none')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.tick_params(colors='white')
        self.ax.legend(facecolor='#2c3e50', edgecolor='white')

        self.canvas.draw()

    def update_blockchain_data(self):
        chain = self.blockchain.get_chain()
        self.blockchain_text.delete(1.0, tk.END)
        for block in chain:
            block_data = f"Index: {block['index']}\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block['timestamp']))}\nData: {block['data']}\nPrevious Hash: {block['previous_hash']}\nHash: {block['hash']}\n\n"
            self.blockchain_text.insert(tk.END, block_data)

    def optimize_settings(self, level, temperature):
        if level < 20 or temperature > 60:
            self.performance_mode.set(False)
        else:
            self.performance_mode.set(True)

        mode_text = "Energy saving mode enabled." if not self.performance_mode.get() else "Performance mode enabled."
        suggestions = []
        if level < 20:
            suggestions.append("Consider reducing the load to extend battery life.")
        if temperature > 60:
            suggestions.append("Ensure proper ventilation to reduce battery temperature.")
        if not suggestions:
            suggestions.append("System operating within optimal parameters.")

        self.energy_saving_message.set(f"{mode_text} | " + " | ".join(suggestions))

    def toggle_charging(self):
        self.charging.set(not self.charging.get())
        charge_button_text = "Start Charging" if not self.charging.get() else "Stop Charging"
        self.charge_button.config(text=charge_button_text)

    def toggle_mode(self):
        self.performance_mode.set(not self.performance_mode.get())
        mode_button_text = "Switch to Performance Mode" if not self.performance_mode.get() else "Switch to Energy Saving Mode"
        self.mode_button.config(text=mode_button_text)

    def update_ui(self):
        self.simulate_battery()
        self.root.after(5000, self.update_ui)

    def apply_macbook_style(self):
        plt.style.use('ggplot')
        plt.rcParams.update({
            "figure.facecolor": "#2c3e50",
            "axes.facecolor": "#2c3e50",
            "axes.edgecolor": "white",
            "axes.labelcolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "legend.facecolor": "#2c3e50",
            "legend.edgecolor": "white",
            "grid.color": "gray",
            "text.color": "white"
        })

    def log_history(self, level, temperature):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_message = f"{timestamp} | Level: {level}% | Temperature: {temperature}°C\n"
        self.history_text.insert(tk.END, log_message)
        self.history_text.see(tk.END)  

    def detect_anomalies(self, level, temperature):
        # Anomali tespiti için basit bir kontrol 
        if level < 10 or temperature > 70:
            self.battery_warning.set("Anomalous condition detected! Take action immediately.")
            self.temperature_warning.set("Anomalous condition detected! Take action immediately.")

# Tkinter arayüzü oluşturma
root = tk.Tk()

# Stil ayarları
style = ttk.Style()
style.configure("TButton", font=('Helvetica', 14), padding=10, background='#34495e', foreground='white')
style.configure("TLabel", font=('Helvetica', 14), background='#2c3e50', foreground='white')
style.configure("Info.TLabelframe", font=('Helvetica', 14, 'bold'), background='#2c3e50', foreground='white')
style.configure("Graph.TLabelframe", font=('Helvetica', 14, 'bold'), background='#2c3e50', foreground='white')
style.configure("Header.TFrame", background='#34495e')
style.configure("Header.TLabel", background='#34495e', foreground='white')
style.configure("Control.TFrame", background='#2c3e50')
style.configure("Warning.TLabel", font=('Helvetica', 14), background='#2c3e50', foreground='red')

app = BatteryManagementSystem(root)
root.mainloop()