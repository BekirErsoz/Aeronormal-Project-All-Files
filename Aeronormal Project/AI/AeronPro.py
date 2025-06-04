import tkinter as tk
from tkinter import messagebox
from tkinter import Canvas
import numpy as np
from scipy.spatial import distance

class AeronProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AeronPro - Otonom Görev Planlama")
        self.root.geometry("800x600")
        self.root.configure(bg="#282c34")
        
        self.canvas = Canvas(self.root, bg="white", height=400, width=600)
        self.canvas.pack(pady=20)
        
        self.start_point = None
        self.end_point = None
        self.waypoints = []

        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Görev Planlama Arayüzü", font=("Arial", 20), bg="#282c34", fg="white")
        self.label.pack(pady=10)

        self.instructions = tk.Label(self.root, text="Başlangıç ve bitiş noktalarını seçmek için haritaya tıklayın.", font=("Arial", 14), bg="#282c34", fg="white")
        self.instructions.pack()

        self.plan_button = tk.Button(self.root, text="Görevi Planla", font=("Arial", 14), bg="#61afef", fg="white", command=self.plan_mission)
        self.plan_button.pack(pady=10)

        self.reset_button = tk.Button(self.root, text="Sıfırla", font=("Arial", 14), bg="#e06c75", fg="white", command=self.reset)
        self.reset_button.pack(pady=10)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        if not self.start_point:
            self.start_point = (x, y)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="green", outline="green")
        elif not self.end_point:
            self.end_point = (x, y)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red", outline="red")
        else:
            self.waypoints.append((x, y))
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="blue", outline="blue")

    def plan_mission(self):
        if not self.start_point or not self.end_point:
            messagebox.showwarning("Uyarı", "Lütfen başlangıç ve bitiş noktalarını seçin.")
            return

        # Optimal rota hesaplama (Yapay Zeka kullanarak)
        all_points = [self.start_point] + self.waypoints + [self.end_point]
        optimal_route = self.optimize_route(all_points)

        for i in range(len(optimal_route) - 1):
            point1 = optimal_route[i]
            point2 = optimal_route[i+1]
            self.canvas.create_line(point1[0], point1[1], point2[0], point2[1], fill="yellow", width=2)

        messagebox.showinfo("Başarılı", "Görev başarıyla planlandı!")

    def reset(self):
        self.start_point = None
        self.end_point = None
        self.waypoints = []
        self.canvas.delete("all")

    def optimize_route(self, points):
        # Yapay Zeka ile optimal rota hesaplama
        points = np.array(points)
        dist_matrix = distance.cdist(points, points, 'euclidean')

        num_points = len(points)
        min_route = None
        min_distance = float('inf')

        def find_shortest_path(route, remaining_points):
            nonlocal min_route, min_distance
            if not remaining_points:
                current_distance = sum(dist_matrix[route[i], route[i+1]] for i in range(len(route) - 1))
                if current_distance < min_distance:
                    min_distance = current_distance
                    min_route = route
            else:
                for i in range(len(remaining_points)):
                    new_route = route + [remaining_points[i]]
                    new_remaining = remaining_points[:i] + remaining_points[i+1:]
                    find_shortest_path(new_route, new_remaining)

        find_shortest_path([0], list(range(1, num_points)))

        optimal_route = [points[i] for i in min_route]
        return optimal_route


if __name__ == "__main__":
    root = tk.Tk()
    app = AeronProApp(root)
    root.mainloop()