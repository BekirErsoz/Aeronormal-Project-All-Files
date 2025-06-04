import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
import cv2

# Rota Optimizasyonu Sınıfı
class RouteOptimizer:
    def __init__(self, locations_file, routes_file):
        self.locations = pd.read_csv(locations_file)
        self.routes = pd.read_csv(routes_file)

    def find_nearest(self, start_location, end_location):
        start_coords = self.locations[self.locations['name'] == start_location][['latitude', 'longitude']].values
        end_coords = self.locations[self.locations['name'] == end_location][['latitude', 'longitude']].values

        neighbors = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(self.routes[['start_latitude', 'start_longitude']])
        distance, index = neighbors.kneighbors(start_coords)
        optimal_route = self.routes.iloc[index[0]]

        return optimal_route

    def calculate_optimal_route(self, start_location, end_location):
        route = self.find_nearest(start_location, end_location)
        return route

# Artırılmış Gerçeklik Sınıfı
class ARNavigator:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def start_navigation(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Basit AR: Çizgilerle yönlendirme
            cv2.line(frame, (100, 200), (400, 200), (0, 255, 0), 5)
            cv2.putText(frame, "Duz ilerleyin", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow('IstanbulAirNavigator AR', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

# Kullanıcı Arayüzü Sınıfı
class IstanbulAirNavigatorUI(tk.Tk):
    def __init__(self, optimizer, ar_navigator):
        super().__init__()

        self.optimizer = optimizer
        self.ar_navigator = ar_navigator

        # Pencere ayarları
        self.title("IstanbulAirNavigator")
        self.geometry("800x600")
        self.configure(bg='#2c3e50')

        # Uygulama logosu
        self.load_logo()

        # Başlık
        self.header = tk.Label(self, text="İstanbul Havalimanı Akıllı Navigasyon Sistemi", 
                               font=("Helvetica", 18, "bold"), fg="white", bg="#2c3e50")
        self.header.pack(pady=10)

        # Harita gösterimi
        self.map_frame = tk.Frame(self, bg='#34495e')
        self.map_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.load_map()

        # Kontrol paneli
        self.control_frame = tk.Frame(self, bg='#34495e')
        self.control_frame.pack(side="right", fill="y", padx=10, pady=10)
        self.create_controls()

    def load_logo(self):
        logo_img = Image.open("assets/logo.png")
        logo_img = logo_img.resize((100, 100), Image.ANTIALIAS)
        self.logo_photo = ImageTk.PhotoImage(logo_img)
        self.logo_label = tk.Label(self, image=self.logo_photo, bg='#2c3e50')
        self.logo_label.pack(pady=5)

    def load_map(self):
        map_img = Image.open("assets/istanbul_map.png")
        map_img = map_img.resize((500, 500), Image.ANTIALIAS)
        self.map_photo = ImageTk.PhotoImage(map_img)
        self.map_label = tk.Label(self.map_frame, image=self.map_photo, bg='#34495e')
        self.map_label.pack(padx=10, pady=10)

    def create_controls(self):
        # Lokasyon seçimleri
        self.start_label = tk.Label(self.control_frame, text="Başlangıç Noktası:", 
                                    font=("Helvetica", 12), fg="white", bg="#34495e")
        self.start_label.pack(pady=5)
        self.start_combobox = ttk.Combobox(self.control_frame, values=self.optimizer.locations['name'].tolist())
        self.start_combobox.pack(pady=5)

        self.end_label = tk.Label(self.control_frame, text="Varış Noktası:", 
                                  font=("Helvetica", 12), fg="white", bg="#34495e")
        self.end_combobox = ttk.Combobox(self.control_frame, values=self.optimizer.locations['name'].tolist())
        self.end_combobox.pack(pady=5)

        # Rota bulma butonu
        self.route_button = tk.Button(self.control_frame, text="En İyi Rotayı Bul", command=self.find_route, 
                                      font=("Helvetica", 12), bg="#1abc9c", fg="white")
        self.route_button.pack(pady=20)

        # AR yönlendirme butonu
        self.ar_button = tk.Button(self.control_frame, text="AR Yönlendirmeyi Başlat", command=self.start_ar_navigation, 
                                   font=("Helvetica", 12), bg="#3498db", fg="white")
        self.ar_button.pack(pady=10)

    def find_route(self):
        start_location = self.start_combobox.get()
        end_location = self.end_combobox.get()
        route = self.optimizer.calculate_optimal_route(start_location, end_location)
        print(f"En iyi rota {start_location} ile {end_location} arasında: {route}")

    def start_ar_navigation(self):
        self.ar_navigator.start_navigation()

# Ana Uygulama Sınıfı
class IstanbulAirNavigatorApp:
    def __init__(self):
        self.optimizer = RouteOptimizer("data/locations.csv", "data/routes.csv")
        self.ar_navigator = ARNavigator()
        self.ui = IstanbulAirNavigatorUI(self.optimizer, self.ar_navigator)

    def run(self):
        self.ui.mainloop()

if __name__ == "__main__":
    app = IstanbulAirNavigatorApp()
    app.run()