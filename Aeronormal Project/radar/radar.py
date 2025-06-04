import numpy as np
import matplotlib.pyplot as plt
import random
import time

class Radar:
    def __init__(self, range_max):
        self.range_max = range_max
    
    def get_distance(self):
        # Simulating distance measurement with random values
        return random.uniform(0, self.range_max)

class Drone:
    def __init__(self, radar):
        self.radar = radar
    
    def collect_radar_data(self, num_measurements):
        distances = []
        for _ in range(num_measurements):
            distance = self.radar.get_distance()
            distances.append(distance)
            time.sleep(0.1)  # Simulate time delay between measurements
        return distances
    
    def analyze_data(self, data):
        avg_distance = np.mean(data)
        max_distance = np.max(data)
        min_distance = np.min(data)
        return avg_distance, max_distance, min_distance
    
    def plot_data(self, data):
        plt.figure(figsize=(10, 6))
        plt.plot(data, label="Distance Measurements")
        plt.axhline(y=np.mean(data), color='r', linestyle='--', label="Average Distance")
        plt.xlabel("Measurement Index")
        plt.ylabel("Distance (meters)")
        plt.title("Radar Distance Measurements")
        plt.legend()
        plt.show()

# Radar range is set to 100 meters
radar = Radar(range_max=100)
drone = Drone(radar=radar)

# Collecting 50 radar measurements
data = drone.collect_radar_data(num_measurements=50)

# Analyzing the collected data
avg_distance, max_distance, min_distance = drone.analyze_data(data)
print(f"Average Distance: {avg_distance:.2f} meters")
print(f"Maximum Distance: {max_distance:.2f} meters")
print(f"Minimum Distance: {min_distance:.2f} meters")

# Plotting the data
drone.plot_data(data)