import tkinter as tk
from tkinter import ttk
import random
import time
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Deprecation uyarısını kapat
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Batarya sağlık durumu fonksiyonu
def update_battery_health(level):
    if level > 75:
        return "Yeni"
    elif level > 50:
        return "İyi"
    elif level > 25:
        return "Zayıf"
    else:
        return "Çok Zayıf"

# Batarya durumu simülasyonu fonksiyonu
def simulate_battery():
    if not charging.get():
        level = max(0, battery_level_int.get() - random.randint(1, 10))
    else:
        level = min(100, battery_level_int.get() + random.randint(5, 15))

    temperature = random.randint(20, 80)
    
    battery_level.set(f"AERON Batarya Seviyesi: {level}%")
    battery_health.set(f"AERON Batarya Sağlığı: {update_battery_health(level)}")
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

    if level < 10:
        critical_warning.set("Kritik batarya seviyesi! Acil iniş yapın.")
    else:
        critical_warning.set("")

    # Kalan süre tahmini
    remaining_time.set(f"Kalan Süre Tahmini: {level * 2} dakika")

    update_graph_data(level, temperature)

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

def toggle_charging():
    charging.set(not charging.get())
    charge_button.config(text="Şarj Et" if not charging.get() else "Şarjı Durdur")

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
battery_health = tk.StringVar()
battery_temperature = tk.StringVar()
battery_warning = tk.StringVar()
temperature_warning = tk.StringVar()
critical_warning = tk.StringVar()
remaining_time = tk.StringVar()
charging = tk.BooleanVar(value=False)
battery_level_int = tk.IntVar(value=100)

battery_level_color = tk.StringVar(value='green')
battery_temperature_color = tk.StringVar(value='green')

style = ttk.Style()
style.configure("TLabel", font=('Helvetica', 14), background='#f0f0f0')
style.configure("Warning.TLabel", font=('Helvetica', 12), foreground='red', background='#f0f0f0')

# Batarya seviyesi etiketi
battery_level_label = ttk.Label(root, textvariable=battery_level, style="TLabel")
battery_level_label.grid(column=0, row=1, padx=10, pady=10)

# Batarya sağlık durumu etiketi
battery_health_label = ttk.Label(root, textvariable=battery_health, style="TLabel")
battery_health_label.grid(column=0, row=2, padx=10, pady=10)

# Batarya sıcaklığı etiketi
battery_temperature_label = ttk.Label(root, textvariable=battery_temperature, style="TLabel")
battery_temperature_label.grid(column=0, row=3, padx=10, pady=10)

# Batarya uyarı etiketi
battery_warning_label = ttk.Label(root, textvariable=battery_warning, style="Warning.TLabel")
battery_warning_label.grid(column=0, row=4, padx=10, pady=10)

# Sıcaklık uyarı etiketi
temperature_warning_label = ttk.Label(root, textvariable=temperature_warning, style="Warning.TLabel")
temperature_warning_label.grid(column=0, row=5, padx=10, pady=10)

# Kritik batarya uyarısı
critical_warning_label = ttk.Label(root, textvariable=critical_warning, style="Warning.TLabel")
critical_warning_label.grid(column=0, row=6, padx=10, pady=10)

# Kalan süre tahmini etiketi
remaining_time_label = ttk.Label(root, textvariable=remaining_time, style="TLabel")
remaining_time_label.grid(column=0, row=7, padx=10, pady=10)

# Şarj etme butonu
charge_button = ttk.Button(root, text="Şarj Et", command=toggle_charging)
charge_button.grid(column=0, row=8, padx=10, pady=10)

# Grafiklerin oluşturulması
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=1, row=0, rowspan=9, padx=10, pady=10)

plt.ion()

battery_levels = []
battery_temperatures = []
times = []
start_time = time.time()

root.after(0, update_ui)
root.mainloop()