import random
import time
import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

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
        self.kmeans_model = KMeans(n_clusters=2)
        self.init_menus()
        self.user_roles = {"admin": ["view", "control", "configure"], "user": ["view"]}
        self.current_user_role = "admin"  
    
    def init_menus(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Logs", command=self.show_logs)
        view_menu.add_command(label="Analytics", command=self.show_analytics)
    
    def show_logs(self):
        log_window = tk.Toplevel(self.root)
        log_window.title("Log Viewer")
        log_text = tk.Text(log_window, state='normal', width=80, height=20)
        log_text.pack()
        log_text.insert(tk.END, self.log_text.get("1.0", tk.END))

    def show_analytics(self):
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Analytics Viewer")
        figure, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(figure, analytics_window)
        canvas.get_tk_widget().pack()
        
        if len(self.data_points) > 0:
            ax.plot(self.data_points, label='Veri Akışı')
            ax.scatter(range(len(self.data_points)), self.data_points, c=['red' if i in self.anomalies else 'blue' for i in range(len(self.data_points))], label='Anomalies', s=10)
            ax.set_title('Drone ve SİHA Veri Akışı')
            ax.set_xlabel('Zaman')
            ax.set_ylabel('Veri Değeri')
            ax.legend()
            canvas.draw()

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
        self.perform_clustering()

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
    
    def perform_clustering(self):
        if len(self.data_points) >= 10:
            data_array = np.array(self.data_points).reshape(-1, 1)
            self.kmeans_model.fit(data_array)
            clusters = self.kmeans_model.labels_
            self.ax.clear()
            self.ax.plot(self.data_points, label='Veri Akışı')
            self.ax.scatter(range(len(self.data_points)), self.data_points, c=clusters, cmap='viridis', label='Clusters', s=10)
            self.ax.set_title('Drone ve SİHA Veri Akışı ve Kümeleme')
            self.ax.set_xlabel('Zaman')
            self.ax.set_ylabel('Veri Değeri')
            self.ax.legend()
            self.canvas.draw()
            self.log_message("Performed clustering on data points.")
    
    def configure_user_roles(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Configure User Roles")
        roles_frame = ttk.Frame(config_window, padding="10")
        roles_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        roles_label = ttk.Label(roles_frame, text="Kullanıcı Rolleri")
        roles_label.grid(row=0, column=0, pady=10)

        self.role_listbox = tk.Listbox(roles_frame)
        self.role_listbox.grid(row=1, column=0, pady=10)

        for role in self.user_roles:
            self.role_listbox.insert(tk.END, role)

        add_role_button = ttk.Button(roles_frame, text="Add Role", command=self.add_role)
        add_role_button.grid(row=2, column=0, pady=5)
        remove_role_button = ttk.Button(roles_frame, text="Remove Role", command=self.remove_role)
        remove_role_button.grid(row=3, column=0, pady=5)

        permissions_label = ttk.Label(roles_frame, text="Permissions")
        permissions_label.grid(row=4, column=0, pady=10)
        self.permissions_text = tk.Text(roles_frame, height=5)
        self.permissions_text.grid(row=5, column=0, pady=10)

        save_button = ttk.Button(roles_frame, text="Save", command=self.save_roles)
        save_button.grid(row=6, column=0, pady=10)

    def add_role(self):
        new_role = self.role_listbox.get(tk.END)
        self.user_roles[new_role] = []
        self.role_listbox.insert(tk.END, new_role)
    
    def remove_role(self):
        selected_role = self.role_listbox.get(tk.ACTIVE)
        if selected_role in self.user_roles:
            del self.user_roles[selected_role]
            self.role_listbox.delete(tk.ACTIVE)
    
    def save_roles(self):
        for role in self.user_roles:
            permissions = self.permissions_text.get("1.0", tk.END).strip().split(",")
            self.user_roles[role] = permissions
        self.log_message("User roles and permissions saved.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationInterface(root)
    root.mainloop()