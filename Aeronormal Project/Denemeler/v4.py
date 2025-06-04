import tkinter as tk
from tkinter import messagebox
import random

class DroneSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Engelden Kaçınma ve Güvenlik Simülasyonu")
        self.root.geometry("800x850")

        self.canvas = tk.Canvas(self.root, width=800, height=800, bg="lightgray")
        self.canvas.pack()

        self.grid_size = 20
        self.cell_size = 40
        self.drone_pos = [10, 10]
        self.obstacles = self.generate_obstacles(30)

        self.create_grid()
        self.draw_drone()
        self.draw_obstacles()

        self.root.bind("<KeyPress>", self.on_key_press)

        self.status_label = tk.Label(self.root, text="Drone Durumu: Bekliyor", font=("Arial", 14), bg="light yellow")
        self.status_label.pack(fill=tk.BOTH, pady=10)

    def create_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.canvas.create_rectangle(i*self.cell_size, j*self.cell_size, 
                                             (i+1)*self.cell_size, (j+1)*self.cell_size, 
                                             outline="white", width=2)

    def draw_drone(self):
        self.drone = self.canvas.create_rectangle(self.drone_pos[0]*self.cell_size, 
                                                  self.drone_pos[1]*self.cell_size, 
                                                  (self.drone_pos[0]+1)*self.cell_size, 
                                                  (self.drone_pos[1]+1)*self.cell_size, 
                                                  fill="blue")

    def draw_obstacles(self):
        for pos in self.obstacles:
            self.canvas.create_rectangle(pos[0]*self.cell_size, pos[1]*self.cell_size, 
                                         (pos[0]+1)*self.cell_size, (pos[1]+1)*self.cell_size,
                                         fill="red")

    def generate_obstacles(self, num_obstacles):
        obstacles = []
        for _ in range(num_obstacles):
            while True:
                x = random.randint(0, self.grid_size - 1)
                y = random.randint(0, self.grid_size - 1)
                if [x, y] != self.drone_pos and [x, y] not in obstacles:
                    obstacles.append([x, y])
                    break
        return obstacles

    def on_key_press(self, event):
        direction = event.keysym
        new_pos = self.drone_pos[:]

        if direction == "Up":
            new_pos[1] -= 1
        elif direction == "Down":
            new_pos[1] += 1
        elif direction == "Left":
            new_pos[0] -= 1
        elif direction == "Right":
            new_pos[0] += 1

        if self.is_valid_move(new_pos):
            self.move_drone(new_pos)
            self.update_status("Drone hareket ediyor...", "green")
        else:
            self.update_status("Engel algılandı! Hareket durduruldu.", "red")

    def is_valid_move(self, pos):
        if pos[0] < 0 or pos[0] >= self.grid_size or pos[1] < 0 or pos[1] >= self.grid_size:
            return False
        if pos in self.obstacles:
            return False
        return True

    def move_drone(self, new_pos):
        self.drone_pos = new_pos
        self.canvas.coords(self.drone, self.drone_pos[0]*self.cell_size, 
                           self.drone_pos[1]*self.cell_size, 
                           (self.drone_pos[0]+1)*self.cell_size, 
                           (self.drone_pos[1]+1)*self.cell_size)

    def update_status(self, message, color):
        self.status_label.config(text=f"Drone Durumu: {message}", bg=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneSimulationApp(root)
    root.mainloop()