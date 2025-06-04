import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.spatial import distance_matrix
import threading
import logging
import time
from itertools import permutations
import folium
from tkhtmlview import HTMLLabel

# Logging yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AeronProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AeronProAI - Otonom Görev Planlama")
        self.root.geometry("1200x800")
        self.root.configure(bg="#282c34")

        self.start_point = None
        self.end_point = None
        self.waypoints = []
        self.battery_level = 100
        self.speed = 0
        self.battery_warning_shown = False
        self.speed_warning_shown = False

        self.create_widgets()
        self.bind_events()
        self.create_map()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Görev Planlama Arayüzü", font=("Arial", 20), bg="#282c34", fg="white")
        self.label.pack(pady=10)

        self.instructions = tk.Label(self.root, text="Başlangıç ve bitiş noktalarını belirlemek için haritaya tıklayın, ardından waypointler ekleyin.", font=("Arial", 14), bg="#282c34", fg="white")
        self.instructions.pack(pady=10)

        self.info_frame = tk.Frame(self.root, bg="#282c34")
        self.info_frame.pack(pady=10)

        self.battery_label = tk.Label(self.info_frame, text="Batarya: %100", font=("Arial", 14), bg="#282c34", fg="white")
        self.battery_label.pack(side="left", padx=20)

        self.speed_label = tk.Label(self.info_frame, text="Hız: 0 km/h", font=("Arial", 14), bg="#282c34", fg="white")
        self.speed_label.pack(side="right", padx=20)

        self.map_frame = tk.Frame(self.root, bg="#282c34")
        self.map_frame.pack(pady=20)

        self.plan_button = tk.Button(self.root, text="Görevi Planla", font=("Arial", 14), bg="#61afef", fg="white", command=self.plan_mission)
        self.plan_button.pack(pady=10)

        self.auto_plan_button = tk.Button(self.root, text="Otomatik Görev Planla", font=("Arial", 14), bg="#98c379", fg="white", command=self.auto_plan_mission)
        self.auto_plan_button.pack(pady=10)

        self.reset_button = tk.Button(self.root, text="Sıfırla", font=("Arial", 14), bg="#e06c75", fg="white", command=self.reset)
        self.reset_button.pack(pady=10)

        self.info_label = tk.Label(self.root, text="Nokta ve Rota Bilgileri", font=("Arial", 16), bg="#282c34", fg="white")
        self.info_label.pack(pady=10)

        self.info_text = tk.Text(self.root, height=10, width=80)
        self.info_text.pack(pady=10)

        self.telemetry_label = tk.Label(self.root, text="Telemetri Verileri", font=("Arial", 16), bg="#282c34", fg="white")
        self.telemetry_label.pack(pady=10)

        self.telemetry_text = tk.Text(self.root, height=10, width=80)
        self.telemetry_text.pack(pady=10)

    def bind_events(self):
        pass  # Harita üzerinde tıklama olayları burada ele alınacak

    def create_map(self):
        map_center = [41.0082, 28.9784]  # Istanbul koordinatları
        self.map = folium.Map(location=map_center, zoom_start=13)
        self.map_html = self.map._repr_html_()

        self.map_label = HTMLLabel(self.map_frame, html=self.map_html)
        self.map_label.pack()

    def plan_mission(self):
        if not self.start_point or not self.end_point:
            messagebox.showwarning("Uyarı", "Lütfen başlangıç ve bitiş noktalarını belirleyin.")
            return

        all_points = [self.start_point] + self.waypoints + [self.end_point]
        optimal_route = self.optimize_route(all_points)

        for i in range(len(optimal_route) - 1):
            point1 = optimal_route[i]
            point2 = optimal_route[i+1]
            folium.PolyLine([point1, point2], color="yellow", weight=2.5, opacity=1).add_to(self.map)

        self.update_map()

    def auto_plan_mission(self):
        if not self.start_point or not self.end_point:
            messagebox.showwarning("Uyarı", "Lütfen başlangıç ve bitiş noktalarını belirleyin.")
            return

        all_points = [self.start_point] + self.waypoints + [self.end_point]
        optimal_route = self.optimize_route(all_points)

        for i in range(len(optimal_route) - 1):
            point1 = optimal_route[i]
            point2 = optimal_route[i+1]
            folium.PolyLine([point1, point2], color="yellow", weight=2.5, opacity=1).add_to(self.map)

        route_str = ' -> '.join([f'({x}, {y})' for x, y in optimal_route])
        self.info_text.insert(tk.END, f"Otomatik Planlanan Rota: {route_str}\n")
        self.update_map()

    def update_map(self):
        self.map_html = self.map._repr_html_()
        self.map_label.set_html(self.map_html)

    def reset(self):
        self.start_point = None
        self.end_point = None
        self.waypoints = []
        self.battery_level = 100
        self.speed = 0
        self.battery_warning_shown = False
        self.speed_warning_shown = False
        self.create_map()
        self.info_text.delete(1.0, tk.END)
        self.telemetry_text.delete(1.0, tk.END)
        self.battery_label.config(text="Batarya: %100")
        self.speed_label.config(text="Hız: 0 km/h")

    def optimize_route(self, points):
        points = np.array(points)
        num_points = len(points)

        if num_points < 3:
            return points

        dist_matrix = distance_matrix(points, points)

        min_route = None
        min_distance = float('inf')

        for perm in permutations(range(1, num_points - 1)):
            route = [0] + list(perm) + [num_points - 1]
            current_distance = sum(
                dist_matrix[route[i], route[i + 1]] for i in range(num_points - 1)
            )
            if current_distance < min_distance:
                min_distance = current_distance
                min_route = route

        optimal_route = [points[i] for i in min_route]
        return optimal_route

    def start_telemetry(self):
        def update_telemetry():
            while self.battery_level > 0:
                self.speed = np.random.uniform(10, 20)
                self.battery_level -= np.random.uniform(0.5, 1.0)
                telemetry_data = {
                    "latitude": np.random.uniform(40, 42),
                    "longitude": np.random.uniform(28, 30),
                    "altitude": np.random.uniform(100, 200),
                    "speed": self.speed,
                    "battery": self.battery_level
                }
                self.telemetry_text.insert(tk.END, f"Telemetri: {telemetry_data}\n")
                self.telemetry_text.see(tk.END)
                logging.info(f"Telemetri verisi güncellendi: {telemetry_data}")
                self.battery_label.config(text=f"Batarya: %{self.battery_level:.2f}")
                self.speed_label.config(text=f"Hız: {self.speed:.2f} km/h")
                if self.battery_level <= 20 and not self.battery_warning_shown:
                    messagebox.showwarning("Uyarı", "Batarya seviyesi düşük!")
                    self.battery_warning_shown = True
                if self.speed > 15 and not self.speed_warning_shown:
                    messagebox.showwarning("Uyarı", "Hız çok yüksek!")
                    self.speed_warning_shown = True
                time.sleep(5)  # Telemetri verilerini her 5 saniyede bir güncelle

        telemetry_thread = threading.Thread(target=update_telemetry, daemon=True)
        telemetry_thread.start()

    def on_map_click(self, event):
        lat, lon = event.latlng
        if not self.start_point:
            self.start_point = [lat, lon]
            folium.Marker(location=self.start_point, popup="Başlangıç Noktası", icon=folium.Icon(color="green")).add_to(self.map)
            self.info_text.insert(tk.END, f"Başlangıç Noktası: ({lat}, {lon})\n")
        elif not self.end_point:
            self.end_point = [lat, lon]
            folium.Marker(location=self.end_point, popup="Bitiş Noktası", icon=folium.Icon(color="red")).add_to(self.map)
            self.info_text.insert(tk.END, f"Bitiş Noktası: ({lat}, {lon})\n")
        else:
            waypoint = [lat, lon]
            self.waypoints.append(waypoint)
            folium.Marker(location=waypoint, popup="Waypoint", icon=folium.Icon(color="blue")).add_to(self.map)
            self.info_text.insert(tk.END, f"Waypoint: ({lat}, {lon})\n")
        self.update_map()

    def create_map(self):
        map_center = [41.0082, 28.9784]  # Istanbul koordinatları
        self.map = folium.Map(location=map_center, zoom_start=13)
        self.map_html = self.map._repr_html_()

        self.map_label = HTMLLabel(self.map_frame, html=self.map_html)
        self.map_label.pack()
        self.map_label.bind("<Button-1>", self.on_map_click)

    def update_map(self):
        self.map_html = self.map._repr_html_()
        self.map_label.set_html(self.map_html)

if __name__ == "__main__":
    root = tk.Tk()
    app = AeronProApp(root)
    root.mainloop()