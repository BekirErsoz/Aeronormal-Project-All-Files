import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

class Radar:
    def __init__(self, range_max):
        self.range_max = range_max
    
    def get_distance(self):
        # Simulating distance measurement with random noise
        return random.uniform(0, self.range_max)

class Drone:
    def __init__(self, radar, path):
        self.radar = radar
        self.path = path
        self.position_index = 0
        self.positions = self.generate_positions()

    def generate_positions(self):
        # Generate drone positions along the path
        positions = []
        for t in np.linspace(0, 2 * np.pi, 100):
            x = self.path[0] + 10 * np.cos(t)
            y = self.path[1] + 10 * np.sin(t)
            positions.append((x, y))
        return positions
    
    def get_current_position(self):
        position = self.positions[self.position_index]
        self.position_index = (self.position_index + 1) % len(self.positions)
        return position
    
    def collect_radar_data(self, num_measurements):
        distances = []
        for _ in range(num_measurements):
            distance = self.radar.get_distance()
            distances.append(distance)
        return distances

    def analyze_data(self, data):
        avg_distance = np.mean(data)
        max_distance = np.max(data)
        min_distance = np.min(data)
        return avg_distance, max_distance, min_distance

    def simulate(self, num_measurements):
        data = self.collect_radar_data(num_measurements)
        avg_distance, max_distance, min_distance = self.analyze_data(data)
        self.plot_simulation(data, avg_distance)
        print(f"Average Distance: {avg_distance:.2f} meters")
        print(f"Maximum Distance: {max_distance:.2f} meters")
        print(f"Minimum Distance: {min_distance:.2f} meters")

    def plot_simulation(self, data, avg_distance):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data, label="Distance Measurements")
        ax.axhline(y=avg_distance, color='r', linestyle='--', label="Average Distance")
        ax.set_xlabel("Measurement Index")
        ax.set_ylabel("Distance (meters)")
        ax.set_title("Radar Distance Measurements")
        ax.legend()

        drone_path_x = [pos[0] for pos in self.positions]
        drone_path_y = [pos[1] for pos in self.positions]

        fig, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(drone_path_x, drone_path_y, label="Drone Path", linestyle='--')
        drone_dot, = ax2.plot([], [], 'bo', label="Drone Position")
        ax2.set_xlim(min(drone_path_x)-5, max(drone_path_x)+5)
        ax2.set_ylim(min(drone_path_y)-5, max(drone_path_y)+5)
        ax2.set_title("Drone Path Simulation")
        ax2.legend()

        def update(frame):
            current_position = self.get_current_position()
            drone_dot.set_data(current_position[0], current_position[1])
            return drone_dot,

        ani = FuncAnimation(fig, update, frames=len(self.positions), interval=100, blit=True)

        plt.show()

# Radar range is set to 100 meters
radar = Radar(range_max=100)
# Drone path center
path_center = (0, 0)
drone = Drone(radar=radar, path=path_center)

# Simulate 50 radar measurements
drone.simulate(num_measurements=50)