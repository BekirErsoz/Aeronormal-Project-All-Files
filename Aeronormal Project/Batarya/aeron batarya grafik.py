import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
import os

# Deprecation uyarısını kapat
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Batarya durumu simülasyonu fonksiyonu
def simulate_battery():
    level = random.randint(0, 100)
    temperature = random.randint(20, 80)
    
    battery_level.set(f"AERON Batarya Seviyesi: {level}%")
    battery_temperature.set(f"AERON Batarya Sıcaklığı: {temperature}°C")
    
    if level < 20:
        battery_level_color.set('red')
    elif level < 50:
        battery_level_color.set('orange')
    else:
        battery_level_color.set('green')
    
    if temperature > 60:
        battery_temperature_color.set('red')
    elif temperature > 40:
        battery_temperature_color.set('orange')
    else:
        battery_temperature_color.set('green')

    if level < 20:
        battery_warning.set("Batarya seviyesi düşük! Dronu geri çağırın.")
    else:
        battery_warning.set("")

    if temperature > 60:
        temperature_warning.set("Batarya aşırı ısınıyor! Güvenli bir şekilde iniş yapın.")
    else:
        temperature_warning.set("")

    update_graph_data(level, temperature)

# Grafik verilerini güncelleme fonksiyonu
def update_graph_data(level, temperature):
    battery_levels.append(level)
    battery_temperatures.append(temperature)
    times.append(time.time() - start_time)

    ax1.clear()
    ax2.clear()

    ax1.plot(times, battery_levels, label='Batarya Seviyesi', color='blue')
    ax2.plot(times, battery_temperatures, label='Batarya Sıcaklığı', color='red')

    ax1.set_xlabel('Zaman (saniye)')
    ax1.set_ylabel('Batarya Seviyesi (%)')
    ax2.set_xlabel('Zaman (saniye)')
    ax2.set_ylabel('Batarya Sıcaklığı (°C)')
    
    if len(times) == 1:
        ax1.legend()
        ax2.legend()

    canvas.draw()

# Arayüzü güncelleme fonksiyonu
def update_ui():
    simulate_battery()
    battery_level_label.config(foreground=battery_level_color.get())
    battery_temperature_label.config(foreground=battery_temperature_color.get())
    root.after(5000, update_ui)

# Tkinter arayüzü oluşturma
root = tk.Tk()
root.title("AERON Batarya Yönetim Sistemi Simülasyonu")
root.configure(bg='#f0f0f0')  # Background color

# Başlık etiketi
header_label = ttk.Label(root, text="AERON Batarya Yönetim Sistemi", font=('Helvetica', 18, 'bold'), background='#f0f0f0')
header_label.grid(column=0, row=0, columnspan=2, padx=10, pady=10)

battery_level = tk.StringVar()
battery_temperature = tk.StringVar()
battery_warning = tk.StringVar()
temperature_warning = tk.StringVar()

battery_level_color = tk.StringVar(value='green')
battery_temperature_color = tk.StringVar(value='green')

style = ttk.Style()
style.configure("TLabel", font=('Helvetica', 14), background='#f0f0f0')
style.configure("Warning.TLabel", font=('Helvetica', 12), foreground='red', background='#f0f0f0')

# Batarya seviyesi etiketi
battery_level_label = ttk.Label(root, textvariable=battery_level, style="TLabel")
battery_level_label.grid(column=0, row=1, padx=10, pady=10)

# Batarya sıcaklığı etiketi
battery_temperature_label = ttk.Label(root, textvariable=battery_temperature, style="TLabel")
battery_temperature_label.grid(column=0, row=2, padx=10, pady=10)

# Batarya uyarı etiketi
battery_warning_label = ttk.Label(root, textvariable=battery_warning, style="Warning.TLabel")
battery_warning_label.grid(column=0, row=3, padx=10, pady=10)

# Sıcaklık uyarı etiketi
temperature_warning_label = ttk.Label(root, textvariable=temperature_warning, style="Warning.TLabel")
temperature_warning_label.grid(column=0, row=4, padx=10, pady=10)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
fig.patch.set_facecolor('#f0f0f0')  # Figure background color
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=1, row=1, rowspan=4, padx=10, pady=10)

plt.ion()

battery_levels = []
battery_temperatures = []
times = []
start_time = time.time()

root.after(0, update_ui)
root.mainloop()