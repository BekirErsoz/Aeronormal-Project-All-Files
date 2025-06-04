import tkinter as tk
from tkinter import ttk
import random
import time
import os
import matplotlib
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use('TkAgg')

# Deprecation uyarısını kapat
os.environ['TK_SILENCE_DEPRECATION'] = '1'

class BatteryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("AERONAI Battery Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')  # Dark background color

        self.battery_level = tk.StringVar(value="Charge: 97 %")
        self.battery_health = tk.StringVar(value="Health: Good")
        self.battery_temperature = tk.StringVar(value="Temperature: 35°C")
        self.battery_warning = tk.StringVar(value="")
        self.temperature_warning = tk.StringVar(value="")
        self.critical_warning = tk.StringVar(value="")
        self.remaining_time = tk.StringVar(value="Estimated Time: 120 min")
        self.energy_saving_message = tk.StringVar(value="")
        self.temperature_management_message = tk.StringVar(value="")
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

        self.setup_ui()
        self.update_ui()

    def build_model(self):
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(1, 1)))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dense(25))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def setup_ui(self):
        # Üst Bilgi Paneli
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(fill=tk.X, pady=10)

        header_label = tk.Label(header_frame, text="AERONAI Battery Management System", font=('Helvetica', 24, 'bold'), bg='#2c3e50', fg='white')
        header_label.pack(pady=10)

        # Sol Panel - Batarya Bilgileri
        left_frame = tk.Frame(self.root, bg='#34495e', relief="flat", padx=15, pady=15)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        battery_icon = tk.Label(left_frame, text="🔋", font=("Helvetica", 60), bg='#34495e', fg='white')
        battery_icon.pack(pady=20)

        # Batarya Bilgileri
        self.create_info_block(left_frame, "Charge", self.battery_level, "#2ecc71")
        self.create_info_block(left_frame, "Health", self.battery_health, "#3498db")
        self.create_info_block(left_frame, "Temperature", self.battery_temperature, "#e74c3c")

        # Batarya Uyarıları
        self.create_warning_block(left_frame, "Battery Warning", self.battery_warning)
        self.create_warning_block(left_frame, "Temperature Warning", self.temperature_warning)
        self.create_warning_block(left_frame, "Critical Warning", self.critical_warning)

        # Performans Modu Butonu
        self.mode_button = tk.Button(left_frame, text="Switch to Performance Mode", command=self.toggle_mode, font=('Helvetica', 16, 'bold'), bg='#2980b9', fg='white', height=2, width=25)
        self.mode_button.pack(side=tk.TOP, pady=20)

        # Alt Panel - Kontrol Butonları
        control_frame = tk.Frame(left_frame, bg='#34495e')
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.charge_button = tk.Button(control_frame, text="Start Charging", command=self.toggle_charging, font=('Helvetica', 12), bg='#27ae60', fg='white', width=20)
        self.charge_button.pack(side=tk.TOP, pady=5)

        self.exit_button = tk.Button(control_frame, text="Exit", command=self.root.quit, font=('Helvetica', 12), bg='#e74c3c', fg='white', width=20)
        self.exit_button.pack(side=tk.TOP, pady=5)

        # Sağ Panel - Grafik ve Detaylı Bilgiler
        right_frame = tk.Frame(self.root, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.graph_frame(right_frame)
        self.info_frame(right_frame)

    def create_info_block(self, parent, label_text, var, color):
        block = tk.Frame(parent, bg=color, padx=10, pady=10, relief="flat", bd=2)
        block.pack(fill=tk.X, pady=5)
        
        label = tk.Label(block, text=label_text, font=('Helvetica', 14, 'bold'), bg=color, fg='white')
        label.pack(side=tk.LEFT)

        value = tk.Label(block, textvariable=var, font=('Helvetica', 14), bg=color, fg='white')
        value.pack(side=tk.RIGHT)

    def create_warning_block(self, parent, label_text, var):
        block = tk.Frame(parent, bg='#c0392b', padx=10, pady=10, relief="flat", bd=2)
        block.pack(fill=tk.X, pady=5)
        
        label = tk.Label(block, text=label_text, font=('Helvetica', 14, 'bold'), bg='#c0392b', fg='white')
        label.pack(side=tk.LEFT)

        value = tk.Label(block, textvariable=var, font=('Helvetica', 14), bg='#c0392b', fg='white')
        value.pack(side=tk.RIGHT)

    def graph_frame(self, parent):
        graph_frame = tk.Frame(parent, bg='#2c3e50')
        graph_frame.pack(fill=tk.BOTH, expand=True)

        fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        plt.ion()
        self.apply_macbook_style()

    def info_frame(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Battery Information", style="Info.TLabelframe", padding=(10, 10))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        general_info = [
            ("Designed Capacity", "48,840 mWh"),
            ("Full Charged Capacity", "44,089 mWh"),
            ("Current Capacity", "42,879 mWh"),
            ("Capacity Drop", "4,751 mWh"),
            ("Battery Voltage", "12,410 mV"),
            ("Charge Rate", "0 mW"),
            ("Warning Alert", "0 mWh"),
            ("Low Level Alert", "0 mWh"),
            ("Critical Bias", "0 mWh"),
        ]

        for label, value in general_info:
            self.create_info_row(info_frame, label, value)

    def create_info_row(self, parent, label_text, value_text):
        row_frame = tk.Frame(parent, bg='#2c3e50')
        row_frame.pack(fill=tk.X, pady=5)

        label = tk.Label(row_frame, text=label_text, font=("Helvetica", 14), bg='#2c3e50', fg='white')
        label.pack(side=tk.LEFT)

        value = tk.Label(row_frame, text=value_text, font=("Helvetica", 14), bg='#2c3e50', fg='#f39c12')
        value.pack(side=tk.RIGHT)

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
        
        self.battery_level.set(f"Charge: {level}%")
        self.battery_health.set(f"Health: {self.update_battery_health(level)}")
        self.battery_temperature.set(f"Temperature: {temperature}°C")
        
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