import numpy as np
import os

def generate_fake_lidar():
    
    num_points = 1000
    points = np.random.rand(num_points, 3)  # 1000 adet 3D nokta (x, y, z)

    
    output_dir = os.path.join(os.path.dirname(__file__), "../data/pointcloud")
    os.makedirs(output_dir, exist_ok=True)
    np.savetxt(os.path.join(output_dir, "pointcloud.txt"), points)
    print("Sahte Lidar verisi oluşturuldu ve kaydedildi.")

if __name__ == "__main__":
    generate_fake_lidar()