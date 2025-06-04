import tkinter as tk
from tkinter import ttk
import random
import time
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

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

# Enerji tasarrufu modu fonksiyonu
def enable_energy_saving_mode(level):
    if level < 20:
        return "Enerji tasarrufu modu etkinleştirildi."
    return ""

# Isı yönetimi fonksiyonu
def manage_temperature(temperature):
    if temperature > 60:
        return "Soğutma sistemi etkinleştirildi."
    return ""

# Saat güncelleme fonksiyonu
def update_clock():
    now = datetime.now().strftime("%H:%M:%S")
    current_time.set(f"Saat: {now}")
    root.after(1000, update_clock)

# Güç tüketimi grafiği için verileri güncelleme fonksiyonu
def update_power_consumption(level):
    power_consumptions.append(100 - level)
    power_times.append(time.time() - start_time)
    ax3.clear()
    ax3.plot(power_times, power_consumptions, label='Güç Tüketimi', color='green')
    ax3.set_xlabel('Zaman (saniye)')
    ax3.set_ylabel('Güç Tüketimi (%)')
    if len(power_times) == 1:
        ax3.legend()
    canvas.draw()

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

    energy_saving_message.set(enable_energy_saving_mode(level))
    temperature_management_message.set(manage_temperature(temperature))

    update_graph_data(level, temperature)
    update_power_consumption(level)

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

def switch_flight_mode():
    modes = ["Otomatik", "Manuel", "Enerji Tasarrufu"]
    current_mode = flight_mode.get()
    new_mode = modes[(modes.index(current_mode) + 1) % len(modes)]
    flight_mode.set(new_mode)
    flight_mode_button.config(text=f"Uçuş Modu: {new_mode}")

# Arayüzü güncelleme fonksiyonu
def update_ui():
    simulate_battery()
    battery_level_label.config(foreground=battery_level_color.get())
    battery_temperature_label.config(foreground=battery_temperature_color.get())
    root.after(5000, update_ui)

# Tkinter arayüzü oluşturma
root = tk.Tk()
root.title("AERON Batarya Yönetim Sistemi Simülasyonu")
root.configure(bg='#1e1e1e')  # Background color

# Stil Ayarları
style = ttk.Style()
style.theme_use('clam')

style.configure("TLabel", font=('Helvetica', 14), background='#1e1e1e', foreground='white')
style.configure("TButton", font=('Helvetica', 14), background='#4CAF50', foreground='white')
style.map("TButton", background=[('active', '#45a049')])

style.configure("Warning.TLabel", font=('Helvetica', 12), foreground='red', background='#1e1e1e')

# Başlık etiketi
header_label = ttk.Label(root, text="AERON Batarya Yönetim Sistemi", font=('Helvetica', 18, 'bold'), background='#1e1e1e', foreground='white')
header_label.grid(column=0, row=0, columnspan=2, padx=10, pady=10)

battery_level = tk.StringVar()
battery_health = tk.StringVar()
battery_temperature = tk.StringVar()
battery_warning = tk.StringVar()
temperature_warning = tk.StringVar()
critical_warning = tk.StringVar()
remaining_time = tk.StringVar()
energy_saving_message = tk.StringVar()
temperature_management_message = tk.StringVar()
current_time = tk.StringVar()
flight_status = tk.StringVar(value="Normal")
backup_battery_status = tk.StringVar(value="Yedek Pil Durumu: İyi")
charging = tk.BooleanVar(value=False)
battery_level_int = tk.IntVar(value=100)
flight_mode = tk.StringVar(value="Otomatik")

battery_level_color = tk.StringVar(value='green')
battery_temperature_color = tk.StringVar(value='green')

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

# Enerji tasarrufu mesajı etiketi
energy_saving_message_label = ttk.Label(root, textvariable=energy_saving_message, style="Warning.TLabel")
energy_saving_message_label.grid(column=0, row=8, padx=10, pady=10)

# Sıcaklık yönetimi mesajı etiketi
temperature_management_message_label = ttk.Label(root, textvariable=temperature_management_message, style="Warning.TLabel")
temperature_management_message_label.grid(column=0, row=9, padx=10, pady=10)

# Uçuş durumu etiketi
flight_status_label = ttk.Label(root, textvariable=flight_status, style="TLabel")
flight_status_label.grid(column=0, row=10, padx=10, pady=10)

# Yedek pil durumu etiketi
backup_battery_status_label = ttk.Label(root, textvariable=backup_battery_status, style="TLabel")
backup_battery_status_label.grid(column=0, row=11, padx=10, pady=10)

# Şu anki zaman etiketi
current_time_label = ttk.Label(root, textvariable=current_time, style="TLabel")
current_time_label.grid(column=0, row=12, padx=10, pady=10)

# Şarj etme butonu
charge_button = ttk.Button(root, text="Şarj Et", command=toggle_charging)
charge_button.grid(column=0, row=13, padx=10, pady=10)

# Uçuş modu butonu
flight_mode_button = ttk.Button(root, text="Uçuş Modu: Otomatik", command=switch_flight_mode)
flight_mode_button.grid(column=0, row=14, padx=10, pady=10)

# Grafiklerin oluşturulması
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 9), facecolor='#1e1e1e')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=1, row=0, rowspan=15, padx=10, pady=10)

plt.ion()

battery_levels = []
battery_temperatures = []
power_consumptions = []
times = []
power_times = []
start_time = time.time()

root.after(0, update_ui)
update_clock()
root.mainloop()